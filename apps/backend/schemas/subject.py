"""
Subject schemas for Awade

This module defines Pydantic models for subject data validation and serialization.
It includes schemas for creating, updating, and responding with subject information.

Author: Tolulope Babajide
"""

from pydantic import BaseModel, Field
from typing import Optional

class SubjectBase(BaseModel):
    """Base subject schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Name of the subject")

class SubjectCreate(SubjectBase):
    """Schema for creating a new subject."""
    pass

class SubjectUpdate(BaseModel):
    """Schema for updating an existing subject."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Name of the subject")

class SubjectResponse(SubjectBase):
    """Schema for subject response."""
    subject_id: int = Field(..., description="Unique identifier for the subject")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "subject_id": 1,
                "name": "Mathematics"
            }
        }
