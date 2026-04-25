"""
Grade Level schemas for Awade

This module defines Pydantic models for grade level data validation and serialization.
It includes schemas for creating, updating, and responding with grade level information.

Author: Tolulope Babajide
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class GradeLevelBase(BaseModel):
    """Base grade level schema with common fields."""
    name: str = Field(..., min_length=1, max_length=50, description="Name of the grade level")

class GradeLevelCreate(GradeLevelBase):
    """Schema for creating a new grade level."""
    pass

class GradeLevelUpdate(BaseModel):
    """Schema for updating an existing grade level."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Name of the grade level")

class GradeLevelResponse(GradeLevelBase):
    """Schema for grade level response."""
    grade_level_id: int = Field(..., description="Unique identifier for the grade level")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "grade_level_id": 1,
                "name": "Grade 5"
            }
        }
    )
