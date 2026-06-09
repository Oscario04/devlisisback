from collections.abc import Generator

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.database import Database

from app.core.config import settings

mongo_client = MongoClient(
    settings.mongodb_uri,
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=10000,
    retryWrites=True,
    retryReads=True,
    tz_aware=True,
)


def get_database() -> Database:
    return mongo_client[settings.mongodb_db_name]


def get_db() -> Generator[Database, None, None]:
    yield get_database()


def initialize_mongo_indexes() -> None:
    db = get_database()
    collection = db["contact_requests"]
    collection.create_index([("created_at", DESCENDING)], background=True)
    collection.create_index([("email", ASCENDING)], background=True)


def close_mongo_connection() -> None:
    mongo_client.close()
