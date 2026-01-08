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

    subject = "New Contact Enquiry Received — Follow-Up Required - BookKeepro"

    body = f"""
Dear Team,
<br> <br>
A new contact enquiry has been received. Please find the details below:
<br><br>
Name: {form.first_name} {form.last_name}<br>
Email: {form.email}<br>
Phone: {form.phone}
<br><br>
Kindly follow up with the user at the earliest convenience.
<br><br>
Thank you,
<br>
BookKeepro Support Team
"""

    # send email to admin
    background.add_task(
        send_email,
        to="info@bookkeepro.net",
        subject="New Contact Enquiry Received — Follow-Up Required - BookKeepro",
        body=f"""
            Dear Team,
            <br> <br>
            A new contact enquiry has been received. Please find the details below:
            <br><br>
            <b>Name:</b> {form.first_name} {form.last_name}<br>
            <b>Email:</b> {form.email}<br>
            <b>Phone:</b> {form.phone}<br><br>
            Kindly follow up with the user at the earliest convenience.
            <br><br>
            Thank you,<br>
            BookKeepro Support Team
        """
    )

    # auto-reply to user
    background.add_task(
        send_email,
        to=form.email,
        subject="Thanks for contacting BookKeepro",
        body=f"""
            Hi {form.first_name},<br><br>
            Thank you for reaching out to BookKeepro.<br>
            We’ve received your enquiry, and our team will get back to you shortly.<br><br>
            Best Regards,<br>
            BookKeepro Team
        """
    )

    return {"status": "sent"}
