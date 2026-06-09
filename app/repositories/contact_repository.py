from datetime import datetime, timedelta, timezone

from pymongo import DESCENDING
from pymongo.database import Database

from app.models.contact_request import ContactRequest
from app.schemas.contact import ContactRequestCreate


class ContactRequestRepository:
    """Repository responsible for contact request persistence."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self.collection = self.db["contact_requests"]

    def create(self, payload: ContactRequestCreate) -> ContactRequest:
        document = {
            "name": payload.name,
            "company": payload.company,
            "email": str(payload.email),
            "phone": payload.phone,
            "message": payload.message,
            "created_at": datetime.now(timezone.utc),
        }
        result = self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return ContactRequest.from_mongo_document(document)

    def list_all(self) -> list[ContactRequest]:
        cursor = self.collection.find().sort("created_at", DESCENDING)
        return [ContactRequest.from_mongo_document(document) for document in cursor]

    def find_recent_duplicate(self, payload: ContactRequestCreate, within_seconds: int) -> ContactRequest | None:
        threshold = datetime.now(timezone.utc) - timedelta(seconds=within_seconds)
        document = self.collection.find_one(
            {
                "name": payload.name,
                "email": str(payload.email),
                "message": payload.message,
                "created_at": {"$gte": threshold},
            },
            sort=[("created_at", DESCENDING)],
        )
        if not document:
            return None
        return ContactRequest.from_mongo_document(document)
