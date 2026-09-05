import os
from pathlib import Path
from typing import List, Union
import json
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    MONGO_DB_NAME: str = Field(
        default="auth_db",
        description="MongoDB database name",
    )
    JWT_SECRET_KEY: str = Field(
        default="change-this-super-secret-key-in-production-min-32-chars",
        description="Secret key used for signing JWT tokens",
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        description="Algorithm for JWT signing",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        description="Access token lifespan in minutes",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token lifespan in days",
    )
    COOKIE_SECURE: bool = Field(
        default=False,
        description="Set to True in production for HTTPS only cookies",
    )
    COOKIE_SAMESITE: str = Field(
        default="lax",
        description="SameSite cookie policy (lax, strict, none)",
    )
    COOKIE_PATH: str = Field(
        default="/api/auth",
        description="Path scope for the refresh token cookie",
    )
    CORS_ORIGINS: Union[List[str], str] = Field(
        default=["http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Document upload settings
    MAX_UPLOAD_MB: int = Field(
        default=20,
        description="Maximum upload size in megabytes",
    )
    UPLOAD_DIR: str = Field(
        default=str(BACKEND_DIR / "uploads"),
        description="Upload storage directory",
    )

    @property
    def max_upload_mb(self) -> int:
        return self.MAX_UPLOAD_MB

    @property
    def upload_dir(self) -> str:
        return self.UPLOAD_DIR

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [origin.strip() for origin in v_stripped.split(",") if origin.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]

    model_config = SettingsConfigDict(
        env_file=(ENV_PATH, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
