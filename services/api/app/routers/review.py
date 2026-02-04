
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import AdminDocument
from app.models import (
    AdminDocument,
    PersonalDocument,
    BusinessDocument,
    User,
)

from app.db import get_db
from app.utils.emailer import send_email
from app import crud

router = APIRouter(
    prefix="/api/review",
    tags=["review"]
)

DASHBOARD_LINK = "https://bookkeepro.net/dashboard"


# =========================================================
# Submit documents for review (ADMIN → USER)
# =========================================================
# @router.post("/submit")
# async def submit_review(payload: dict, db: Session = Depends(get_db)):
#     user_id = payload.get("user_id")

#     if not user_id:
#         raise HTTPException(status_code=400, detail="user_id required")

#     user = crud.get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Update review status
#     user.review_status = "submitted"
#     db.commit()

#     # Send email (clean, formatted version)
#     await send_email(
#         to=user.email,
#         subject="Documents Ready for Review — BookKeepro",
#         body=f"""
#         <p>Dear Sir/Ma’am,</p>

#         <p>
#           Your documents have been successfully submitted and are pending review.
#         </p>

#         <p>
#           Please log in to your dashboard to track the approval status:
#         </p>

#         <p>
#           <a href="{DASHBOARD_LINK}"
#              style="color:#0077c8;font-weight:600;text-decoration:none;">
#             👉 Go to Dashboard
#           </a>
#         </p>

#         <p style="margin-top:20px;">
#           Kind regards,<br>
#           <strong>BookKeepro Team</strong>
#         </p>
#         """
#     )

#     return {"status": "submitted"}


@router.post("/submit")
async def submit_review(payload: dict, db: Session = Depends(get_db)):
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update review status
    user.review_status = "submitted"
    db.commit()

    email_sent = True

    try:
        await send_email(
            to=user.email,
            subject="Documents Ready for Review — BookKeepro",
            body=f"""
            <p>Dear Sir/Ma’am,</p>

            <p>Your documents have been successfully submitted and are pending review.</p>

            <p>
              <a href="{DASHBOARD_LINK}"
                 style="color:#0077c8;font-weight:600;text-decoration:none;">
                👉 Go to Dashboard
              </a>
            </p>

            <p style="margin-top:20px;">
              Kind regards,<br>
              <strong>BookKeepro Team</strong>
            </p>
            """
        )
    except Exception as e:
        email_sent = False
        logger.error(f"Email sending failed: {e}")

    return {
        "status": "submitted",
        "email_sent": email_sent
    }


# =========================================================
# Notify user after approval / rejection (ADMIN → USER)
# =========================================================
# @router.post("/notify-user")
# async def notify_user_review(
#     payload: dict,
#     db: Session = Depends(get_db)
# ):
#     user_id = payload.get("user_id")
#     approved = payload.get("approved", [])
#     rejected = payload.get("rejected", [])
#     personal_timeline = payload.get("personal_timeline", 0)
#     business_timeline = payload.get("business_timeline", 0)


#     if not user_id:
#         raise HTTPException(status_code=400, detail="user_id is required")

#     user = crud.get_user_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     approved_html = "".join(f"<li>{d}</li>" for d in approved) or "<li>None</li>"
#     rejected_html = "".join(f"<li>{d}</li>" for d in rejected) or "<li>None</li>"

#     body = f"""
#     <p>Dear Sir/Ma’am,</p>

#     <p>
#       Your uploaded documents have been reviewed. Please find the details below:
#     </p>

#     <p><strong>Approved Documents</strong></p>
#     <ul>
#       {approved_html}
#     </ul>

#     <p><strong>Rejected Documents</strong></p>
#     <ul>
#       {rejected_html}
#     </ul>

#     <p>
#     <strong>Estimated Filing Timeline:</strong>
#     </p>
#     <ul>
#       <li>Personal Documents: {personal_timeline} days</li>
#       <li>Business Documents: {business_timeline} days</li>
#     </ul>



#     <p>
#       Our team will contact you if any additional information or clarification is required.
#     </p>

#     <p style="margin-top:20px;">
#       Kind regards,<br>
#       <strong>BookKeepro Team</strong>
#     </p>
#     """

#     await send_email(
#         to=user.email,
#         subject="Document Review Update — BookKeepro",
#         body=body
#     )

#     return {"status": "notified"}



@router.post("/notify-user")
async def notify_user_review(
    payload: dict,
    db: Session = Depends(get_db)
):
    user_id = payload.get("user_id")
    approved = payload.get("approved", [])
    rejected = payload.get("rejected", [])

    # ✅ FIX
    personal_timeline = payload.get("personal_timeline", 0)
    business_timeline = payload.get("business_timeline", 0)

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    approved_html = "".join(f"<li>{d}</li>" for d in approved) or "<li>None</li>"
    rejected_html = "".join(f"<li>{d}</li>" for d in rejected) or "<li>None</li>"

    body = f"""
    <p>Dear Sir/Ma’am,</p>

    <p>Your uploaded documents have been reviewed.</p>

    <p><strong>Approved Documents</strong></p>
    <ul>{approved_html}</ul>

    <p><strong>Rejected Documents</strong></p>
    <ul>{rejected_html}</ul>

    <p><strong>Estimated Filing Timeline:</strong></p>
    <ul>
      <li>Personal Documents: {personal_timeline} days</li>
      <li>Business Documents: {business_timeline} days</li>
    </ul>

    <p>Kind regards,<br><strong>BookKeepro Team</strong></p>
    """

    await send_email(
        to=user.email,
        subject="Document Review Update — BookKeepro",
        body=body
    )

    return {"status": "notified"}





from app.routers.auth import get_current_user_real


@router.post("/admin-doc-response")
async def admin_doc_response(
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_real),
):
    if current_user.jwt_role != "user":
        raise HTTPException(status_code=403, detail="Users only")

    doc_id = payload.get("doc_id")
    status = payload.get("status")
    reason = payload.get("reason", "")

    if not doc_id or status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="Invalid payload")

    doc = db.query(AdminDocument).filter_by(id=doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    admin = db.query(User).filter_by(id=doc.uploaded_by).first()

    body = f"""
    <p>Dear Admin,</p>

    <p>
      The user <b>{current_user.email}</b> has
      <b>{status.upper()}</b> the document:
    </p>

    <p><b>{doc.doc_label}</b></p>
    """

    if status == "rejected":
        body += f"""
        <p><strong>Reason for rejection:</strong></p>
        <p>{reason}</p>
        """

    body += """
    <p style="margin-top:20px;">
      BookKeepro System
    </p>
    """

    await send_email(
        to=admin.email,
        # subject=f"Admin Document {status.capitalize()} — BookKeepro",
        subject=f"Admin Return Status {status.capitalize()} — BookKeepro",
        body=body
    )

    return {"status": "notified"}
