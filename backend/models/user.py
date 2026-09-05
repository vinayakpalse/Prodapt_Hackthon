from datetime import datetime, timezone
from typing import Optional, Any, Dict
from bson import ObjectId


class User:
    """
    MongoDB User document model representation.
    """
    def __init__(
        self,
        name: str,
        email: str,
        password_hash: str,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        id: Optional[str] = None,
    ):
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self._id = _id
        self.id = id or (str(_id) if _id is not None else None)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "name": self.name,
            "email": self.email,
            "password_hash": self.password_hash,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self._id is not None:
            data["_id"] = self._id
        return data

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["User"]:
        if not doc:
            return None
        _id = doc.get("_id")
        return cls(
            name=doc["name"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            is_active=doc.get("is_active", True),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            _id=_id,
            id=str(_id) if _id is not None else doc.get("id"),
        )
