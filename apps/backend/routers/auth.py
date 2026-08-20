"""
Authentication Router for Awade API

This module provides authentication endpoints for the Awade platform, including Google OAuth, 
email/password signup, login, and password reset functionality. It delegates business logic
to the AuthService for clean separation of concerns.

Endpoints:
- /api/auth/google: Google OAuth login
- /api/auth/signup: Email/password registration
- /api/auth/login: Email/password login
- /api/auth/me: Get current user profile
- /api/auth/refresh: Refresh JWT token
- /api/auth/logout: Logout (client-side token removal)
- /api/auth/forgot-password: Password reset request
- /api/auth/reset-password: Password reset

Author: Tolulope Babajide
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from apps.backend.database import get_db
from apps.backend.schemas.users import AuthResponse, CookieAuthResponse, UserResponse, UserCreate, UserLogin, PasswordResetRequest, PasswordReset
from apps.backend.models import User
from apps.backend.dependencies import get_current_user
from apps.backend.services.auth_service import AuthService
from apps.backend.services.token_service import TokenService
from apps.backend.limiter import limiter

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging
import os

logger = logging.getLogger(__name__)

# Determine if running in production
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------------------------------------------------------------------------
# Cookie helper
# ---------------------------------------------------------------------------

ACCESS_TOKEN_MAX_AGE = 30 * 60  # 30 minutes
REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60  # 7 days

def _cookie_options() -> dict[str, object]:
    """Return environment-appropriate cookie flags.

    The production frontend and API are hosted on different sites, so browsers
    require SameSite=None together with Secure for credentialed API requests.
    """
    return {
        "httponly": True,
        "secure": IS_PRODUCTION,
        "samesite": "none" if IS_PRODUCTION else "lax",
        "path": "/",
    }

def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set both auth cookies (access + refresh) as HttpOnly on a response."""
    cookie_options = _cookie_options()
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_MAX_AGE,
        **cookie_options,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_MAX_AGE,
        **cookie_options,
    )


class GoogleAuthRequest(BaseModel):
    """
    Request schema for Google OAuth authentication.
    """
    credential: str
    role: str = "PARENT"  # Default to PARENT for new Google sign-ups

class TokenRefreshRequest(BaseModel):
    """
    Request schema for token refresh.
    """
    refresh_token: str

@router.post("/google", response_model=CookieAuthResponse)
@limiter.limit("10/minute")
def google_auth(
    request: Request,
    response: Response,
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth credential (ID token).
    The access token is delivered as an HttpOnly cookie; only user data is
    returned in the response body.
    Rate limit: 10 requests per minute.
    """
    try:
        service = AuthService(db)
        auth_response, refresh_token = service.authenticate_google_user(payload.credential, requested_role=payload.role)
    except HTTPException:
        raise
    except Exception:
        logger.error("Unexpected error in google_auth endpoint", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during Google authentication")

    _set_auth_cookies(response, auth_response.access_token, refresh_token)
    return CookieAuthResponse(user=auth_response.user)

@router.post("/signup", response_model=CookieAuthResponse)
@limiter.limit("5/minute")
def signup(
    request: Request,
    response: Response,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    The access token is delivered as an HttpOnly cookie; only user data is
    returned in the response body.
    Rate limit: 5 requests per minute.
    """
    try:
        service = AuthService(db)
        auth_response, refresh_token = service.register_user(user_data)
    except HTTPException:
        raise
    except Exception:
        logger.error("Unexpected error in signup endpoint", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during registration")

    _set_auth_cookies(response, auth_response.access_token, refresh_token)
    return CookieAuthResponse(user=auth_response.user)

@router.post("/login", response_model=CookieAuthResponse)
@limiter.limit("10/minute")
def login(
    request: Request,
    response: Response,
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password.
    The access token is delivered as an HttpOnly cookie; only user data is
    returned in the response body.
    Rate limit: 10 requests per minute.
    """
    try:
        service = AuthService(db)
        auth_response, refresh_token = service.authenticate_user(user_data)
    except HTTPException:
        raise
    except Exception:
        logger.error("Unexpected error in login endpoint", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred during authentication")

    _set_auth_cookies(response, auth_response.access_token, refresh_token)
    return CookieAuthResponse(user=auth_response.user)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile."""
    service = AuthService(db)
    return service.get_current_user_profile(current_user)

@router.post("/refresh", response_model=CookieAuthResponse)
@limiter.limit("20/minute")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh JWT token using the refresh_token HttpOnly cookie and rotate both tokens.
    The new access token is issued as an HttpOnly cookie; only user data is returned in the
    response body.
    Rate limit: 20 requests per minute.
    """
    stored_refresh_token = request.cookies.get("refresh_token")
    if not stored_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )

    service = TokenService(db)
    redis_pool = getattr(request.app.state, "redis", None)
    auth_response, new_refresh_token = await service.refresh_access_token(stored_refresh_token, redis_pool)

    _set_auth_cookies(response, auth_response.access_token, new_refresh_token)
    return CookieAuthResponse(user=auth_response.user)

@router.post("/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logout endpoint (client-side token removal and server-side blacklisting).
    """
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        service = TokenService(db)
        redis_pool = getattr(request.app.state, "redis", None)
        if redis_pool:
            await service.blacklist_refresh_token(refresh_token, redis_pool)
            
    cookie_options = _cookie_options()
    response.delete_cookie("access_token", **cookie_options)
    response.delete_cookie("refresh_token", **cookie_options)
    return {"message": "Logged out successfully"}

@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(
    request: Request,
    payload: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset for a user.
    Rate limit: 5 requests per minute (prevents email-bombing and user enumeration).
    """
    service = AuthService(db)
    return service.request_password_reset(payload.email)

@router.post("/reset-password")
@limiter.limit("5/minute")
def reset_password(
    request: Request,
    payload: PasswordReset,
    db: Session = Depends(get_db)
):
    """
    Reset user password using reset token.
    Rate limit: 5 requests per minute (prevents token brute-force).
    """
    service = AuthService(db)
    return service.reset_password(payload.token, payload.new_password)
