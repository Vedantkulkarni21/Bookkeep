# ...existing code...
import os
import tempfile
import time
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from sqlalchemy.orm import Session

from app.db import get_db
import app.crud as crud
from app.routers.auth import get_current_user_real

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["upload"])

SCOPES = ['https://www.googleapis.com/auth/drive']
# oauth token should be at myapp/oauth_token.json (kept for backward-compat)
OAUTH_TOKEN_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "oauth_token.json"))
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", None)  # set in .env if you have one

def get_drive_service():
    """
    Look for oauth_token.json in several sensible locations:
      1) Path from GOOGLE_OAUTH_TOKEN_PATH env var (if set)
      2) Project root: myapp/oauth_token.json
      3) Services folder: myapp/services/oauth_token.json (legacy/default)
      4) Current working directory: ./oauth_token.json

    Logs the candidates and uses the first match. Raises HTTPException(400) if not found.
    """
    env_path = os.getenv("GOOGLE_OAUTH_TOKEN_PATH")
    base = os.path.dirname(__file__)
    candidates = []
    if env_path:
        candidates.append(os.path.normpath(env_path))
    # project root (myapp/oauth_token.json)
    candidates.append(os.path.normpath(os.path.join(base, "../../../../oauth_token.json")))
    # services folder (myapp/services/oauth_token.json) — previous default
    candidates.append(os.path.normpath(os.path.join(base, "../../../oauth_token.json")))
    # cwd
    candidates.append(os.path.normpath(os.path.join(os.getcwd(), "oauth_token.json")))
    # explicit constant fallback (keeps old behaviour)
    candidates.append(os.path.normpath(OAUTH_TOKEN_FILE))

    log = logging.getLogger("uvicorn.error")
    log.info(f"[upload] token lookup candidates: {candidates}")

    token_path = None
    for p in candidates:
        try:
            if p and os.path.exists(p):
                token_path = p
                break
        except Exception:
            continue

    if not token_path:
        # include tried paths in message to make debugging easy
        raise HTTPException(status_code=400, detail=(
            "OAuth token file not found. Tried paths: " + ", ".join(candidates) +
            ". Put oauth_token.json in one of these locations or set GOOGLE_OAUTH_TOKEN_PATH."
        ))

    log.info(f"[upload] using oauth token at: {os.path.abspath(token_path)}")

    try:
        creds = OAuth2Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        log.exception("Failed to build Drive service from token")
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Drive client: {e}")

@router.post("/business-document")
async def upload_business_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_real)
):
    tmp_path = None
    try:
        service = get_drive_service()

        # temporary dir in project root /temp
        temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "temp"))
        os.makedirs(temp_dir, exist_ok=True)

        with tempfile.NamedTemporaryFile(dir=temp_dir, delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        file_metadata = {'name': file.filename}
        if DRIVE_FOLDER_ID:
            file_metadata['parents'] = [DRIVE_FOLDER_ID]

        media = MediaFileUpload(tmp_path, mimetype=file.content_type)
        drive_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        drive_id = drive_file.get('id')

        # store metadata
        try:
            crud.create_uploaded_file(db, filename=file.filename, drive_file_id=drive_id, content_type=file.content_type, owner_id=current_user.id)
        except Exception:
            logger.exception("Failed to write uploaded file metadata")

        return {"file_id": drive_id, "filename": file.filename}
    except HTTPException:
        # re-raise HTTPExceptions so the correct status code passes through
        raise
    except Exception as e:
        logger.exception("Upload error")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                time.sleep(0.1)
                os.remove(tmp_path)
            except Exception:
                logger.warning("Temp cleanup failed")

@router.delete("/business-document/{file_id}")
async def delete_business_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user_real)
):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()
        deleted = crud.delete_uploaded_file(db, drive_file_id=file_id, owner_id=current_user.id)
        return {"deleted": bool(deleted)}
    except Exception as e:
        logger.exception("Delete error")
        raise HTTPException(status_code=500, detail=str(e))
