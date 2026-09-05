from typing import Generator
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from backend.core.config import settings

# Initialize PyMongo client with connect=False for lazy connection and fast startup
client: MongoClient = MongoClient(
    settings.MONGO_URI,
    tz_aware=True,
    serverSelectionTimeoutMS=5000,
    connect=False,
)

db: Database = client[settings.MONGO_DB_NAME]


def get_db() -> Generator[Database, None, None]:
    """Dependency for obtaining MongoDB database instance."""
    yield db


def init_db(database: Database = None) -> None:
    """
    Ensures that essential indexes are created on MongoDB collections.
    Safe to call at application startup.
    """
    target_db = database if database is not None else db
    try:
        # Unique index on users.email
        target_db.users.create_index([("email", ASCENDING)], unique=True)

        # Indexes on refresh_tokens
        target_db.refresh_tokens.create_index([("token_jti", ASCENDING)], unique=True)
        target_db.refresh_tokens.create_index([("token_hash", ASCENDING)])
        target_db.refresh_tokens.create_index([("user_id", ASCENDING)])
    except Exception:
        # Index creation failure (e.g. if offline during tests or already exists)
        pass
