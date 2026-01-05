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
    <h2>Document Review Update — BookKeepro</h2>

    <p>Your uploaded documents were reviewed.</p>

    <h3 style="color:green">Approved</h3>
    <ul>{approved_html or "<li>None</li>"}</ul>

    <h3 style="color:red">Rejected</h3>
    <ul>{rejected_html or "<li>None</li>"}</ul>

    <p><b>Estimated Filing Timeline:</b> {timeline} days</p>

    <p>Our team will contact you if further information is needed.</p>
    """

    await send_email(
        to=user.email,
        subject="Your Document Review Status — BookKeepro",
        body=body
    )

    return {"status": "sent"}
