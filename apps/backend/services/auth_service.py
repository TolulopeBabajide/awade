"""
Authentication Service for Awade

This module provides service methods for user authentication, including Google OAuth,
email/password signup, login, and password reset functionality. It handles all business
logic related to authentication, separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets
import json
import requests
from fastapi import HTTPException, status

from apps.backend.models import User, UserRole
from apps.backend.schemas.users import AuthResponse, UserResponse, UserCreate, UserLogin, PasswordResetRequest, PasswordReset
from apps.backend.dependencies import get_jwt_secret_key, get_jwt_algorithm

class AuthService:
    """Service class for authentication operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the AuthService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def get_google_client_id(self) -> str:
        """Get Google OAuth client ID from environment variables."""
        import os
        return os.getenv("GOOGLE_CLIENT_ID", "")
    
    def get_jwt_expires_minutes(self) -> int:
        """Get JWT expiration time from environment variables."""
        import os
        return int(os.getenv("JWT_EXPIRES_MINUTES", "60"))
    
    def get_password_min_length(self) -> int:
        """Get minimum password length from environment variables."""
        import os
        return int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    
    def verify_google_token(self, id_token: str) -> Dict[str, Any]:
        """
        Verify Google OAuth ID token.
        
        Args:
            id_token (str): Google ID token
            
        Returns:
            Dict[str, Any]: Verified token data
            
        Raises:
            HTTPException: If token verification fails
        """
        GOOGLE_CLIENT_ID = self.get_google_client_id()
        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=500, 
                detail="Google OAuth is not configured. Please set GOOGLE_CLIENT_ID environment variable."
            )
        
        # Verify the token with Google
        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        resp = requests.get(google_verify_url)
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        google_data = resp.json()
        
        # Check audience
        if google_data.get("aud") != GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid Google client ID")
        
        return google_data
    
    def authenticate_google_user(self, id_token: str) -> AuthResponse:
        """
        Authenticate user with Google OAuth.
        
        Args:
            id_token (str): Google ID token
            
        Returns:
            AuthResponse: Authentication response with JWT token and user data
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Verify Google token
            google_data = self.verify_google_token(id_token)
            
            # Extract user info
            email = google_data.get("email")
            full_name = google_data.get("name")
            if not email:
                raise HTTPException(status_code=400, detail="Google account missing email")
            
            # Lookup or create user in DB
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    password_hash="google-oauth",  # Not used for Google users
                    full_name=full_name or email,
                    role=UserRole.EDUCATOR,
                    country="",
                    created_at=datetime.utcnow()
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            else:
                user.last_login = datetime.utcnow()
                self.db.commit()
                self.db.refresh(user)
            
            # Generate JWT token
            JWT_SECRET_KEY = get_jwt_secret_key()
            JWT_EXPIRES_MINUTES = self.get_jwt_expires_minutes()
            
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
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred during Google authentication: {str(e)}"
            )
    
    def register_user(self, user_data: UserCreate) -> AuthResponse:
        """
        Register a new user with email and password.
        
        Args:
            user_data (UserCreate): User registration data
            
        Returns:
            AuthResponse: Authentication response with JWT token and user data
            
        Raises:
            HTTPException: If registration fails
        """
        try:
            JWT_SECRET_KEY = get_jwt_secret_key()
            JWT_EXPIRES_MINUTES = self.get_jwt_expires_minutes()
            PASSWORD_MIN_LENGTH = self.get_password_min_length()
            
            # Validate password length
            if len(user_data.password) < PASSWORD_MIN_LENGTH:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
                )
            
            # Check if user already exists
            if self.db.query(User).filter(User.email == user_data.email).first():
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
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
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
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred during user registration: {str(e)}"
            )
    
    def authenticate_user(self, user_data: UserLogin) -> AuthResponse:
        """
        Authenticate user with email and password.
        
        Args:
            user_data (UserLogin): User login credentials
            
        Returns:
            AuthResponse: Authentication response with JWT token and user data
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            JWT_SECRET_KEY = get_jwt_secret_key()
            JWT_EXPIRES_MINUTES = self.get_jwt_expires_minutes()
            
            # Find user by email
            user = self.db.query(User).filter(User.email == user_data.email).first()
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
            
            # Verify password with bcrypt
            if not bcrypt.checkpw(user_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Update last login
            user.last_login = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
            
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
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred during authentication: {str(e)}"
            )
    
    def get_current_user_profile(self, current_user: User) -> UserResponse:
        """
        Get current user profile.
        
        Args:
            current_user (User): Current authenticated user
            
        Returns:
            UserResponse: User profile data
        """
        try:
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
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving user profile: {str(e)}"
            )
    
    def request_password_reset(self, email: str) -> Dict[str, str]:
        """
        Request password reset for a user.
        
        Args:
            email (str): User's email address
            
        Returns:
            Dict[str, str]: Success message
            
        Raises:
            HTTPException: If request fails
        """
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                # Don't reveal if email exists or not for security
                return {"message": "If the email exists, a password reset link has been sent"}
            
            # Generate reset token (in-memory for demo, use DB/Redis in production)
            reset_token = secrets.token_urlsafe(32)
            # In production, store this token in database with expiration
            
            # Send email with reset link (placeholder)
            # In production, implement actual email sending
            
            return {"message": "If the email exists, a password reset link has been sent"}
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while requesting password reset: {str(e)}"
            )
    
    def reset_password(self, token: str, new_password: str) -> Dict[str, str]:
        """
        Reset user password using reset token.
        
        Args:
            token (str): Password reset token
            new_password (str): New password
            
        Returns:
            Dict[str, str]: Success message
            
        Raises:
            HTTPException: If reset fails
        """
        try:
            # Validate password length
            PASSWORD_MIN_LENGTH = self.get_password_min_length()
            if len(new_password) < PASSWORD_MIN_LENGTH:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
                )
            
            # In production, validate token from database and get user
            # For demo purposes, we'll just return success
            # In production: verify token, find user, update password
            
            return {"message": "Password reset successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while resetting password: {str(e)}"
            )
