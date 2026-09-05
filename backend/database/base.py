"""
Database base module for MongoDB backend.
Provides collection definitions and initialization utilities.
"""
from backend.database.database import db, get_db, init_db

__all__ = ["db", "get_db", "init_db"]
