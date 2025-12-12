from app.crud import create_user
from app.db import SessionLocal

db = SessionLocal()
admin_user = create_user(
    db,
    name="Admin1",
    email="admin1@gmail.com",
    phone="99299922",
    password="pass",
    role="admin"
)
print(f"Admin created: {admin_user.email} with role {admin_user.role}")