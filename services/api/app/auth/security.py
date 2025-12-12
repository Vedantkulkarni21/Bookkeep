
# from datetime import datetime, timedelta
# import jwt
# from jwt.exceptions import InvalidTokenError
# from fastapi import Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.db import get_db
# from app.models import User

# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# auth_scheme = HTTPBearer()


# SECRET_KEY = "supersecret123456789"  # put any long fixed string
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60




# def verify_password(plain_password, hashed_password):
#     from passlib.context import CryptContext
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     return pwd_context.verify(plain_password, hashed_password)


# def hash_password(password: str):
#     from passlib.context import CryptContext
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     return pwd_context.hash(password)


# def create_access_token(data: dict, expires_minutes=60):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)



# from jwt.exceptions import InvalidTokenError

# def get_current_user(
#     credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
#     db: Session = Depends(get_db)
# ):
#     token = credentials.credentials  # This is the JWT token

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("id")

#         if not user_id:
#             raise HTTPException(status_code=401, detail="Invalid token")

#         user = db.query(User).filter(User.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=401, detail="User not found")

#         return user

#     except InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")





import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db import get_db
from app.crud import get_user_by_email
from pydantic import BaseModel

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class TokenData(BaseModel):
    email: str | None = None

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user