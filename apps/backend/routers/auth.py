"""
Authentication Router for Awade API

This module provides authentication endpoints for the Awade platform, including Google OAuth, email/password signup, login, and password reset functionality. It handles JWT token issuance and user management for secure access to the API.

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
from apps.backend.models import User, UserRole
from apps.backend.dependencies import get_current_user, get_jwt_secret_key, get_jwt_algorithm
import requests
import os
import jwt
from datetime import datetime, timedelta
import bcrypt
import secrets
import json

# In-memory token store for demo (replace with DB/Redis in production)
reset_tokens = {}

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

def get_google_client_id() -> str:
    """Get Google OAuth client ID from environment variables."""
    return os.getenv("GOOGLE_CLIENT_ID", "")

def get_jwt_expires_minutes() -> int:
    """Get JWT expiration time from environment variables."""
    return int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

def get_password_min_length() -> int:
    """Get minimum password length from environment variables."""
    return int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

@router.post("/google", response_model=AuthResponse)
def google_auth(
    payload: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth credential (ID token).
    """
    GOOGLE_CLIENT_ID = get_google_client_id()
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID environment variable."
        )
    
    JWT_SECRET_KEY = get_jwt_secret_key()
    JWT_EXPIRES_MINUTES = get_jwt_expires_minutes()
    id_token = payload.credential

    # Verify the token with Google
    google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
    resp = requests.get(google_verify_url)
    if resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    google_data = resp.json()

    # Check audience
    if google_data.get("aud") != GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Invalid Google client ID")

    # Extract user info
    email = google_data.get("email")
    full_name = google_data.get("name")
    if not email:
        raise HTTPException(status_code=400, detail="Google account missing email")

    # Lookup or create user in DB
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            password_hash="google-oauth",  # Not used for Google users
            full_name=full_name or email,
            role=UserRole.EDUCATOR,
            country="",
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

    # Generate JWT token
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=get_jwt_algorithm())

    # Parse JSON strings back to lists for response
    subjects_list = json.loads(user.subjects) if user.subjects else None
    grade_levels_list = json.loads(user.grade_levels) if user.grade_levels else None
    
    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        country=user.country,
        region=user.region,
        school_name=user.school_name,
        subjects=subjects_list,
        grade_levels=grade_levels_list,
        languages_spoken=user.languages_spoken,
        created_at=user.created_at,
        last_login=user.last_login
    )
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@router.post("/signup", response_model=AuthResponse)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password.
    """
    JWT_SECRET_KEY = get_jwt_secret_key()
    JWT_EXPIRES_MINUTES = get_jwt_expires_minutes()
    PASSWORD_MIN_LENGTH = get_password_min_length()

    # Validate password length
    if len(user_data.password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        )

    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), salt).decode('utf-8')

    # Create user
    user = User(
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        role=user_data.role,
        country=user_data.country,
        region=user_data.region,
        school_name=user_data.school_name,
        subjects=json.dumps(user_data.subjects) if user_data.subjects else None,
        grade_levels=json.dumps(user_data.grade_levels) if user_data.grade_levels else None,
        languages_spoken=user_data.languages_spoken,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT token
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=get_jwt_algorithm())

    # Parse JSON strings back to lists for response
    subjects_list = json.loads(user.subjects) if user.subjects else None
    grade_levels_list = json.loads(user.grade_levels) if user.grade_levels else None
    
    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        country=user.country,
        region=user.region,
        school_name=user.school_name,
        subjects=subjects_list,
        grade_levels=grade_levels_list,
        languages_spoken=user.languages_spoken,
        created_at=user.created_at,
        last_login=user.last_login
    )
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@router.post("/login", response_model=AuthResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email and password.
    """
    JWT_SECRET_KEY = get_jwt_secret_key()
    JWT_EXPIRES_MINUTES = get_jwt_expires_minutes()

    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is Google OAuth user
    if user.password_hash == "google-oauth":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please use Google OAuth to login with this account",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Generate JWT token
    payload = {
        "sub": str(user.user_id),
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MINUTES)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=get_jwt_algorithm())

    # Parse JSON strings back to lists for response
    try:
        subjects_list = json.loads(user.subjects) if user.subjects else None
    except (json.JSONDecodeError, TypeError):
        subjects_list = None
    
    try:
        grade_levels_list = json.loads(user.grade_levels) if user.grade_levels else None
    except (json.JSONDecodeError, TypeError):
        grade_levels_list = None
    
    user_response = UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        country=user.country,
        region=user.region,
        school_name=user.school_name,
        subjects=subjects_list,
        grade_levels=grade_levels_list,
        languages_spoken=user.languages_spoken,
        created_at=user.created_at,
        last_login=user.last_login
    )
    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=user_response
    )

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    """
    # Parse JSON strings back to lists for response
    try:
        subjects_list = json.loads(current_user.subjects) if current_user.subjects else None
    except (json.JSONDecodeError, TypeError):
        subjects_list = None
    
    try:
        grade_levels_list = json.loads(current_user.grade_levels) if current_user.grade_levels else None
    except (json.JSONDecodeError, TypeError):
        grade_levels_list = None
    
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        country=current_user.country,
        region=current_user.region,
        school_name=current_user.school_name,
        subjects=subjects_list,
        grade_levels=grade_levels_list,
        languages_spoken=current_user.languages_spoken,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token removal).
    In a more sophisticated setup, you might want to blacklist tokens.
    """
    return {"message": "Successfully logged out"}

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Handle password reset requests by generating a reset token and (in production) sending a reset link to the user's email.

    Args:
        request (PasswordResetRequest): The password reset request containing the user's email.
        db (Session): Database session dependency.

    Returns:
        dict: Message indicating whether a reset link was sent.
    """
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # For security, do not reveal if user exists
        return {"message": "If the email exists, a reset link has been sent."}
    
    # Check if user is Google OAuth user
    if user.password_hash == "google-oauth":
        return {"message": "Google OAuth users cannot reset password via email."}
    
    # Generate token
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = user.email
    
    # TODO: Send email with reset link (e.g., https://yourdomain.com/reset-password?token=...)
    print(f"[DEBUG] Password reset link: https://yourdomain.com/reset-password?token={token}")
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(request: PasswordReset, db: Session = Depends(get_db)):
    """
    Reset a user's password using a valid reset token.

    Args:
        request (PasswordReset): The password reset request containing the token and new password.
        db (Session): Database session dependency.

    Returns:
        dict: Message indicating whether the password was reset successfully.
    """
    PASSWORD_MIN_LENGTH = get_password_min_length()
    
    # Validate password length
    if len(request.new_password) < PASSWORD_MIN_LENGTH:
        raise HTTPException(
            status_code=400, 
            detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        )
    
    email = reset_tokens.get(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is Google OAuth user
    if user.password_hash == "google-oauth":
        raise HTTPException(status_code=400, detail="Google OAuth users cannot reset password via email.")
    
    # Hash new password
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(request.new_password.encode('utf-8'), salt).decode('utf-8')
    user.password_hash = password_hash
    db.commit()
    
    # Remove token after use
    del reset_tokens[request.token]
    return {"message": "Password has been reset successfully."} 