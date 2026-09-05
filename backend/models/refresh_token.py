from datetime import datetime, timezone
from typing import Optional, Any, Dict
from bson import ObjectId


class RefreshToken:
    """
    MongoDB RefreshToken document model representation.
    """
    def __init__(
        self,
        user_id: str,
        token_jti: str,
        token_hash: str,
        expires_at: datetime,
        revoked: bool = False,
        created_at: Optional[datetime] = None,
        revoked_at: Optional[datetime] = None,
        replaced_by_jti: Optional[str] = None,
        _id: Optional[Any] = None,
        id: Optional[str] = None,
    ):
        self.user_id = str(user_id)
        self.token_jti = token_jti
        self.token_hash = token_hash
        self.expires_at = expires_at
        self.revoked = revoked
        self.created_at = created_at or datetime.now(timezone.utc)
        self.revoked_at = revoked_at
        self.replaced_by_jti = replaced_by_jti
        self._id = _id
        self.id = id or (str(_id) if _id is not None else None)

    def to_dict(self) -> Dict[str, Any]:
        data = {
            "user_id": self.user_id,
            "token_jti": self.token_jti,
            "token_hash": self.token_hash,
            "expires_at": self.expires_at,
            "revoked": self.revoked,
            "created_at": self.created_at,
            "revoked_at": self.revoked_at,
            "replaced_by_jti": self.replaced_by_jti,
        }
        if self._id is not None:
            data["_id"] = self._id
        return data

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["RefreshToken"]:
        if not doc:
            return None
        _id = doc.get("_id")
        return cls(
            user_id=doc["user_id"],
            token_jti=doc["token_jti"],
            token_hash=doc["token_hash"],
            expires_at=doc["expires_at"],
            revoked=doc.get("revoked", False),
            created_at=doc.get("created_at"),
            revoked_at=doc.get("revoked_at"),
            replaced_by_jti=doc.get("replaced_by_jti"),
            _id=_id,
            id=str(_id) if _id is not None else doc.get("id"),
        )
