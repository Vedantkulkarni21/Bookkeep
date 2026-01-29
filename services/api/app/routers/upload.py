
import os
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials as OAuth2Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.models import AdminDocument
from app.db import get_db
import app.crud as crud
from app.routers.auth import get_current_user_real
from app.utils.emailer import send_email
from app.models import User
from app.models import (
    AdminDocument,
    PersonalDocument,
    BusinessDocument,
    User,          # ✅ THIS WAS MISSING
)
from app.models import User


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["upload"])

SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID")

OAUTH_TOKEN_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "oauth_token.json")
)

async def upload_to_drive(file: UploadFile) -> str:
    await file.seek(0)

    service = get_drive_service()

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=os.path.splitext(file.filename)[1]
    ) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        media = MediaFileUpload(tmp_path, mimetype=file.content_type)
        meta = {"name": file.filename}

        if DRIVE_FOLDER_ID:
            meta["parents"] = [DRIVE_FOLDER_ID]

        created = service.files().create(
            body=meta,
            media_body=media,
            fields="id"
        ).execute()

        return created["id"]

    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            logger.warning("Temp cleanup failed")


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


#  drive_id = await upload_to_drive(file)

# @router.post("/admin-documents")
# async def upload_admin_document(
#     file: UploadFile = File(...),
#     doc_key: str = Form(...),
#     doc_label: str = Form(...),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):

#     drive_id = await upload_to_drive(file)

#     record = AdminDocument(
#         doc_key=doc_key,
#         doc_label=doc_label,
#         filename=file.filename,
#         drive_file_id=drive_id,
#         content_type=file.content_type,
#         uploaded_by=current_user.id,
#     )

#     db.add(record)
#     db.commit()
#     db.refresh(record)

#     return {
#         "id": record.id,
#         "doc_key": record.doc_key,
#         "doc_label": record.doc_label,
#         "filename": record.filename,
#         "drive_file_id": record.drive_file_id,
#     }

@router.post("/admin-documents")
async def upload_admin_document(
    file: UploadFile = File(...),
    doc_key: str = Form(...),
    doc_label: str = Form(...),
    user_id: int = Form(...),          # 👈 add
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    drive_id = await upload_to_drive(file)

    record = AdminDocument(
        doc_key=doc_key,
        doc_label=doc_label,
        filename=file.filename,
        drive_file_id=drive_id,
        content_type=file.content_type,
        uploaded_by=current_user.id,   # admin
        user_id=user_id,               # 👈 target user
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "doc_label": record.doc_label,
        "filename": record.filename,
        "drive_file_id": record.drive_file_id,
    }



# @router.get("/admin-documents")
# def list_admin_documents(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     # allow BOTH user and admin
#     if current_user.jwt_role not in ("admin", "user"):
#         raise HTTPException(status_code=403, detail="Unauthorized")

#     docs = (
#         db.query(AdminDocument)
#         .order_by(AdminDocument.uploaded_at.desc())
#         .all()
#     )

#     return [
#         {
#             "id": d.id,
#             "doc_key": d.doc_key,
#             "doc_label": d.doc_label,
#             "filename": d.filename,
#             "drive_file_id": d.drive_file_id,
#         }
#         for d in docs
#     ]

# @router.get("/admin-documents")
# def list_admin_documents(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user_real),
# ):
#     # Admin sees documents for selected user (via query param)
#     if current_user.jwt_role == "admin":
#         return (
#             db.query(AdminDocument)
#             .order_by(AdminDocument.uploaded_at.desc())
#             .all()
#         )

#     # User sees ONLY documents uploaded for them
#     return (
#         db.query(AdminDocument)
#         .filter(AdminDocument.user_id == current_user.id)
#         .order_by(AdminDocument.uploaded_at.desc())
#         .all()
#     )


@router.get("/admin-documents")
def list_admin_documents(
    user_id: int | None = None,          # 👈 IMPORTANT
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    if current_user.jwt_role == "admin":
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id is required for admin"
            )

        docs = (
            db.query(AdminDocument)
            .filter(AdminDocument.user_id == user_id)
            .order_by(AdminDocument.uploaded_at.desc())
            .all()
        )

    elif current_user.jwt_role == "user":
        docs = (
            db.query(AdminDocument)
            .filter(AdminDocument.user_id == current_user.id)
            .order_by(AdminDocument.uploaded_at.desc())
            .all()
        )

    else:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return [
        {
            "id": d.id,
            "doc_key": d.doc_key,
            "doc_label": d.doc_label,
            "filename": d.filename,
            "drive_file_id": d.drive_file_id,
        }
        for d in docs
    ]



@router.delete("/admin-documents/{doc_id}")
def delete_admin_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    if current_user.jwt_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")

    doc = db.query(AdminDocument).filter_by(id=doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    service = get_drive_service()
    service.files().delete(fileId=doc.drive_file_id).execute()

    db.delete(doc)
    db.commit()

    return {"deleted": True}



from app.models import PersonalDocument

@router.get("/personal-documents")
def list_personal_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    return (
        db.query(PersonalDocument)
        .filter(PersonalDocument.user_id == current_user.id)
        .order_by(PersonalDocument.uploaded_at.desc())
        .all()
    )

@router.delete("/personal-documents/{doc_id}")
def delete_personal_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    doc = (
        db.query(PersonalDocument)
        .filter(
            PersonalDocument.id == doc_id,
            PersonalDocument.user_id == current_user.id
        )
        .first()
    )

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # delete from Drive
    service = get_drive_service()
    try:
        service.files().delete(fileId=doc.drive_file_id).execute()
    except Exception:
        logger.warning("Drive delete failed, continuing DB cleanup")

    # delete from DB
    db.delete(doc)
    db.commit()

    return {"deleted": True}



from app.models import BusinessDocument

@router.get("/business-documents")
def list_business_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    return (
        db.query(BusinessDocument)
        .filter(BusinessDocument.user_id == current_user.id)  # ✅ IMPORTANT
        .order_by(BusinessDocument.uploaded_at.desc())
        .all()
    )



@router.delete("/business-documents/{doc_id}")
def delete_business_document(
    doc_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    doc = db.query(BusinessDocument).filter_by(id=doc_id).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Not found")

    service = get_drive_service()
    try:
        service.files().delete(fileId=doc.drive_file_id).execute()
    except Exception:
        logger.warning("Drive delete failed, continuing DB cleanup")

    db.delete(doc)
    db.commit()

    return {"deleted": True}





@router.get("/admin/users/{user_id}/documents")
def get_user_all_documents(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    if current_user.jwt_role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    personal_docs = (
        db.query(PersonalDocument)
        .filter(PersonalDocument.user_id == user_id)
        .order_by(PersonalDocument.uploaded_at.desc())
        .all()
    )

    business_docs = (
    db.query(BusinessDocument)
    .filter(BusinessDocument.user_id == user_id)  # ✅ CORRECT
    .order_by(BusinessDocument.uploaded_at.desc())
    .all()
)


    documents = []

    for d in personal_docs:
        documents.append({
            "id": d.id,
            "table": "personal",
            "doc_type": d.doc_type,
            "filename": d.filename,
            "drive_file_id": d.drive_file_id,
            "uploaded_at": d.uploaded_at,
        })

    for d in business_docs:
        documents.append({
            "id": d.id,
            "table": "business",
            "doc_type": d.business_type,
            "filename": d.filename,
            "drive_file_id": d.drive_file_id,
            "uploaded_at": d.uploaded_at,
        })

    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
        "documents": documents,
    }


async def send_upload_emails(
    *,
    user_email: str,
    filename: str,
    doc_category: str,  # "Personal" | "Business"
):
    admin_email = os.getenv("ADMIN_EMAIL")

    # Email to USER
    await send_email(
        to=user_email,
        subject=f"New {doc_category} Document Uploaded — BookKeepro",
        body=f"""
        <p>Dear Sir/Ma’am,</p>

        <p>We have successfully received your {doc_category.lower()} document:</p>
        <p><strong>{filename}</strong></p>

        <p>Our team will review the document and update you shortly.</p>

        <br>
        <strong>BookKeepro Team</strong>
        """,
    )

    # Email to ADMIN
    if admin_email:
        await send_email(
            to=admin_email,
            subject=f"New {doc_category} Document Uploaded — BookKeepro",
            body=f"""
            <p>User <strong>{user_email}</strong> uploaded a {doc_category.lower()} document.</p>
            <p><strong>File:</strong> {filename}</p>
            """,
        )


@router.post("/personal-documents")
async def upload_personal_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    drive_id = await upload_to_drive(file)

    record = PersonalDocument(
        user_id=current_user.id,
        doc_type=doc_type,
        filename=file.filename,
        drive_file_id=drive_id,
        content_type=file.content_type,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    await send_upload_emails(
        user_email=current_user.email,
        filename=file.filename,
        doc_category="Personal",
    )

    return {
        "id": record.id,
        "filename": record.filename,
        "doc_type": record.doc_type,
        "drive_file_id": record.drive_file_id,
        "uploaded_at": record.uploaded_at,
        "email_sent": True,
    }


    return {
        "id": record.id,
        "filename": record.filename,
        "doc_type": record.doc_type,
        "drive_file_id": record.drive_file_id,
        "uploaded_at": record.uploaded_at,
        "email_sent": True,
    }

@router.post("/business-documents")
async def upload_business_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    drive_id = await upload_to_drive(file)

    record = BusinessDocument(
        user_id=current_user.id,
        business_type=doc_type,
        filename=file.filename,
        drive_file_id=drive_id,
        content_type=file.content_type,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    await send_upload_emails(
        user_email=current_user.email,
        filename=file.filename,
        doc_category="Business",
    )

    return {
        "id": record.id,
        "filename": record.filename,
        "business_type": record.business_type,
        "drive_file_id": record.drive_file_id,
        "email_sent": True,
    }
