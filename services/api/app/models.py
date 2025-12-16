
# ...existing code...
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.db import Base
import enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150))
    email = Column(String(200), unique=True, index=True, nullable=False)
    phone = Column(String(50), default="")
    hashed_password = Column(String(300), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    uploads = relationship("UploadedFile", back_populates="owner")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(512))
    drive_file_id = Column(String(200))
    content_type = Column(String(100))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="uploads")
# ...existing code...