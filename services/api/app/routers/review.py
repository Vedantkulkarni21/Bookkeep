from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.utils.emailer import send_email
from app import crud

router = APIRouter(prefix="/api/review", tags=["review"])


@router.post("/notify-user")
async def notify_user_review(
    payload: dict,
    db: Session = Depends(get_db)
):
    user_id = payload.get("user_id")
    approved = payload.get("approved", [])
    rejected = payload.get("rejected", [])
    timeline = payload.get("timeline", 0)

    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    user = crud.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    approved_html = "".join(f"<li>{d}</li>" for d in approved)
    rejected_html = "".join(f"<li>{d}</li>" for d in rejected)

    body = f"""
    <p>Dear Sir/Ma’am,</p>

    <p>
    Your uploaded documents have been reviewed. Please find the status details below:
    </p>

    <p><strong>Approved Documents</strong></p>
    <ul>
        {approved_html or "<li>None</li>"}
    </ul>

    <p><strong>Rejected Documents</strong></p>
    <ul>
        {rejected_html or "<li>None</li>"}
    </ul>

    <p>
    <strong>Estimated Filing Timeline:</strong> {timeline} days
    </p>

    <p>
    Our team will contact you if any additional information or clarification is required.
    </p>

    <p style="margin-top:20px;">
    Kind regards,<br>
    <strong>BookKeepro Team</strong>
    </p>
    """

    await send_email(
        to=user.email,
        subject="Document Review Update — BookKeepro",
        body=body
    )

    return {"status": "sent"}
