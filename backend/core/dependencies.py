from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pymongo.database import Database
from backend.database.database import get_db
from backend.models.user import User
from backend.core.security import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=True,
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Database = Depends(get_db),
) -> User:
    """
    Dependency that extracts the Bearer token, validates that it is an active access token,
    and returns the authenticated User instance from MongoDB.
    """
    payload = decode_jwt(token)

    # Enforce token type: must be 'access'
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_doc = None
    try:
        if ObjectId.is_valid(user_id_str):
            user_doc = db.users.find_one({"_id": ObjectId(user_id_str)})
    except Exception:
        pass

    if not user_doc:
        user_doc = db.users.find_one({"id": user_id_str})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = User.from_doc(user_doc)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_id(current_user: User = Depends(get_current_user)) -> str:
    """Returns the authenticated user's ID string."""
    return str(current_user.id)
