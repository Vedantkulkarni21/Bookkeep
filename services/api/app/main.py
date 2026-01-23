import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app import models
from app.db import engine


log = logging.getLogger("uvicorn.error")

# create app early so mounts can reference it
app = FastAPI(title="BookKeepPro API")

# create database tables
models.Base.metadata.create_all(bind=engine)

# include routers from app.routers (they should expose `router`)
try:
    from app.routers import auth, upload  # type: ignore
    try:
        app.include_router(auth.router)
    except Exception as exc:
        log.exception("Failed to include auth.router: %s", exc)

    try:
        app.include_router(upload.router)
    except Exception as exc:
        log.exception("Failed to include upload.router: %s", exc)
except Exception as exc:
    log.exception("Failed to import routers package: %s", exc)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend directory (project-root/frontend)
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend"))

def mount_if_exists(route: str, subdir: str, name: str):
    path = os.path.join(FRONTEND_DIR, subdir)
    if os.path.isdir(path):
        app.mount(route, StaticFiles(directory=path), name=name)
        log.info("Mounted static %s -> %s", route, path)
    else:
        log.debug("Static directory not found, skipping mount: %s", path)

# mount common static folders only when present
mount_if_exists("/js", "js", "js")
mount_if_exists("/images", "images", "images")
mount_if_exists("/css", "css", "css")


def serve_frontend_file(filename: str):
    full = os.path.join(FRONTEND_DIR, filename)
    if os.path.isfile(full):
        return FileResponse(full)
    log.warning("Frontend file not found: %s", full)
    raise HTTPException(status_code=404, detail="Page not found")

# simple frontend routes (safe if frontend folder or files missing)
@app.get("/", tags=["frontend"])
def home():
    return serve_frontend_file("home.html")

@app.get("/home", tags=["frontend"])
def home_page():
    return serve_frontend_file("home.html")

@app.get("/login", tags=["frontend"])
def login_page():
    return serve_frontend_file("login.html")

@app.get("/signup", tags=["frontend"])
def signup_page():
    return serve_frontend_file("signup.html")

@app.get("/dashboard", tags=["frontend"])
def dashboard_page():
    return serve_frontend_file("dashboard.html")

@app.get("/admin-dashboard", tags=["frontend"])
def admin_dashboard_page():
    return serve_frontend_file("admin-dashboard.html")

@app.get("/admin-user-detail", tags=["frontend"])
def admin_user_detail():
    return serve_frontend_file("admin-user-detail.html")


@app.get("/upload-personal", tags=["frontend"])
def upload_personal():
    return serve_frontend_file("upload-personal.html")

@app.get("/upload-business", tags=["frontend"])
def upload_business():
    return serve_frontend_file("upload-business.html")

@app.get("/contact", tags=["frontend"])
def contact_page():
    return serve_frontend_file("contact.html")

@app.get("/services", tags=["frontend"])
def services_page():
    return serve_frontend_file("services.html")

@app.get("/about-us", tags=["frontend"])
def about_us_page():
    return serve_frontend_file("about-us.html")

@app.get("/admin-login", tags=["frontend"])
def admin_login_page():
    return serve_frontend_file("admin-login.html")
    
@app.post("/logout")
def logout():
    # JWT is stateless → nothing to invalidate server-side
    return {"message": "Logged out"}




from app.routers import upload
app.include_router(upload.router)


from app.routers import contact
app.include_router(contact.router)

from app.routers import review
app.include_router(review.router)


from app.utils.emailer import send_email

@app.get("/test-email", tags=["email"])
async def test_email():
    await send_email(
        to="info@bookkeepro.net",
        subject="BookKeepro SMTP Test",
        body="<p>Email sending is working ✔️</p>"
    )
    return {"status": "sent"}



@app.get("/auth/google/callback")
def google_callback(code: str = None):
    return "OAuth successful. You can close this tab."

@app.get("/forgot-password", tags=["frontend"])
def forgot_password_page():
    return serve_frontend_file("forgot-password.html")

@app.get("/reset-password", tags=["frontend"])
def reset_password_page():
    return serve_frontend_file("reset-password.html")