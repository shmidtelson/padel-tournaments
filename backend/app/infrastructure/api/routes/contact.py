"""Contact form: submit message (logged; plug mailer or Sentry in production)."""

import logging
from fastapi import APIRouter
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/contact", tags=["contact"])
logger = logging.getLogger(__name__)


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    subject: str = Field("", max_length=300)
    message: str = Field(..., min_length=1, max_length=10000)


@router.post("", status_code=200)
async def submit_contact(body: ContactRequest):
    """Accept contact form submission. Logs only; add email/Sentry in production."""
    logger.info(
        "contact_submit name=%s email=%s subject=%s len_message=%s",
        body.name[:50],
        body.email,
        body.subject[:50] if body.subject else "",
        len(body.message),
    )
    return {"status": "ok", "message": "Received"}
