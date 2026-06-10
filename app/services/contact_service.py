import logging

from app.core.config import get_settings
from app.core.exceptions import EmailDeliveryError
from app.models.contact_request import ContactRequest
from app.repositories.contact_repository import ContactRequestRepository
from app.schemas.contact import ContactRequestCreate
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


class ContactService:
    """Application service that orchestrates persistence and email delivery."""

    def __init__(
        self,
        repository: ContactRequestRepository,
        email_service: EmailService,
    ) -> None:
        self.repository = repository
        self.email_service = email_service

    def create_contact_request(self, payload: ContactRequestCreate) -> ContactRequest:
        settings = get_settings()  # ✅ runtime safe

        existing = self.repository.find_recent_duplicate(
            payload=payload,
            within_seconds=settings.contact_dedupe_window_seconds,
        )

        if existing:
            logger.info(
                "Duplicate lead submission detected",
                extra={"contact_id": existing.id, "email": existing.email},
            )
            return existing

        contact = self.repository.create(payload)

        try:
            self.email_service.send_new_lead_notification(contact)
        except EmailDeliveryError as exc:
            logger.warning(
                "Lead persisted but email delivery failed",
                extra={"contact_id": contact.id, "error": str(exc)},
            )

        return contact

    def list_contact_requests(self) -> list[ContactRequest]:
        return self.repository.list_all()