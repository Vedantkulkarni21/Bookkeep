import os
import tempfile
import time
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.db import get_db
import app.crud as crud
from app.routers.auth import get_current_user_real
from app.utils.emailer import send_email


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", None)

OAUTH_TOKEN_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "oauth_token.json")
)


# ---------------- GOOGLE DRIVE CLIENT ---------------- #
def get_drive_service():
    env_path = os.getenv("GOOGLE_OAUTH_TOKEN_PATH")
    base = os.path.dirname(__file__)

    candidates = [
        env_path,
        os.path.join(base, "../../../../oauth_token.json"),
        os.path.join(base, "../../../oauth_token.json"),
        os.path.join(os.getcwd(), "oauth_token.json"),
        OAUTH_TOKEN_FILE,
    ]

    candidates = [p for p in candidates if p]
    logger.info(f"[upload] token lookup candidates: {candidates}")

    token_path = next((p for p in candidates if os.path.exists(p)), None)

    if not token_path:
        raise HTTPException(
            status_code=400,
            detail="OAuth token file not found. Specify GOOGLE_OAUTH_TOKEN_PATH or place oauth_token.json in project.",
        )

    logger.info(f"[upload] Using OAuth token file: {token_path}")

    try:
        creds = OAuth2Credentials.from_authorized_user_file(
            token_path, scopes=SCOPES
        )
        return build("drive", "v3", credentials=creds)

    except Exception as e:
        logger.exception("Failed to initialize Google Drive client")
        raise HTTPException(status_code=500, detail=f"Google Drive init failed: {e}")


# ---------------- COMMON UPLOAD HANDLER ---------------- #
async def _upload_to_drive(file: UploadFile, user_id: int, db: Session):
    service = get_drive_service()

    temp_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "temp")
    )
    os.makedirs(temp_dir, exist_ok=True)

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            dir=temp_dir,
            delete=False,
            suffix=os.path.splitext(file.filename)[1],
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        file_meta = {"name": file.filename}
        if DRIVE_FOLDER_ID:
            file_meta["parents"] = [DRIVE_FOLDER_ID]

        media = MediaFileUpload(tmp_path, mimetype=file.content_type)

        drive_file = (
            service.files()
            .create(body=file_meta, media_body=media, fields="id")
            .execute()
        )

        drive_id = drive_file.get("id")

        crud.create_uploaded_file(
            db=db,
            filename=file.filename,
            drive_file_id=drive_id,
            content_type=file.content_type,
            owner_id=user_id,
        )

        return drive_id

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                time.sleep(0.1)
                os.remove(tmp_path)
            except Exception:
                logger.warning("Temp cleanup failed")


# ---------------- PERSONAL DOCUMENT UPLOAD ---------------- #
@router.post("/personal-document")
async def upload_personal_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    try:
        drive_id = await _upload_to_drive(file, current_user.id, db)
        admin_email = os.getenv("ADMIN_EMAIL")

        # Email to user
        await send_email(
            to=current_user.email,
            subject="New Personal Document Uploaded — BookKeepro",
            body=f"""
            <p>Dear Sir/Ma’am,</p>

            <p>
            We have successfully received your personal document:
            </p>

            <p><strong>{file.filename}</strong></p>

            <p>
            Our team will review the document and update you on the next steps shortly.
            </p>

            <p>
            If any additional information is required, we will contact you promptly.
            </p>

            <p style="margin-top:20px;">
            Kind regards,<br>
            <strong>The BookKeepro Team</strong>
            </p>
            """,
        )

        # Email to admin
        if admin_email:
            await send_email(
                to=admin_email,
                subject="New Personal Document Uploaded — BookKeepro",
                body=f"""
                <p>Dear Team,</p>
                
                <p>the <strong>User:</strong> {current_user.email} has uploaded a personal document-</p>
                <p><strong>File Uploaded:</strong> {file.filename}</p>

                <p>
                Kindly review the document and proceed with the next steps as applicable.
                </p>

                <p>
                Thank you,<br>
                <strong>BookKeepro Support Team</strong>
                </p>
                """,
            )

        return {"file_id": drive_id, "filename": file.filename}

    except Exception as e:
        logger.exception("Personal upload error")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- DELETE PERSONAL DOCUMENT ---------------- #
@router.delete("/personal-document/{file_id}")
async def delete_personal_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()

        crud.delete_uploaded_file(
            db=db,
            drive_file_id=file_id,
            owner_id=current_user.id,
        )

        return {"deleted": True}

    except Exception as e:
        logger.exception("Delete personal doc failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- BUSINESS DOCUMENT UPLOAD ---------------- #
@router.post("/business-document")
async def upload_business_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    try:
        drive_id = await _upload_to_drive(file, current_user.id, db)
        admin_email = os.getenv("ADMIN_EMAIL")

        # Email to user
        await send_email(
            to=current_user.email,
            subject="Business Document Uploaded — BookKeepro",
            body=f"""
            <p>Dear Sir/Ma’am,</p>

            <p>
            We have successfully received your business document:
            </p>

            <p><strong>{file.filename}</strong></p>

            <p>
            Our review team will verify the document and update you shortly.
            </p>

            <p>
            Kind regards,<br>
            <strong>BookKeepro Team</strong>
            </p>
            """,
        )

        # Email to admin
        if admin_email:
            await send_email(
                to=admin_email,
                subject="New Business Document Uploaded — BookKeepro",
                body=f"""
                <p>Dear Team,</p>

                <p>the <strong>User:</strong> {current_user.email} has uploaded a Business document-</p>
                <p><strong>File Uploaded:</strong> {file.filename}</p>
                
                <p>
                Kindly review the document and proceed with the next steps as applicable.
                </p>

                <p>
                Thank you,<br>
                <strong>BookKeepro Support Team</strong>
                </p>
                """,
            )

        return {"file_id": drive_id, "filename": file.filename}

    except Exception as e:
        logger.exception("Business upload error")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- DELETE BUSINESS DOCUMENT ---------------- #
@router.delete("/business-document/{file_id}")
async def delete_business_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()

        crud.delete_uploaded_file(
            db=db,
            drive_file_id=file_id,
            owner_id=current_user.id,
        )

        return {"deleted": True}

    except Exception as e:
        logger.exception("Delete business doc failed")
        raise HTTPException(status_code=500, detail=str(e))
