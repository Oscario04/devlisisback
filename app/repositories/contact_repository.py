from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.contact_request import ContactRequest
from app.schemas.contact import ContactRequestCreate


class ContactRequestRepository:
    """Repository responsible for contact request persistence."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payload: ContactRequestCreate) -> ContactRequest:
        entity = ContactRequest(
            name=payload.name,
            company=payload.company,
            email=payload.email,
            phone=payload.phone,
            message=payload.message,
        )
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
        except Exception:
            self.db.rollback()
            raise
        return entity

    def list_all(self) -> list[ContactRequest]:
        stmt = select(ContactRequest).order_by(ContactRequest.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def find_recent_duplicate(self, payload: ContactRequestCreate, within_seconds: int) -> ContactRequest | None:
        threshold = datetime.utcnow() - timedelta(seconds=within_seconds)
        stmt = (
            select(ContactRequest)
            .where(ContactRequest.name == payload.name)
            .where(ContactRequest.email == payload.email)
            .where(ContactRequest.message == payload.message)
            .where(ContactRequest.created_at >= threshold)
            .order_by(ContactRequest.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(stmt)
