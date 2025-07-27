"""
Pydantic schemas for user management API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """Enumeration of user roles in the system."""
    EDUCATOR = "educator"
    ADMIN = "admin"

# Request schemas
class UserCreate(BaseModel):
    """Schema for creating a new user account."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (minimum 8 characters)")
    full_name: str = Field(..., description="User's full name")
    role: UserRole = Field(UserRole.EDUCATOR, description="User role")
    country: str = Field(..., description="User's country")
    region: Optional[str] = Field(None, description="User's region/state")
    school_name: Optional[str] = Field(None, description="User's school name")
    subjects: Optional[List[str]] = Field(None, description="List of subjects taught")
    grade_levels: Optional[List[str]] = Field(None, description="List of grade levels taught")
    languages_spoken: Optional[str] = Field(None, description="Comma-separated list of languages spoken")

class UserUpdate(BaseModel):
    """Schema for updating user profile information."""
    full_name: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    school_name: Optional[str] = None
    subjects: Optional[List[str]] = None
    grade_levels: Optional[List[str]] = None
    languages_spoken: Optional[str] = None

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
    new_password: str = Field(..., min_length=8, description="New password (minimum 8 characters)") 