import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import auth, upload
from app.db import engine
from app import models

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookKeepPro API")

# Include routers (only once)
app.include_router(auth.router)
app.include_router(upload.router)

# CORS - allow all for local/dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FRONTEND_DIR relative to this file:
# this file: myapp/services/api/app/main.py
# we want: myapp/frontend => go up 3 levels then "frontend"
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend")
)

# Ensure folder exists (helpful for debugging)
if not os.path.isdir(FRONTEND_DIR):
    raise RuntimeError(f"Frontend directory not found at: {FRONTEND_DIR}")

# Serve static files from root endpoints:
app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/images", StaticFiles(directory=os.path.join(FRONTEND_DIR, "images")), name="images")

# HTML routes (serve files from frontend folder)
@app.get("/", tags=["frontend"])
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "home.html"))

@app.get("/home", tags=["frontend"])
def home_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "home.html"))

@app.get("/login", tags=["frontend"])
def login_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/signup", tags=["frontend"])
def signup_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "signup.html"))

@app.get("/dashboard", tags=["frontend"])
def dashboard_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "dashboard.html"))

@app.get("/upload/business", tags=["frontend"])
def upload_business_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "upload_business.html"))
