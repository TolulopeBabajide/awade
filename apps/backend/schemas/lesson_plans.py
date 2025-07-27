"""
Pydantic schemas for lesson plan API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class LessonStatus(str, Enum):
    """Enumeration of lesson plan status values."""
    DRAFT = "draft"
    EDITED = "edited"
    REVIEWED = "reviewed"
    EXPORTED = "exported"
    ARCHIVED = "archived"

class ResourceType(str, Enum):
    """Enumeration of resource file types."""
    PDF = "pdf"
    DOCX = "docx"

# Request schemas
class LessonPlanCreate(BaseModel):
    """Schema for creating a new lesson plan."""
    subject: str = Field(..., description="Subject area (e.g., Mathematics, Science)")
    grade_level: str = Field(..., description="Grade level (e.g., Grade 4, Grade 7)")
    topic: str = Field(..., description="Specific topic within the subject (e.g., Fractions, Photosynthesis)")
    user_id: int = Field(..., description="User ID of the lesson plan author")

class LessonPlanUpdate(BaseModel):
    """Schema for updating an existing lesson plan."""
    title: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[LessonStatus] = None    
    learning_objectives: Optional[str] = None
    topic_content: Optional[str] = None

# Response schemas
class LessonPlanResponse(BaseModel):
    """Schema for lesson plan response data."""
    lesson_id: int
    title: str
    subject: str
    grade_level: str
    topic: Optional[str] = None
    author_id: int
    duration_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    status: LessonStatus
    curriculum_learning_objectives: Optional[List[str]] = None
    curriculum_contents: Optional[List[str]] = None
    
    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True

# LessonResource schemas
class LessonResourceCreate(BaseModel):
    """Schema for creating lesson resources."""
    lesson_plan_id: int
    user_id: int
    context_input: Optional[str] = None

class LessonResourceUpdate(BaseModel):
    """Schema for updating lesson resources."""
    user_edited_content: str

class LessonResourceResponse(BaseModel):
    """Schema for lesson resource response data."""
    lesson_resources_id: int
    lesson_plan_id: int
    user_id: int
    context_input: Optional[str] = None
    ai_generated_content: Optional[str] = None
    user_edited_content: Optional[str] = None
    export_format: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True 