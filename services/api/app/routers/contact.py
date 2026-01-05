from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.utils.emailer import send_email

router = APIRouter(prefix="/api", tags=["contact"])

class ContactForm(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

@router.post("/contact")
async def contact_message(form: ContactForm, background: BackgroundTasks):

    subject = "New Contact Form Submission — BookKeepro"

    body = f"""
New contact enquiry received:

Name: {form.first_name} {form.last_name}
Email: {form.email}
Phone: {form.phone}

Please follow up with the user.
"""

    # send email to admin
    background.add_task(
        send_email,
        to="info@bookkeepro.net",
        subject="New Contact Form Submission — BookKeepro",
        body=f"""
            New contact enquiry received:<br><br>
            <b>Name:</b> {form.first_name} {form.last_name}<br>
            <b>Email:</b> {form.email}<br>
            <b>Phone:</b> {form.phone}<br><br>
            Please follow up with the user.
        """
    )

    # auto-reply to user
    background.add_task(
        send_email,
        to=form.email,
        subject="Thanks for contacting BookKeepro",
        body=f"""
            Hi {form.first_name},<br><br>
            Thanks for reaching out to BookKeepro.<br>
            Our team will get back to you shortly.<br><br>
            Best Regards,<br>
            BookKeepro Team
        """
    )

    return {"status": "sent"}
