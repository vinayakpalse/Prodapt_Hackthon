from datetime import datetime, timezone
from typing import Tuple, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database
from backend.models.user import User
from backend.models.refresh_token import RefreshToken
from backend.schemas.auth import UserRegister, UserLogin
from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_jwt,
)
from backend.utils.token_utils import hash_token


class AuthService:
    @staticmethod
    def register_user(db: Database, user_data: UserRegister) -> User:
        """
        Registers a new user in MongoDB after verifying email uniqueness and hashing password.
        """
        normalized_email = user_data.email.strip().lower()

        existing_user = db.users.find_one({"email": normalized_email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        password_hash = hash_password(user_data.password)
        now_utc = datetime.now(timezone.utc)

        user_doc = {
            "name": user_data.name.strip(),
            "email": normalized_email,
            "password_hash": password_hash,
            "is_active": True,
            "created_at": now_utc,
            "updated_at": now_utc,
        }

        result = db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id

        return User.from_doc(user_doc)

    @staticmethod
    def authenticate_user(db: Database, credentials: UserLogin) -> User:
        """
        Validates user credentials against MongoDB. Uses generic message to prevent user enumeration.
        """
        normalized_email = credentials.email.strip().lower()
        user_doc = db.users.find_one({"email": normalized_email})

        if not user_doc or not verify_password(credentials.password, user_doc["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = User.from_doc(user_doc)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    @staticmethod
    def create_user_session(db: Database, user: User) -> Tuple[str, str]:
        """
        Generates access and refresh tokens, saves the hashed refresh token
        in MongoDB collection 'refresh_tokens', and returns both tokens.
        """
        access_token = create_access_token(user.id)
        refresh_token, jti, expires_at = create_refresh_token(user.id)

        token_doc = {
            "user_id": str(user.id),
            "token_jti": jti,
            "token_hash": hash_token(refresh_token),
            "expires_at": expires_at,
            "revoked": False,
            "created_at": datetime.now(timezone.utc),
            "revoked_at": None,
            "replaced_by_jti": None,
        }

        db.refresh_tokens.insert_one(token_doc)

        return access_token, refresh_token

    @staticmethod
    def rotate_refresh_token(db: Database, raw_token: Optional[str]) -> Tuple[str, str]:
        """
        Rotates the refresh token:
        1. Validates JWT signature and type == 'refresh'.
        2. Retrieves refresh token record from MongoDB.
        3. Detects token reuse (revokes all active user tokens if detected).
        4. Validates expiration and token hash.
        5. Issues new tokens, revokes the old one, and saves the new record.
        """
        if not raw_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = decode_jwt(raw_token)

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type: refresh token required",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id_str = payload.get("sub")
        jti = payload.get("jti")
        if not user_id_str or not jti:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_doc = db.refresh_tokens.find_one({"token_jti": jti})

        if not token_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        now_utc = datetime.now(timezone.utc)

        # Token Reuse Detection
        if token_doc.get("revoked", False):
            db.refresh_tokens.update_many(
                {"user_id": user_id_str, "revoked": False},
                {"$set": {"revoked": True, "revoked_at": now_utc}},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token reuse detected. All sessions revoked for security.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Expiration Check
        expires_at = token_doc["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < now_utc:
            db.refresh_tokens.update_one(
                {"_id": token_doc["_id"]},
                {"$set": {"revoked": True, "revoked_at": now_utc}},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Hash Check
        if token_doc.get("token_hash") != hash_token(raw_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify User Existence and Active Status
        user_doc = None
        try:
            if ObjectId.is_valid(user_id_str):
                user_doc = db.users.find_one({"_id": ObjectId(user_id_str)})
        except Exception:
            pass

        if not user_doc:
            user_doc = db.users.find_one({"id": user_id_str})

        user = User.from_doc(user_doc)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive or not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate new tokens
        new_access_token = create_access_token(user.id)
        new_refresh_token, new_jti, new_expires_at = create_refresh_token(user.id)

        # Revoke old refresh token and link replacement JTI
        db.refresh_tokens.update_one(
            {"_id": token_doc["_id"]},
            {
                "$set": {
                    "revoked": True,
                    "revoked_at": now_utc,
                    "replaced_by_jti": new_jti,
                }
            },
        )

        # Store new refresh token
        new_token_doc = {
            "user_id": str(user.id),
            "token_jti": new_jti,
            "token_hash": hash_token(new_refresh_token),
            "expires_at": new_expires_at,
            "revoked": False,
            "created_at": now_utc,
            "revoked_at": None,
            "replaced_by_jti": None,
        }
        db.refresh_tokens.insert_one(new_token_doc)

        return new_access_token, new_refresh_token

    @staticmethod
    def revoke_refresh_token(db: Database, raw_token: Optional[str]) -> bool:
        """
        Revokes a refresh token on logout.
        """
        if not raw_token:
            return True

        try:
            payload = decode_jwt(raw_token)
            if payload.get("type") == "refresh":
                jti = payload.get("jti")
                if jti:
                    db.refresh_tokens.update_one(
                        {"token_jti": jti, "revoked": False},
                        {
                            "$set": {
                                "revoked": True,
                                "revoked_at": datetime.now(timezone.utc),
                            }
                        },
                    )
        except Exception:
            pass

        return True
