from app.crud import create_user
from app.db import SessionLocal


db = SessionLocal()
admin_user = create_user(
    db,
    name="sachink",
    email="sachink.aiindia@gmail.com",
    phone="99",
    password="pass",
    role="admin"
)
print(f"Admin created: {admin_user.email} with role {admin_user.role}")