"""
Pydantic schemas for user management API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum
import os

class UserRole(str, Enum):
    """Enumeration of user roles in the system."""
    EDUCATOR = "EDUCATOR"
    PARENT = "PARENT"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"

def get_password_min_length() -> int:
    """Get minimum password length from environment variables."""
    return int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

_BCRYPT_MAX_BYTES = 72  # bcrypt 4.3.0 hard limit (truncate_error=True)

# Common passwords rejected at registration and reset time (AWD-M-92).
# Single source of truth — do not duplicate in validators.
_WEAK_PASSWORDS: frozenset = frozenset(
    {'password', '123456', 'qwerty', 'admin', 'letmein'}
)


def _validate_password_byte_length(v: str, max_bytes: int) -> None:
    """Raise ValueError if *v* exceeds *max_bytes* UTF-8 bytes.

    bcrypt 4.3.0 raises ValueError for passwords > 72 bytes
    (truncate_error=True by default).  Calling this helper before hashpw /
    checkpw converts that crash into a clean HTTP 422 for the caller.

    Args:
        v:         The raw password string.
        max_bytes: Byte ceiling (typically from get_password_max_length()).

    Raises:
        ValueError: When the encoded length exceeds *max_bytes*.
    """
    if len(v.encode('utf-8')) > max_bytes:
        raise ValueError(
            f'Password is too long (exceeds the {max_bytes}-byte limit). '
            'Please use a shorter password.'
        )


def _validate_weak_password(v: str) -> None:
    """Raise ValueError if *v* appears in the common-password denylist.

    Args:
        v: The raw password string (case-insensitive comparison).

    Raises:
        ValueError: When the password is on the denylist.
    """
    if v.lower() in _WEAK_PASSWORDS:
        raise ValueError('Password is too common. Please choose a stronger password.')


def get_password_max_length() -> int:
    """Get maximum password length from environment variables.

    The return value is hard-capped at 72 — the maximum byte length accepted by
    bcrypt 4.3.0 (truncate_error=True by default).  Even if PASSWORD_MAX_LENGTH
    is set above 72 (e.g. 128), this function returns 72 so that validators
    never pass a password that would crash hashpw()/checkpw() with ValueError
    (which previously bubbled up as HTTP 500 before AWD-M-72 was fixed).

    Use PASSWORD_MAX_LENGTH only to enforce a *stricter* (lower) cap; values
    above 72 are silently clamped to 72 (AWD-H-70).
    """
    configured = int(os.getenv("PASSWORD_MAX_LENGTH", str(_BCRYPT_MAX_BYTES)))
    return min(configured, _BCRYPT_MAX_BYTES)

# Request schemas
class UserCreate(BaseModel):
    """Schema for creating a new user account."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    full_name: str = Field(..., description="User's full name")
    role: UserRole = Field(UserRole.EDUCATOR, description="User role")
    country: str = Field(..., description="User's country")
    region: Optional[str] = Field(None, description="User's region/state")
    school_name: Optional[str] = Field(None, description="User's school name")
    subjects: Optional[List[str]] = Field(None, description="List of subjects taught")
    grade_levels: Optional[List[str]] = Field(None, description="List of grade levels taught")
    languages_spoken: Optional[str] = Field(None, description="Comma-separated list of languages spoken")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        min_length = get_password_min_length()
        max_bytes = get_password_max_length()

        if len(v) < min_length:
            raise ValueError(f'Password must be at least {min_length} characters long')
        # Use UTF-8 byte length to match bcrypt's hard limit (AWD-M-72).
        # A multi-byte password can exceed 72 bytes with far fewer than 72 chars.
        _validate_password_byte_length(v, max_bytes)
        _validate_weak_password(v)

        return v

class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    full_name: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    school_name: Optional[str] = None
    subjects: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None
    languages_spoken: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    @field_validator('password')
    @classmethod
    def validate_password_bytes(cls, v: str) -> str:
        """Reject passwords that exceed the configured byte limit.

        bcrypt 4.3.0 raises ValueError for passwords > 72 bytes (truncate_error=True
        by default).  Without this guard, authenticate_user() would catch the
        ValueError in its bare ``except Exception`` block and return HTTP 500
        instead of a user-friendly 422.

        Uses get_password_max_length() so that a lower PASSWORD_MAX_LENGTH env var
        (e.g. 64) is enforced consistently at login as well as registration (AWD-M-91).
        """
        max_bytes = get_password_max_length()
        _validate_password_byte_length(v, max_bytes)
        return v

# Response schemas
class UserResponse(BaseModel):
    """Schema for user response data."""
    user_id: int
    email: str
    full_name: str
    role: UserRole
    country: Optional[str] = None
    region: Optional[str] = None
    school_name: Optional[str] = None
    subjects: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None
    languages_spoken: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserProfileResponse(BaseModel):
    """Simplified user profile for public display"""
    user_id: int
    full_name: str
    country: Optional[str] = None
    region: Optional[str] = None
    school_name: Optional[str] = None
    subjects: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class AuthResponse(BaseModel):
    """Schema for authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class CookieAuthResponse(BaseModel):
    """Schema for cookie-based authentication response.

    The access token is delivered via HttpOnly Set-Cookie header; only the
    user payload is included in the response body so the frontend never needs
    to touch or store the raw JWT.
    """
    token_type: str = "bearer"
    user: UserResponse

class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address for password reset")

class PasswordReset(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password")

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        min_length = get_password_min_length()
        max_bytes = get_password_max_length()

        if len(v) < min_length:
            raise ValueError(f'Password must be at least {min_length} characters long')
        # Use UTF-8 byte length to match bcrypt's hard limit (AWD-M-72).
        _validate_password_byte_length(v, max_bytes)
        _validate_weak_password(v)

        return v
