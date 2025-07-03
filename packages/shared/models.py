"""
Shared Pydantic models for Awade application.
These models are used across the backend and frontend.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    """Supported languages for the platform."""
    ENGLISH = "en"
    FRENCH = "fr"
    SWAHILI = "sw"
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"

class GradeLevel(str, Enum):
    """Supported grade levels."""
    GRADE_1 = "Grade 1"
    GRADE_2 = "Grade 2"
    GRADE_3 = "Grade 3"
    GRADE_4 = "Grade 4"
    GRADE_5 = "Grade 5"
    GRADE_6 = "Grade 6"
    GRADE_7 = "Grade 7"
    GRADE_8 = "Grade 8"
    GRADE_9 = "Grade 9"
    GRADE_10 = "Grade 10"
    GRADE_11 = "Grade 11"
    GRADE_12 = "Grade 12"

class Subject(str, Enum):
    """Supported subjects."""
    MATHEMATICS = "Mathematics"
    SCIENCE = "Science"
    ENGLISH = "English"
    HISTORY = "History"
    GEOGRAPHY = "Geography"
    CIVICS = "Civics"
    ART = "Art"
    MUSIC = "Music"
    PHYSICAL_EDUCATION = "Physical Education"
    TECHNOLOGY = "Technology"

class TrainingCategory(str, Enum):
    """Training module categories."""
    CLASSROOM_MANAGEMENT = "Classroom Management"
    PEDAGOGY = "Pedagogy"
    TECHNOLOGY_INTEGRATION = "Technology Integration"
    ASSESSMENT = "Assessment"
    CULTURAL_RELEVANCE = "Cultural Relevance"
    SPECIAL_NEEDS = "Special Needs"
    LEADERSHIP = "Leadership"

class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class LessonPlanRequest(BaseModel):
    """Request model for lesson plan generation."""
    subject: Subject = Field(..., description="Subject area")
    grade: GradeLevel = Field(..., description="Grade level")
    objectives: List[str] = Field(..., description="Learning objectives", min_items=1, max_items=5)
    duration: int = Field(45, description="Lesson duration in minutes", ge=15, le=120)
    language: Language = Field(Language.ENGLISH, description="Primary language")
    cultural_context: Optional[str] = Field(None, description="Cultural context for adaptations")

class LessonPlan(BaseModel):
    """Lesson plan model."""
    id: str = Field(..., description="Unique lesson plan ID")
    title: str = Field(..., description="Lesson plan title")
    subject: Subject = Field(..., description="Subject area")
    grade: GradeLevel = Field(..., description="Grade level")
    objectives: List[str] = Field(..., description="Learning objectives")
    activities: List[str] = Field(..., description="Lesson activities")
    materials: List[str] = Field(..., description="Required materials")
    assessment: str = Field(..., description="Assessment strategy")
    rationale: str = Field(..., description="Pedagogical rationale")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    language: Language = Field(Language.ENGLISH, description="Lesson language")
    is_offline: bool = Field(True, description="Whether available offline")
    ai_explanation: Optional[str] = Field(None, description="AI explanation of choices")

class TrainingModuleRequest(BaseModel):
    """Request model for training module generation."""
    topic: str = Field(..., description="Training topic")
    duration: int = Field(..., description="Module duration in minutes", ge=5, le=60)
    category: TrainingCategory = Field(..., description="Training category")
    language: Language = Field(Language.ENGLISH, description="Module language")
    audience: Optional[str] = Field("African teachers", description="Target audience")

class TrainingModule(BaseModel):
    """Training module model."""
    id: str = Field(..., description="Unique module ID")
    title: str = Field(..., description="Module title")
    description: str = Field(..., description="Module description")
    duration: int = Field(..., description="Duration in minutes")
    category: TrainingCategory = Field(..., description="Training category")
    language: Language = Field(Language.ENGLISH, description="Module language")
    is_offline: bool = Field(True, description="Whether available offline")
    objectives: List[str] = Field(..., description="Learning objectives")
    steps: List[str] = Field(..., description="Step-by-step instructions")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    completion_rate: Optional[float] = Field(None, description="Completion rate percentage")

class User(BaseModel):
    """User model."""
    id: str = Field(..., description="Unique user ID")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    role: str = Field(..., description="User role (teacher, admin, etc.)")
    school: Optional[str] = Field(None, description="School name")
    region: Optional[str] = Field(None, description="Geographic region")
    preferred_language: Language = Field(Language.ENGLISH, description="Preferred language")
    created_at: datetime = Field(default_factory=datetime.now, description="Account creation timestamp")
    last_active: Optional[datetime] = Field(None, description="Last activity timestamp")

class SavedResource(BaseModel):
    """Saved resource model."""
    id: str = Field(..., description="Unique resource ID")
    user_id: str = Field(..., description="User who saved the resource")
    resource_type: str = Field(..., description="Type of resource (lesson_plan, training_module)")
    resource_id: str = Field(..., description="ID of the saved resource")
    title: str = Field(..., description="Resource title")
    saved_at: datetime = Field(default_factory=datetime.now, description="When resource was saved")
    notes: Optional[str] = Field(None, description="User notes about the resource")

class AIExplanation(BaseModel):
    """AI explanation model."""
    content_id: str = Field(..., description="ID of the content being explained")
    content_type: str = Field(..., description="Type of content (lesson_plan, training_module)")
    explanation: str = Field(..., description="AI explanation text")
    confidence_score: float = Field(..., description="AI confidence in the explanation", ge=0.0, le=1.0)
    generated_at: datetime = Field(default_factory=datetime.now, description="When explanation was generated")

class OfflineSync(BaseModel):
    """Offline synchronization model."""
    user_id: str = Field(..., description="User ID")
    resource_type: str = Field(..., description="Type of resource")
    resource_id: str = Field(..., description="Resource ID")
    action: str = Field(..., description="Action (download, upload, delete)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Sync timestamp")
    status: str = Field(..., description="Sync status (pending, completed, failed)")

class CulturalContext(BaseModel):
    """Cultural context model."""
    region: str = Field(..., description="Geographic region")
    language: Language = Field(..., description="Primary language")
    cultural_practices: List[str] = Field(..., description="Relevant cultural practices")
    available_resources: List[str] = Field(..., description="Available resources")
    teaching_style: str = Field(..., description="Preferred teaching style")
    community_values: List[str] = Field(..., description="Community values to consider")

class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details") 