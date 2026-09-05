# app compatibility package
from backend.core.config import settings
from backend.database.database import get_db, db

__all__ = ["settings", "get_db", "db"]
