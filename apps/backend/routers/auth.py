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
from fastapi import APIRouter, HTTPException, Depends, Request, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from apps.backend.database import get_db
from apps.backend.schemas.users import AuthResponse, UserResponse, UserCreate, UserLogin, PasswordResetRequest, PasswordReset
from apps.backend.models import User
from apps.backend.dependencies import get_current_user
from apps.backend.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

class GoogleAuthRequest(BaseModel):
    """
    Request schema for Google OAuth authentication.
    """
    credential: str

class TokenRefreshRequest(BaseModel):
    """
    Request schema for token refresh.
    """
    refresh_token: str

@router.post("/google", response_model=AuthResponse)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth credential (ID token).
    """
    service = AuthService(db)
    return service.authenticate_google_user(payload.credential)

@router.post("/signup", response_model=AuthResponse)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    """
    service = AuthService(db)
    return service.register_user(user_data)

@router.post("/login", response_model=AuthResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    service = AuthService(db)
    return service.authenticate_user(user_data)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile."""
    service = AuthService(db)
    return service.get_current_user_profile(current_user)

@router.post("/refresh", response_model=AuthResponse)
def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """
    Refresh JWT token using refresh token.
    Note: This is a placeholder implementation.
    """
    # TODO: Implement refresh token logic
    raise HTTPException(status_code=501, detail="Token refresh not yet implemented")

@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token removal).
    Note: JWT tokens are stateless, so this is mainly for client-side cleanup.
    """
    return {"message": "Logged out successfully"}

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request password reset for a user.
    """
    service = AuthService(db)
    return service.request_password_reset(request.email)

@router.post("/reset-password")
def reset_password(request: PasswordReset, db: Session = Depends(get_db)):
    """
    Reset user password using reset token.
    """
    service = AuthService(db)
    return service.reset_password(request.token, request.new_password) 