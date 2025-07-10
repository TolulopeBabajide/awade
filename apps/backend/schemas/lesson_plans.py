"""
Pydantic schemas for lesson plan API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class LessonStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class ResourceType(str, Enum):
    PDF = "pdf"
    VIDEO = "video"
    TOOL = "tool"
    EXTERNAL = "external"

# Request schemas
class LessonPlanCreate(BaseModel):
    subject: str = Field(..., description="Subject area (e.g., Mathematics, Science)")
    grade_level: str = Field(..., description="Grade level (e.g., Grade 4, Grade 7)")
    topic: str = Field(..., description="Specific topic within the subject (e.g., Fractions, Photosynthesis)")
    objectives: Optional[List[str]] = Field(None, description="Learning objectives (optional - AI will generate if not provided)")
    duration_minutes: int = Field(45, description="Lesson duration in minutes")
    local_context: Optional[str] = Field(None, description="Local context for the lesson (e.g., rural school, urban setting, available resources)")
    language: str = Field("en", description="Primary language for the lesson")
    cultural_context: Optional[str] = Field("African", description="Cultural context for adaptations")
    country: Optional[str] = Field(None, description="Country for curriculum mapping")
    author_id: int = Field(..., description="User ID of the lesson plan author")

class LessonPlanUpdate(BaseModel):
    title: Optional[str] = None
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    context_description: Optional[str] = None
    duration_minutes: Optional[int] = None
    status: Optional[LessonStatus] = None

class LessonContextCreate(BaseModel):
    context_key: str = Field(..., description="Context key (e.g., local_resources, student_background)")
    context_value: str = Field(..., description="Context value")

# Response schemas
class LessonPlanResponse(BaseModel):
    lesson_id: int
    title: str
    subject: str
    grade_level: str
    topic: Optional[str] = None
    author_id: int
    context_description: Optional[str]
    duration_minutes: int
    created_at: datetime
    updated_at: datetime
    status: LessonStatus
    
    class Config:
        from_attributes = True

class LessonPlanDetailResponse(BaseModel):
    lesson_id: int
    title: str
    subject: str
    grade_level: str
    topic: Optional[str] = None
    author_id: int
    context_description: Optional[str]
    duration_minutes: int
    created_at: datetime
    updated_at: datetime
    status: LessonStatus
    learning_objectives: Optional[str] = None
    local_context: Optional[str] = None
    core_content: Optional[str] = None
    activities: Optional[str] = None
    quiz: Optional[str] = None
    related_projects: Optional[str] = None
    
    class Config:
        from_attributes = True

class CurriculumMapResponse(BaseModel):
    curriculum_id: int
    subject: str
    grade_level: str
    curriculum_standard: str
    description: str
    country: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class LessonSectionResponse(BaseModel):
    section_id: int
    lesson_id: int
    section_title: str
    content_text: str
    media_link: Optional[str]
    order_number: int
    
    class Config:
        from_attributes = True

class ResourceLinkResponse(BaseModel):
    resource_id: int
    lesson_id: int
    link_url: str
    type: ResourceType
    description: Optional[str]
    
    class Config:
        from_attributes = True

class LessonContextResponse(BaseModel):
    context_id: int
    lesson_id: int
    context_key: str
    context_value: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Comprehensive lesson plan response with all related data
class LessonPlanFullResponse(BaseModel):
    lesson_plan: LessonPlanResponse
    sections: List[LessonSectionResponse]
    resources: List[ResourceLinkResponse]
    contexts: List[LessonContextResponse]
    curriculum: Optional[CurriculumMapResponse]
    
    class Config:
        from_attributes = True 