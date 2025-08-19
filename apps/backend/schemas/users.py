"""
Pydantic schemas for user management API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum
import os

class UserRole(str, Enum):
    """Enumeration of user roles in the system."""
    EDUCATOR = "EDUCATOR"
    ADMIN = "ADMIN"

def get_password_min_length() -> int:
    """Get minimum password length from environment variables."""
    return int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

def get_password_max_length() -> int:
    """Get maximum password length from environment variables."""
    return int(os.getenv("PASSWORD_MAX_LENGTH", "128"))

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

    @validator('password')
    def validate_password(cls, v):
        min_length = get_password_min_length()
        max_length = get_password_max_length()
        
        if len(v) < min_length:
            raise ValueError(f'Password must be at least {min_length} characters long')
        if len(v) > max_length:
            raise ValueError(f'Password must be no more than {max_length} characters long')
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password.')
        
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
    profile_image_url: Optional[str] = None
    profile_image_data: Optional[str] = None
    profile_image_type: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login credentials."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

# Response schemas
class UserResponse(BaseModel):
    """Schema for user response data."""
    user_id: int
    email: str
    full_name: str
    role: UserRole
    country: str
    region: Optional[str]
    school_name: Optional[str]
    subjects: Optional[List[str]]
    grade_levels: Optional[List[str]]
    languages_spoken: Optional[str]
    profile_image_url: Optional[str]
    profile_image_data: Optional[str]
    profile_image_type: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True

class UserProfileResponse(BaseModel):
    """Simplified user profile for public display"""
    user_id: int
    full_name: str
    country: str
    region: Optional[str]
    school_name: Optional[str]
    subjects: Optional[List[str]]
    grade_levels: Optional[List[str]]
    
    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True

class AuthResponse(BaseModel):
    """Schema for authentication response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""
    email: EmailStr = Field(..., description="Email address for password reset")

class PasswordReset(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password")

    @validator('new_password')
    def validate_new_password(cls, v):
        min_length = get_password_min_length()
        max_length = get_password_max_length()
        
        if len(v) < min_length:
            raise ValueError(f'Password must be at least {min_length} characters long')
        if len(v) > max_length:
            raise ValueError(f'Password must be no more than {max_length} characters long')
        
        # Check for common weak passwords
        weak_passwords = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password.')
        
        return v 