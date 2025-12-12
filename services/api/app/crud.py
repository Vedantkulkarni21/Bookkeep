from sqlalchemy.orm import Session
from app.models import User, UploadedFile
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, phone: str, password: str, role: str = "user"):
    hashed = pwd_context.hash(password)
    user = User(name=name, email=email, phone=phone, hashed_password=hashed, role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_uploaded_file(db: Session, filename: str, drive_file_id: str, content_type: str, owner_id: int):
    uf = UploadedFile(filename=filename, drive_file_id=drive_file_id, content_type=content_type, owner_id=owner_id)
    db.add(uf)
    db.commit()
    db.refresh(uf)
    return uf

def delete_uploaded_file(db: Session, drive_file_id: str, owner_id: int):
    q = db.query(UploadedFile).filter(UploadedFile.drive_file_id == drive_file_id, UploadedFile.owner_id == owner_id)
    obj = q.first()
    if obj:
        q.delete()
        db.commit()
        return True
    return False

# ...existing code...
from sqlalchemy.orm import Session
from app.models import User
# ...existing code...

def get_all_users(db: Session):
    return db.query(User).all()

# ...existing code...