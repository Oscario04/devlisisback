import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from app.core.config import get_settings
from app.core.exceptions import EmailDeliveryError
from app.models.contact_request import ContactRequest
from app.utils.email_templates import build_new_lead_email_body

logger = logging.getLogger(__name__)

settings = get_settings()


class EmailService(Protocol):
    def send_new_lead_notification(self, contact: ContactRequest) -> None:
        ...


class SmtpEmailService:
    def send_new_lead_notification(self, contact: ContactRequest) -> None:
        if not settings.smtp_is_configured():
            raise EmailDeliveryError("SMTP no configurado")

        message = EmailMessage()
        message["Subject"] = "Nuevo lead desde Devlisis.com"
        message["From"] = settings.smtp_from
        message["To"] = settings.smtp_from
        message.set_content(build_new_lead_email_body(contact))

        try:
            with smtplib.SMTP(
                settings.smtp_host,
                settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
            ) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()

                smtp.login(settings.smtp_user, settings.smtp_password)
                smtp.send_message(message)

        except Exception as exc:
            logger.exception("SMTP error", exc_info=exc)
            raise EmailDeliveryError("No se pudo enviar correo") from exc