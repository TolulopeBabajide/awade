"""
Pydantic schemas for curriculum structure API endpoints.
"""

from pydantic import BaseModel, ConfigDict


class CurriculumStructureCreate(BaseModel):
    """Schema for creating a new curriculum structure."""
    curricula_id: int
    grade_level_id: int
    subject_id: int


class CurriculumStructureResponse(BaseModel):
    """Schema for curriculum structure response data."""
    curriculum_structure_id: int
    curricula_id: int
    grade_level_id: int
    subject_id: int
    model_config = ConfigDict(from_attributes=True)
