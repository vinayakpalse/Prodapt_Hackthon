from bson import ObjectId
from fastapi import HTTPException, status


def parse_object_id(id_str: str, field_name: str = "id") -> ObjectId:
    """Safely parses an ObjectId from string or raises HTTP 400 Bad Request."""
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name}",
        )
