"""
Pydantic schemas for child profile management API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional
from datetime import datetime


# Request schemas
class ChildProfileCreate(BaseModel):
    """Schema for creating a new child profile."""
    name: str = Field(..., min_length=1, max_length=100, description="Child's name")
    age: Optional[int] = Field(None, ge=3, le=25, description="Child's age")
    school_name: Optional[str] = Field(None, max_length=200, description="Child's school name")
    country_id: Optional[int] = Field(None, description="Country ID for curriculum")
    curricula_id: Optional[int] = Field(None, description="Curriculum ID")
    grade_level_id: Optional[int] = Field(None, description="Grade level ID")
    subjects: Optional[List[int]] = Field(None, description="List of subject IDs the child needs help with")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v and v.strip() == '':
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()


class ChildProfileUpdate(BaseModel):
    """Schema for updating a child profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Child's name")
    age: Optional[int] = Field(None, ge=3, le=25, description="Child's age")
    school_name: Optional[str] = Field(None, max_length=200, description="Child's school name")
    country_id: Optional[int] = Field(None, description="Country ID for curriculum")
    curricula_id: Optional[int] = Field(None, description="Curriculum ID")
    grade_level_id: Optional[int] = Field(None, description="Grade level ID")
    subjects: Optional[List[int]] = Field(None, description="List of subject IDs the child needs help with")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip() if v else v


# Response schemas
class ChildProfileResponse(BaseModel):
    """Schema for child profile response data."""
    child_id: int
    parent_id: int
    name: str
    age: Optional[int] = None
    school_name: Optional[str] = None
    country_id: Optional[int] = None
    country_name: Optional[str] = None
    curricula_id: Optional[int] = None
    curricula_title: Optional[str] = None
    grade_level_id: Optional[int] = None
    grade_level_name: Optional[str] = None
    subjects: Optional[List[int]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChildProfileListResponse(BaseModel):
    """Schema for listing child profiles."""
    children: List[ChildProfileResponse]
    total: int


# Parent Guide schemas
class ParentGuideResponse(BaseModel):
    """Schema for parent guide response data."""
    guide_id: int
    child_id: int
    topic_id: int
    topic_title: Optional[str] = None
    subject_name: Optional[str] = None
    ai_generated_content: Optional[str] = None
    user_edited_content: Optional[str] = None
    is_bookmarked: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ParentGuideListResponse(BaseModel):
    """Schema for listing parent guides."""
    guides: List[ParentGuideResponse]
    total: int
