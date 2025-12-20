import os
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db import get_db
import app.crud as crud
from app.schemas import SignupRequest, LoginRequest, TokenResponse


# =========================
# Router
# =========================
router = APIRouter(prefix="/api/auth", tags=["auth"])


# =========================
# Config
# =========================
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# =========================
# JWT helpers
# =========================
def create_access_token(
    subject: str,
    role: str = "user",
    expires_minutes: int | None = None,
) -> str:
    expire = datetime.utcnow() + timedelta(
        minutes=expires_minutes or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "role": role.lower(),
        "exp": expire,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        jwt_role: str = (payload.get("role") or "").lower()

        if not email:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email)
    if not user:
        raise credentials_exception

    # attach role from token (important for admin check)
    setattr(user, "jwt_role", jwt_role)
    return user


# =========================
# Auth Routes
# =========================
@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    role_value = getattr(payload, "role", None) or "user"

    user = crud.create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        phone=payload.phone or "",
        password=payload.password,
        role=role_value,
    )

    user_role = (
        user.role.value if hasattr(user.role, "value") else str(user.role)
    ).lower()

    token = create_access_token(subject=user.email, role=user_role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user_role,
        "user_id": user.id,
    }


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, payload.email)

    verified = False
    if user:
        if hasattr(crud, "verify_password"):
            verified = crud.verify_password(
                payload.password, user.hashed_password
            )
        else:
            verified = pwd_context.verify(
                payload.password, user.hashed_password
            )

    if not user or not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    user_role = (
        user.role.value if hasattr(user.role, "value") else str(user.role)
    ).lower()

    requested_role = (getattr(payload, "role", None) or "user").lower()

    # enforce admin login strictly
    if requested_role == "admin" and user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized as admin",
        )

    token = create_access_token(subject=user.email, role=user_role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user_role,
        "user_id": user.id,
    }


@router.get("/me")
def me(current_user=Depends(get_current_user)):
    role = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else str(current_user.role)
    )

    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": role,
    }


# =========================
# Admin Routes
# =========================
@router.get("/admin/users")
def list_users_for_admin(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if getattr(current_user, "jwt_role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    users = crud.get_all_users(db)
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "role": u.role.value if hasattr(u.role, "value") else str(u.role),
        }
        for u in users
    ]


@router.get("/admin/users/{user_id}/documents")
def get_user_documents(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if getattr(current_user, "jwt_role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    from app import models

    documents = (
        db.query(models.UploadedFile)
        .filter(models.UploadedFile.owner_id == user_id)
        .all()
    )

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        },
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "content_type": d.content_type,
                "uploaded_at": d.uploaded_at.isoformat()
                if d.uploaded_at
                else None,
                "drive_file_id": d.drive_file_id,
            }
            for d in documents
        ],
    }
