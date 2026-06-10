import logging
import smtplib
from email.message import EmailMessage
from typing import Protocol

from app.core.config import get_settings
from app.core.exceptions import EmailDeliveryError
from app.models.contact_request import ContactRequest
from app.utils.email_templates import build_new_lead_email_body

logger = logging.getLogger(__name__)


class EmailService(Protocol):
    def send_new_lead_notification(self, contact: ContactRequest) -> None:
        """Send a notification email for a newly received lead."""


class SmtpEmailService:
    def send_new_lead_notification(self, contact: ContactRequest) -> None:
        # 🔴 IMPORTANT: settings must be loaded at runtime (not import time)
        settings = get_settings()

        if not settings.smtp_is_configured():
            raise EmailDeliveryError(
                "El servicio SMTP no está configurado. Revisa las variables de entorno SMTP_."
            )

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

            logger.info(
                "Lead notification email sent",
                extra={"contact_id": contact.id},
            )

        except (smtplib.SMTPException, OSError) as exc:
            logger.exception("Failed to send lead notification email", exc_info=exc)
            raise EmailDeliveryError("No fue posible enviar el correo del lead.") from exc