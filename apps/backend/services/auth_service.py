"""
Authentication Service for Awade

This module provides service methods for user authentication, including Google OAuth,
email/password signup, login, and password reset functionality. It handles all business
logic related to authentication, separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import secrets
import hashlib
import json
import logging
import requests
import os
from fastapi import HTTPException, status
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

from apps.backend.models import User, UserRole
from apps.backend.schemas.users import AuthResponse, UserResponse, UserCreate, UserLogin, PasswordResetRequest, PasswordReset
from apps.backend.dependencies import get_jwt_secret_key, get_jwt_algorithm

# Roles that users may request at self-registration (email/password or OAuth).
# ADMIN and SUPER_ADMIN are excluded — those roles must be assigned by an admin.
# Using frozenset to prevent accidental mutation.
_SELF_REGISTERABLE_ROLES: frozenset = frozenset({UserRole.PARENT, UserRole.EDUCATOR})

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
        return os.getenv("GOOGLE_CLIENT_ID", "")

    def get_jwt_expires_minutes(self) -> int:
        """Get JWT expiration time from environment variables."""
        return int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

    def get_password_min_length(self) -> int:
        """Get minimum password length from environment variables."""
        return int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def create_access_token(self, data: dict) -> str:
        """
        Create a new access token (JWT).
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.get_jwt_expires_minutes())
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, get_jwt_secret_key(), algorithm=get_jwt_algorithm())

    def create_refresh_token(self, data: dict) -> str:
        """
        Create a new refresh token (JWT) with a unique identifier (JTI).
        Longer expiration (e.g. 7 days).
        """
        to_encode = data.copy()
        # Refresh token valid for 7 days
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        # Add JTI to ensure uniqueness and for revocation tracking
        jti = secrets.token_urlsafe(16)
        to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
        return jwt.encode(to_encode, get_jwt_secret_key(), algorithm=get_jwt_algorithm())
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password (str): Plain text password
            hashed_password (str): Hashed password
            
        Returns:
            bool: True if password matches hash
        """
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def _build_token_payload(self, user: "User") -> dict:
        """Build the JWT token payload for a given user.

        Centralises the ``sub`` + ``email`` payload construction so that
        adding a new claim (e.g. ``role``) requires a single edit here
        instead of four scattered inline dicts.

        Args:
            user: The authenticated :class:`User` ORM instance.

        Returns:
            dict: Payload dict ready to pass to :meth:`create_access_token`
                  or :meth:`create_refresh_token`.
        """
        return {"sub": str(user.user_id), "email": user.email}

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
            logger.warning("Google OAuth is not available: GOOGLE_CLIENT_ID is not set")
            raise HTTPException(
                status_code=500,
                detail="Google OAuth is not available. Please contact support."
            )
        
        # Verify the token with Google
        google_verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        try:
            resp = requests.get(google_verify_url, timeout=10)
        except requests.exceptions.Timeout:
            logger.warning("Google tokeninfo request timed out")
            raise HTTPException(
                status_code=503,
                detail="Google OAuth temporarily unavailable. Please try again."
            )
        if resp.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        google_data = resp.json()
        
        # Check audience
        if google_data.get("aud") != GOOGLE_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid Google client ID")
        
        return google_data
    
    def authenticate_google_user(self, id_token: str, requested_role: str = "PARENT") -> Tuple[AuthResponse, str]:
        """
        Authenticate user with Google OAuth.
        
        Args:
            id_token (str): Google ID token
            
        Returns:
            Tuple[AuthResponse, str]: Authentication response and refresh token
            
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
                # Whitelist only PARENT and EDUCATOR — coerce anything else (including
                # ADMIN / SUPER_ADMIN) to PARENT so clients cannot self-elevate via OAuth.
                try:
                    candidate = UserRole(requested_role)
                    new_role = candidate if candidate in _SELF_REGISTERABLE_ROLES else UserRole.PARENT
                except (ValueError, KeyError):
                    new_role = UserRole.PARENT

                user = User(
                    email=email,
                    password_hash="google-oauth",  # Not used for Google users
                    full_name=full_name or email,
                    role=new_role,
                    country="",
                    created_at=datetime.now(timezone.utc)
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
            else:
                user.last_login = datetime.now(timezone.utc)
                self.db.commit()
                self.db.refresh(user)
            
            # Generate JWT tokens
            token_payload = self._build_token_payload(user)
            token = self.create_access_token(token_payload)
            refresh_token = self.create_refresh_token(token_payload)
            
            # Delegate UserResponse construction to get_current_user_profile() — single
            # source of truth for JSON parsing (AWD-M-98)
            user_response = self.get_current_user_profile(user)

            return AuthResponse(
                access_token=token,
                token_type="bearer",
                user=user_response
            ), refresh_token

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error during Google authentication: %s", e, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred during Google authentication"
            )
    
    def register_user(self, user_data: UserCreate) -> Tuple[AuthResponse, str]:
        """
        Register a new user with email and password.
        
        Args:
            user_data (UserCreate): User registration data
            
        Returns:
            Tuple[AuthResponse, str]: Authentication response and refresh token
            
        Raises:
            HTTPException: If registration fails
        """
        try:
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

            # Hash password — delegate to _hash_password() to avoid divergent bcrypt paths
            password_hash = self._hash_password(user_data.password)
            
            # Whitelist only PARENT and EDUCATOR — coerce anything else (including
            # ADMIN / SUPER_ADMIN) to PARENT so clients cannot self-elevate at registration.
            safe_role = user_data.role if user_data.role in _SELF_REGISTERABLE_ROLES else UserRole.PARENT

            # Create user
            user = User(
                email=user_data.email,
                password_hash=password_hash,
                full_name=user_data.full_name,
                role=safe_role,
                country=user_data.country,
                region=user_data.region,
                school_name=user_data.school_name,
                subjects=json.dumps(user_data.subjects) if user_data.subjects else None,
                grade_levels=json.dumps(user_data.grade_levels) if user_data.grade_levels else None,
                languages_spoken=user_data.languages_spoken,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            # Generate JWT tokens
            token_payload = self._build_token_payload(user)
            token = self.create_access_token(token_payload)
            refresh_token = self.create_refresh_token(token_payload)
            
            # Delegate UserResponse construction to get_current_user_profile() — single
            # source of truth for JSON parsing (AWD-M-98)
            user_response = self.get_current_user_profile(user)

            return AuthResponse(
                access_token=token,
                token_type="bearer",
                user=user_response
            ), refresh_token

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error during user registration: %s", e, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred during user registration"
            )
    
    
    async def refresh_access_token(self, refresh_token: str, redis_pool: Optional[Any] = None) -> Tuple[AuthResponse, str]:
        """
        Refresh access token using a valid refresh token and rotate the refresh token.
        
        Args:
            refresh_token (str): The refresh token
            redis_pool (Optional[Any]): Redis pool for blacklist check
            
        Returns:
            Tuple[AuthResponse, str]: New access token and user data, plus new refresh token
        """
        try:
            # Verify token
            payload = jwt.decode(refresh_token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])
            
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")
                
            # Check blacklist
            if await self.is_refresh_token_blacklisted(refresh_token, redis_pool):
                raise HTTPException(status_code=401, detail="Token has been revoked")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")
                
            # Get user
            user = self.db.query(User).filter(User.user_id == int(user_id)).first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token")
                
            # Generate new tokens
            token_payload = self._build_token_payload(user)
            new_access_token = self.create_access_token(token_payload)
            new_refresh_token = self.create_refresh_token(token_payload)
            
            # Retrieve user profile for response
            user_response = self.get_current_user_profile(user)
            
            return AuthResponse(
                access_token=new_access_token,
                token_type="bearer",
                user=user_response
            ), new_refresh_token
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            logger.error("Unexpected error during token refresh: %s", e, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred during token refresh"
            )

    def authenticate_user(self, user_data: UserLogin) -> Tuple[AuthResponse, str]:
        """
        Authenticate user with email and password.
        
        Args:
            user_data (UserLogin): User login credentials
            
        Returns:
            Tuple[AuthResponse, str]: Authentication response and refresh token
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Find user by email
            user = self.db.query(User).filter(User.email == user_data.email).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Check if user is Google OAuth user — use generic message to prevent
            # account enumeration (revealing that an email is registered via OAuth)
            if user.password_hash == "google-oauth":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Verify password — delegate to _verify_password() to keep a single bcrypt path (AWD-M-107)
            if not self._verify_password(user_data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(user)
            
            # Generate JWT tokens
            token_payload = self._build_token_payload(user)
            token = self.create_access_token(token_payload)
            refresh_token = self.create_refresh_token(token_payload)
            
            # Delegate UserResponse construction to get_current_user_profile() — single
            # source of truth for JSON parsing (AWD-M-98)
            user_response = self.get_current_user_profile(user)

            return AuthResponse(
                access_token=token,
                token_type="bearer",
                user=user_response
            ), refresh_token

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error during authentication: %s", e, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred during authentication"
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
            logger.error("Unexpected error while retrieving user profile: %s", e, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving user profile"
            )
    
    @staticmethod
    def _hash_reset_token(raw_token: str) -> str:
        """Return the SHA-256 hex digest of a raw reset token for safe DB storage."""
        return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

    def request_password_reset(self, email: str) -> Dict[str, str]:
        """
        Request a password reset for the given email address.

        Generates a cryptographically random token, stores its SHA-256 hash on the
        user record with a 1-hour expiry, and (when email is wired up) would dispatch
        a reset link containing the raw token.

        The response is intentionally identical for existing and non-existing emails
        so that callers cannot enumerate registered accounts (OWASP A07).

        Args:
            email: Email address submitted by the user.

        Returns:
            Dict with a generic success message (enumeration-safe).
        """
        _ENUM_SAFE_RESPONSE = {"message": "If the email exists, a password reset link has been sent"}
        try:
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                return _ENUM_SAFE_RESPONSE

            # Generate a URL-safe random token (256 bits of entropy).
            raw_token = secrets.token_urlsafe(32)

            # Store the SHA-256 hash — the raw token is never persisted.
            user.password_reset_token = self._hash_reset_token(raw_token)
            user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
            self.db.commit()

            # TODO(AWD-H-68): send email with reset link once email layer is wired up.
            # The reset URL should be: {FRONTEND_URL}/reset-password?token={raw_token}
            # Do NOT log raw_token — it is a credential.
            logger.info("Password reset token generated for user_id=%s", user.user_id)

            return _ENUM_SAFE_RESPONSE

        except Exception as e:
            self.db.rollback()
            logger.error("Unexpected error while requesting password reset", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while requesting password reset"
            )

    def reset_password(self, token: str, new_password: str) -> Dict[str, str]:
        """
        Reset the password for the user identified by the given reset token.

        Validates:
        - Token exists in the DB (matched by SHA-256 hash).
        - Token has not expired.
        - New password passes the configured length / byte-size constraints
          (the PasswordReset Pydantic schema already validates these at the HTTP layer,
           but we re-check here as a defence-in-depth measure).

        On success clears the token columns to prevent replay attacks.

        Args:
            token: Raw reset token from the email link.
            new_password: Plaintext new password (pre-validated by Pydantic schema).

        Returns:
            Dict with a success message.

        Raises:
            HTTPException 400: Token is invalid or expired.
            HTTPException 500: Unexpected DB / hashing failure.
        """
        try:
            token_hash = self._hash_reset_token(token)
            now = datetime.now(timezone.utc)

            user = (
                self.db.query(User)
                .filter(
                    User.password_reset_token == token_hash,
                    User.password_reset_expires > now,
                )
                .first()
            )

            if user is None:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid or expired reset token"
                )

            # Hash and store the new password, respecting bcrypt's 72-byte cap (AWD-M-72).
            user.password_hash = self._hash_password(new_password)

            # Clear token fields to prevent replay.
            user.password_reset_token = None
            user.password_reset_expires = None

            self.db.commit()
            logger.info("Password reset completed for user_id=%s", user.user_id)

            return {"message": "Password reset successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Unexpected error while resetting password", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while resetting password"
            )
    async def blacklist_refresh_token(self, refresh_token: str, redis_pool: Any):
        """
        Blacklist a refresh token in Redis until it expires using its JTI.
        """
        try:
            # Decode to get expiration and jti
            payload = jwt.decode(refresh_token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])
            jti = payload.get("jti")
            exp = payload.get("exp")
            if not jti or not exp:
                return
            
            # Calculate TTL
            ttl = int(exp - datetime.now(timezone.utc).timestamp())
            if ttl <= 0:
                return
            
            # Store in Redis with TTL
            key = f"blacklist:{jti}"
            await redis_pool.setex(key, ttl, "true")
            
        except Exception as e:
            # Log error but don't fail logout
            logger.error("Error blacklisting token: %s", e, exc_info=True)

    async def is_refresh_token_blacklisted(self, refresh_token: str, redis_pool: Any) -> bool:
        """
        Check if a refresh token's JTI is blacklisted in Redis.

        Degraded mode: when redis_pool is None (Redis unavailable), the blacklist check
        is skipped and the token is treated as valid.  This is a fail-open trade-off —
        logged as a WARNING so the nightly-monitor surfaces the outage.  See
        docs/agentic/mcp-circuit-breaker-policy.md §auth-service for the policy rationale.
        """
        if not redis_pool:
            logger.warning(
                "Redis unavailable — refresh token blacklist check skipped; "
                "revoked tokens may be reusable until Redis recovers (AWD-M-102)"
            )
            return False
            
        try:
            # Decode to get jti
            payload = jwt.decode(refresh_token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])
            jti = payload.get("jti")
            if not jti:
                return False
                
            key = f"blacklist:{jti}"
            return await redis_pool.exists(key)
        except Exception as e:
            logger.warning("Error checking refresh token blacklist: %s", e, exc_info=True)
            return False
