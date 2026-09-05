from typing import Optional
from fastapi import APIRouter, Depends, Response, Cookie, status
from pymongo.database import Database
from backend.core.config import settings
from backend.database.database import get_db
from backend.models.user import User
from backend.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenResponse,
    MessageResponse,
    ProtectedResponse,
)
from backend.services.auth_service import AuthService
from backend.core.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def register(user_data: UserRegister, db: Database = Depends(get_db)):
    """
    Create a new user account in MongoDB with unique email and bcrypt-hashed password.
    """
    user = AuthService.register_user(db=db, user_data=user_data)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in with email and password",
)
def login(
    credentials: UserLogin,
    response: Response,
    db: Database = Depends(get_db),
):
    """
    Authenticate user credentials against MongoDB, return a short-lived Bearer access token,
    and attach a long-lived HttpOnly refresh token cookie.
    """
    user = AuthService.authenticate_user(db=db, credentials=credentials)
    access_token, refresh_token = AuthService.create_user_session(db=db, user=user)

    # Set HttpOnly cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=settings.COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
        ),
    )


@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    summary="Rotate refresh token and issue new access token",
)
def refresh(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db: Database = Depends(get_db),
):
    """
    Reads the refresh token from HttpOnly cookie, validates it against MongoDB,
    rotates it, sets a new HttpOnly refresh token cookie, and returns a new Bearer access token.
    """
    new_access_token, new_refresh_token = AuthService.rotate_refresh_token(
        db=db, raw_token=refresh_token
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        path=settings.COOKIE_PATH,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )

    return RefreshTokenResponse(
        access_token=new_access_token,
        token_type="bearer",
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out and revoke refresh session",
)
def logout(
    response: Response,
    refresh_token: Optional[str] = Cookie(default=None),
    db: Database = Depends(get_db),
):
    """
    Revokes the current refresh token session in MongoDB and clears
    the HttpOnly refresh cookie.
    """
    AuthService.revoke_refresh_token(db=db, raw_token=refresh_token)

    response.delete_cookie(
        key="refresh_token",
        path=settings.COOKIE_PATH,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

    return MessageResponse(message="Logged out successfully")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Fetch the currently authenticated user's profile details using the Bearer access token.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
    )


@router.get(
    "/protected",
    response_model=ProtectedResponse,
    summary="Protected endpoint for authentication verification",
)
def get_protected(current_user: User = Depends(get_current_user)):
    """
    A protected test endpoint verifying access with a valid Bearer token.
    """
    return ProtectedResponse(
        message="Authenticated access granted",
        user_id=current_user.id,
    )
