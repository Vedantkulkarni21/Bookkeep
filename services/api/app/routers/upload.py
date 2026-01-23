
# import os
# import tempfile
# import time
# import logging
# from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
# from sqlalchemy.orm import Session
# from google.oauth2.credentials import Credentials as OAuth2Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# from app.db import get_db
# import app.crud as crud
# from app.routers.auth import get_current_user_real
# from app.utils.emailer import send_email

# logger = logging.getLogger(__name__)

# router = APIRouter(prefix="/api/upload", tags=["upload"])

# SCOPES = ["https://www.googleapis.com/auth/drive"]
# DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

# OAUTH_TOKEN_FILE = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), "..", "..", "..", "oauth_token.json")
# )

# # ---------------- GOOGLE DRIVE CLIENT ---------------- #
# def get_drive_service():
#     env_path = os.getenv("GOOGLE_OAUTH_TOKEN_PATH")
#     base = os.path.dirname(__file__)

#     candidates = [
#         env_path,
#         os.path.join(base, "../../../../oauth_token.json"),
#         os.path.join(base, "../../../oauth_token.json"),
#         os.path.join(os.getcwd(), "oauth_token.json"),
#         OAUTH_TOKEN_FILE,
#     ]

#     candidates = [p for p in candidates if p]
#     token_path = next((p for p in candidates if os.path.exists(p)), None)

#     if not token_path:
#         raise HTTPException(
#             status_code=400,
#             detail="OAuth token file not found. Specify GOOGLE_OAUTH_TOKEN_PATH or place oauth_token.json in project.",
#         )

#     try:
#         creds = OAuth2Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
#         return build("drive", "v3", credentials=creds)
#     except Exception as e:
#         logger.exception("Drive init failed")
#         raise HTTPException(status_code=500, detail=str(e))


# # ---------------- COMMON UPLOAD HANDLER ---------------- #
# async def _upload_to_drive(file: UploadFile, user_id: int, doc_type: str, db: Session):
#     service = get_drive_service()

#     temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "temp"))
#     os.makedirs(temp_dir, exist_ok=True)

#     tmp_path = None

#     try:
#         with tempfile.NamedTemporaryFile(
#             dir=temp_dir, delete=False, suffix=os.path.splitext(file.filename)[1]
#         ) as tmp:
#             tmp.write(await file.read())
#             tmp_path = tmp.name

#         file_meta = {"name": file.filename}
#         if DRIVE_FOLDER_ID:
#             file_meta["parents"] = [DRIVE_FOLDER_ID]

#         media = MediaFileUpload(tmp_path, mimetype=file.content_type)

#         drive_file = service.files().create(
#             body=file_meta, media_body=media, fields="id"
#         ).execute()

#         drive_id = drive_file["id"]

#         # Save to DB WITH doc_type
#         crud.create_uploaded_file(
#             db=db,
#             filename=file.filename,
#             drive_file_id=drive_id,
#             content_type=file.content_type,
#             doc_type=doc_type,
#             owner_id=user_id,
#         )

#         return drive_id

#     finally:
#         if tmp_path and os.path.exists(tmp_path):
#             try:
#                 time.sleep(0.1)
#                 os.remove(tmp_path)
#             except Exception:
#                 logger.warning("Temp cleanup failed")


# # ---------------- PERSONAL DOCUMENT UPLOAD ---------------- #
# @router.post("/personal-document")
# async def upload_personal_document(
#     file: UploadFile = File(...),
#     doc_type: str = Form("Personal"),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     try:
#         drive_id = await _upload_to_drive(file, current_user.id, doc_type, db)
#         admin_email = os.getenv("ADMIN_EMAIL")

#         # await send_email(
#         #     to=current_user.email,
#         #     subject="New Personal Document Uploaded — BookKeepro",
#         #     body=f"<p>We have received your personal document:<br><b>{file.filename}</b></p>",
#         # )
#         await send_email(
#             to=current_user.email,
#             subject="New Personal Document Uploaded — BookKeepro",
#             body=f"""
#             <p>Dear Sir/Ma’am,</p>

#             <p>
#             We have successfully received your personal document:
#             </p>

#             <p><strong>{file.filename}</strong></p>

#             <p>
#             Our team will review the document and update you on the next steps shortly.
#             </p>

#             <p>
#             If any additional information is required, we will contact you promptly.
#             </p>

#             <p style="margin-top:20px;">
#             Kind regards,<br>
#             <strong>The BookKeepro Team</strong>
#             </p>
#             """,
#         )

#         if admin_email:
#             await send_email(
#                 to=admin_email,
#                 subject="New Personal Document Uploaded — BookKeepro",
#                 body=f"""
#                 <p>Dear Team,</p>
                
#                 <p>the <strong>User:</strong> {current_user.email} has uploaded a personal document-</p>
#                 <p><strong>File Uploaded:</strong> {file.filename}</p>

#                 <p>
#                 Kindly review the document and proceed with the next steps as applicable.
#                 </p>

#                 <p>
#                 Thank you,<br>
#                 <strong>BookKeepro Support Team</strong>
#                 </p>
#                 """,
#             )

#         return {"file_id": drive_id, "filename": file.filename}

#     except Exception as e:
#         logger.exception("Personal upload error")
#         raise HTTPException(status_code=500, detail=str(e))


# # ---------------- BUSINESS DOCUMENT UPLOAD ---------------- #
# @router.post("/business-document")
# async def upload_business_document(
#     file: UploadFile = File(...),
#     doc_type: str = Form(...),  # 🔥 REQUIRED
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     try:
#         drive_id = await _upload_to_drive(file, current_user.id, doc_type, db)
#         admin_email = os.getenv("ADMIN_EMAIL")

#         await send_email(
#             to=current_user.email,
#             subject="Business Document Uploaded — BookKeepro",
#             body=f"""
#             <p>Dear Sir/Ma’am,</p>

#             <p>
#             We have successfully received your business document:
#             </p>

#             <p><strong>{file.filename}</strong></p>

#             <p>
#             Our review team will verify the document and update you shortly.
#             </p>

#             <p>
#             Kind regards,<br>
#             <strong>BookKeepro Team</strong>
#             </p>
#             """,
#         )

#         if admin_email:
#             await send_email(
#                 to=admin_email,
#                 subject="New Business Document Uploaded — BookKeepro",
#                 body=f"""
#                 <p>Dear Team,</p>

#                 <p>the <strong>User:</strong> {current_user.email} has uploaded a Business document-</p>
#                 <p><strong>File Uploaded:</strong> {file.filename}</p>
                
#                 <p>
#                 Kindly review the document and proceed with the next steps as applicable.
#                 </p>

#                 <p>
#                 Thank you,<br>
#                 <strong>BookKeepro Support Team</strong>
#                 </p>
#                 """,
#             )

#         return {"file_id": drive_id, "filename": file.filename}

#     except Exception as e:
#         logger.exception("Business upload error")
#         raise HTTPException(status_code=500, detail=str(e))


# # ---------------- DELETE (shared) ---------------- #
# @router.delete("/business-document/{file_id}")
# @router.delete("/personal-document/{file_id}")
# async def delete_document(
#     file_id: str,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     try:
#         service = get_drive_service()
#         service.files().delete(fileId=file_id).execute()

#         crud.delete_uploaded_file(db, file_id, current_user.id)

#         return {"deleted": True}

#     except Exception as e:
#         logger.exception("Delete failed")
#         raise HTTPException(status_code=500, detail=str(e))


# # ---------------- LIST USER FILES ---------------- #
# @router.get("/my-documents")
# def my_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user_real)):
#     return db.query(crud.UploadedFile).filter_by(owner_id=current_user.id).all()


# @router.get("/engagement-letter/status")
# def engagement_letter_status(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     record = (
#         db.query(crud.UploadedFile)
#         .filter(
#             crud.UploadedFile.owner_id == current_user.id,
#             crud.UploadedFile.doc_type == "EngagementLetter"
#         )
#         .first()
#     )

#     if not record:
#         return {"uploaded": False}

#     return {
#         "uploaded": True,
#         "file_id": record.drive_file_id,
#         "filename": record.filename,
#     }








# # ---------------- ADMIN DOCUMENT UPLOAD ---------------- #
# @router.post("/admin-upload")
# async def admin_upload_document(
#     file: UploadFile = File(...),
#     doc_type: str = Form(...),
#     user_id: int = Form(...),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     # 🔐 Only admin allowed
#     if getattr(current_user, "jwt_role", None) != "admin":
#         raise HTTPException(status_code=403, detail="Admins only")

#     try:
#         # 🔁 important for FastAPI file streams
#         await file.seek(0)

#         # ⬆️ Upload FOR THE USER (not admin)
#         drive_id = await _upload_to_drive(
#             file=file,
#             user_id=user_id,      # 🔥 SAME USER ID
#             doc_type=doc_type,    # 🔥 "Document 01 / 02 / 03"
#             db=db,
#         )

#         return {
#             "drive_file_id": drive_id,
#             "filename": file.filename,
#             "user_id": user_id,
#             "doc_type": doc_type,
#         }

#     except Exception as e:
#         logger.exception("Admin upload failed")
#         raise HTTPException(status_code=500, detail=str(e))


# # ---------------- ADMIN DELETE DOCUMENT ---------------- #
# @router.delete("/admin-document/{file_id}")
# async def admin_delete_document(
#     file_id: str,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     if getattr(current_user, "jwt_role", None) != "admin":
#         raise HTTPException(status_code=403, detail="Admins only")

#     from app.models import UploadedFile

#     record = db.query(UploadedFile).filter(
#         UploadedFile.drive_file_id == file_id
#     ).first()

#     if not record:
#         raise HTTPException(status_code=404, detail="File not found")

#     service = get_drive_service()
#     service.files().delete(fileId=file_id).execute()

#     db.delete(record)
#     db.commit()

#     return {"deleted": True}















































import os
import tempfile
import time
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
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
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

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
    token_path = next((p for p in candidates if os.path.exists(p)), None)

    if not token_path:
        raise HTTPException(
            status_code=400,
            detail="OAuth token file not found. Specify GOOGLE_OAUTH_TOKEN_PATH or place oauth_token.json in project.",
        )

    try:
        creds = OAuth2Credentials.from_authorized_user_file(token_path, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)
    except Exception as e:
        logger.exception("Drive init failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- COMMON UPLOAD HANDLER ---------------- #
async def _upload_to_drive(file: UploadFile, user_id: int, doc_type: str, db: Session):
    service = get_drive_service()

    temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "temp"))
    os.makedirs(temp_dir, exist_ok=True)

    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            dir=temp_dir, delete=False, suffix=os.path.splitext(file.filename)[1]
        ) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        file_meta = {"name": file.filename}
        if DRIVE_FOLDER_ID:
            file_meta["parents"] = [DRIVE_FOLDER_ID]

        media = MediaFileUpload(tmp_path, mimetype=file.content_type)

        drive_file = service.files().create(
            body=file_meta, media_body=media, fields="id"
        ).execute()

        drive_id = drive_file["id"]

        # Save to DB WITH doc_type
        crud.create_uploaded_file(
            db=db,
            filename=file.filename,
            drive_file_id=drive_id,
            content_type=file.content_type,
            doc_type=doc_type,
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
    doc_type: str = Form("Personal"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    try:
        drive_id = await _upload_to_drive(file, current_user.id, doc_type, db)
        admin_email = os.getenv("ADMIN_EMAIL")

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


# ---------------- BUSINESS DOCUMENT UPLOAD ---------------- #
@router.post("/business-document")
async def upload_business_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    user_id: int | None = Form(None),   # 👈 allow admin override
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    owner_id = current_user.id

    # 🔐 admin can upload for selected user
    if getattr(current_user, "jwt_role", None) == "admin" and user_id:
        owner_id = user_id

    drive_id = await _upload_to_drive(
        file=file,
        user_id=owner_id,
        doc_type=doc_type,
        db=db
    )

    return {
        "drive_file_id": drive_id,
        "filename": file.filename,
        "owner_id": owner_id,
        "doc_type": doc_type,
    }


# ---------------- DELETE (shared) ---------------- #
@router.delete("/business-document/{file_id}")
@router.delete("/personal-document/{file_id}")
async def delete_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    try:
        service = get_drive_service()
        service.files().delete(fileId=file_id).execute()

        crud.delete_uploaded_file(db, file_id, current_user.id)

        return {"deleted": True}

    except Exception as e:
        logger.exception("Delete failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- LIST USER FILES ---------------- #
@router.get("/my-documents")
def my_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user_real)):
    return db.query(crud.UploadedFile).filter_by(owner_id=current_user.id).all()


@router.get("/engagement-letter/status")
def engagement_letter_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    record = (
        db.query(crud.UploadedFile)
        .filter(
            crud.UploadedFile.owner_id == current_user.id,
            crud.UploadedFile.doc_type == "EngagementLetter"
        )
        .first()
    )

    if not record:
        return {"uploaded": False}

    return {
        "uploaded": True,
        "file_id": record.drive_file_id,
        "filename": record.filename,
    }








# ---------------- ADMIN DOCUMENT UPLOAD ---------------- #
@router.post("/admin-upload")
async def admin_upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    # 🔐 Only admin allowed
    if getattr(current_user, "jwt_role", None) != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    try:
        # 🔁 important for FastAPI file streams
        await file.seek(0)

        # ⬆️ Upload FOR THE USER (not admin)
        drive_id = await _upload_to_drive(
            file=file,
            user_id=user_id,      # 🔥 SAME USER ID
            doc_type=doc_type,    # 🔥 "Document 01 / 02 / 03"
            db=db,
        )

        return {
            "drive_file_id": drive_id,
            "filename": file.filename,
            "user_id": user_id,
            "doc_type": doc_type,
        }

    except Exception as e:
        logger.exception("Admin upload failed")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- ADMIN DELETE DOCUMENT ---------------- #
@router.delete("/admin-document/{file_id}")
async def admin_delete_document(
    file_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    if getattr(current_user, "jwt_role", None) != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    from app.models import UploadedFile

    record = db.query(UploadedFile).filter(
        UploadedFile.drive_file_id == file_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="File not found")

    service = get_drive_service()
    service.files().delete(fileId=file_id).execute()

    db.delete(record)
    db.commit()

    return {"deleted": True}
