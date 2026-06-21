"""
Pydantic schemas for lesson plan API endpoints.
"""

from pydantic import BaseModel, Field, ConfigDict, Json
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


class ExportFormatRequest(BaseModel):
    format: ResourceType = ResourceType.PDF


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
    
    model_config = ConfigDict(from_attributes=True)

# LessonResource schemas
class LessonResourceCreate(BaseModel):
    """Schema for creating lesson resources."""
    lesson_plan_id: int
    context_input: Optional[str] = None
    export_format: Optional[str] = None

class LessonResourceUpdate(BaseModel):
    """Schema for updating lesson resources."""
    user_edited_content: str
    status: Optional[str] = None

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

    model_config = ConfigDict(from_attributes=True)


# AI-output validation schemas (AWD-M-48)

class LessonResourceTitleHeader(BaseModel):
    """Sub-schema for the title_header field in AI-generated lesson resource content."""
    topic: str
    subject: str
    grade_level: str
    country: Optional[str] = None
    local_context: Optional[str] = None


class LessonResourceLessonContent(BaseModel):
    """Sub-schema for the lesson_content field in AI-generated lesson resource content."""
    introduction: str
    main_concepts: List[str]
    examples: Optional[List[str]] = None
    step_by_step_instructions: Optional[List[str]] = None


class LessonResourceAIContent(BaseModel):
    """
    Full Pydantic schema for AI-generated lesson resource content.

    Used to validate the JSON returned by AwadeGPTService.generate_lesson_resource()
    before the content is written to the database.  If validation fails the worker
    sets the resource status to 'failed' and creates a ResourceModeration entry
    rather than persisting malformed data that could cause downstream 503s in the
    PDF export service (OWASP LLM02 — insecure output handling).
    """
    title_header: LessonResourceTitleHeader
    learning_objectives: List[str]
    lesson_content: LessonResourceLessonContent
    assessment: Optional[List[str]] = None
    key_takeaways: Optional[List[str]] = None
    related_projects_or_activities: Optional[List[str]] = None
    references: Optional[List[str]] = None