
# ...existing code...
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.db import Base
import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
    Enum,
    UniqueConstraint,
)


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
    filename = Column(String(512), nullable=False)
    drive_file_id = Column(String(200), nullable=False)
    content_type = Column(String(100))
    doc_type = Column(String(150))   # 🔥 ADD THIS
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="uploads")


class AdminDocument(Base):
    __tablename__ = "admin_documents"

    id = Column(Integer, primary_key=True, index=True)

    # flexible & future-proof
    doc_key = Column(String(100), nullable=False, index=True)
    doc_label = Column(String(150), nullable=False)

    filename = Column(String(512), nullable=False)
    drive_file_id = Column(String(200), nullable=False)
    content_type = Column(String(100))

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    admin = relationship("User")

    __table_args__ = (
        UniqueConstraint("doc_key", name="uq_admin_doc_key"),
    )


# class PersonalDocument(Base):
#     __tablename__ = "personal_documents"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

#     filename = Column(String(512), nullable=False)
#     drive_file_id = Column(String(200), nullable=False)
#     content_type = Column(String(100))

#     uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

#     user = relationship("User")

class PersonalDocument(Base):
    __tablename__ = "personal_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    doc_type = Column(String(200), nullable=False)  # ✅ ADD THIS

    filename = Column(String(512), nullable=False)
    drive_file_id = Column(String(200), nullable=False)
    content_type = Column(String(100))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())



class BusinessDocument(Base):
    __tablename__ = "business_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    business_type = Column(String(100))  # optional
    filename = Column(String(512), nullable=False)
    drive_file_id = Column(String(200), nullable=False)
    content_type = Column(String(100))

    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
