from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, EmailStr


class ContactRequest(BaseModel):
    id: str
    name: str
    company: str | None
    email: EmailStr
    phone: str | None
    message: str
    created_at: datetime

    @classmethod
    def from_mongo_document(cls, document: dict[str, Any]) -> "ContactRequest":
        created_at = document.get("created_at") or datetime.now(timezone.utc)
        if isinstance(created_at, datetime) and created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return cls(
            id=str(document.get("_id")),
            name=document.get("name", ""),
            company=document.get("company"),
            email=document.get("email", ""),
            phone=document.get("phone"),
            message=document.get("message", ""),
            created_at=created_at,
        )
