from app.crud import create_user
from app.db import SessionLocal


db = SessionLocal()
admin_user = create_user(
    db,
    name="NAME",
    email="MAIL@gmail.com",
    phone="99",
    password="pass",
    role="admin"
)
print(f"Admin created: {admin_user.email} with role {admin_user.role}")
