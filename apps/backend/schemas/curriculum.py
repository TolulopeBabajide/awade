"""
Pydantic schemas for curriculum mapping API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CurriculumFrameworkType(str, Enum):
    NATIONAL = "national"
    STATE = "state"
    INTERNATIONAL = "international"
    SCHOOL_DISTRICT = "school_district"

class StandardLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningOutcomeType(str, Enum):
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    ATTITUDE = "attitude"
    COMPETENCY = "competency"

# Request schemas
class CurriculumFrameworkCreate(BaseModel):
    name: str = Field(..., description="Name of the curriculum framework")
    description: Optional[str] = Field(None, description="Description of the framework")
    framework_type: CurriculumFrameworkType = Field(..., description="Type of framework")
    country: Optional[str] = Field(None, description="Country for the framework")
    region: Optional[str] = Field(None, description="Region/state for the framework")
    version: Optional[str] = Field(None, description="Version of the framework")
    effective_date: Optional[datetime] = Field(None, description="When the framework becomes effective")
    expiry_date: Optional[datetime] = Field(None, description="When the framework expires")
    is_active: bool = Field(True, description="Whether the framework is active")

class CurriculumFrameworkUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    framework_type: Optional[CurriculumFrameworkType] = None
    country: Optional[str] = None
    region: Optional[str] = None
    version: Optional[str] = None
    effective_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class CurriculumStandardCreate(BaseModel):
    framework_id: int = Field(..., description="ID of the curriculum framework")
    subject: str = Field(..., description="Subject area")
    grade_level: str = Field(..., description="Grade level")
    standard_code: str = Field(..., description="Unique code for the standard")
    standard_title: str = Field(..., description="Title of the standard")
    standard_description: str = Field(..., description="Detailed description of the standard")
    level: Optional[StandardLevel] = Field(None, description="Difficulty level")
    strand: Optional[str] = Field(None, description="Main strand/category")
    sub_strand: Optional[str] = Field(None, description="Sub-strand within the main strand")
    content_area: Optional[str] = Field(None, description="Specific content area")
    is_core: bool = Field(True, description="Whether this is a core standard")

class CurriculumStandardUpdate(BaseModel):
    standard_code: Optional[str] = None
    standard_title: Optional[str] = None
    standard_description: Optional[str] = None
    level: Optional[StandardLevel] = None
    strand: Optional[str] = None
    sub_strand: Optional[str] = None
    content_area: Optional[str] = None
    is_core: Optional[bool] = None

class LearningOutcomeCreate(BaseModel):
    standard_id: int = Field(..., description="ID of the curriculum standard")
    outcome_type: LearningOutcomeType = Field(..., description="Type of learning outcome")
    outcome_code: Optional[str] = Field(None, description="Code for the outcome")
    outcome_title: str = Field(..., description="Title of the learning outcome")
    outcome_description: str = Field(..., description="Description of the learning outcome")
    success_criteria: Optional[str] = Field(None, description="How to measure achievement")
    assessment_methods: Optional[List[str]] = Field(None, description="Types of assessment methods")
    prerequisites: Optional[str] = Field(None, description="Prerequisite knowledge/skills")
    order_sequence: Optional[int] = Field(None, description="Ordering sequence")

class LearningOutcomeUpdate(BaseModel):
    outcome_type: Optional[LearningOutcomeType] = None
    outcome_code: Optional[str] = None
    outcome_title: Optional[str] = None
    outcome_description: Optional[str] = None
    success_criteria: Optional[str] = None
    assessment_methods: Optional[List[str]] = None
    prerequisites: Optional[str] = None
    order_sequence: Optional[int] = None

class StandardMappingCreate(BaseModel):
    standard_id: int = Field(..., description="ID of the curriculum standard")
    lesson_plan_id: int = Field(..., description="ID of the lesson plan")
    mapping_type: str = Field("primary", description="Type of mapping (primary, secondary, supplementary)")
    coverage_percentage: Optional[float] = Field(None, ge=0, le=100, description="Percentage of standard covered")
    alignment_notes: Optional[str] = Field(None, description="Notes about alignment")
    created_by: int = Field(..., description="ID of the user creating the mapping")

class StandardMappingUpdate(BaseModel):
    mapping_type: Optional[str] = None
    coverage_percentage: Optional[float] = Field(None, ge=0, le=100)
    alignment_notes: Optional[str] = None

class CurriculumTopicCreate(BaseModel):
    subject: str = Field(..., description="Subject area")
    grade_level: str = Field(..., description="Grade level")
    topic_name: str = Field(..., description="Name of the topic")
    topic_description: Optional[str] = Field(None, description="Description of the topic")
    parent_topic_id: Optional[int] = Field(None, description="ID of parent topic for hierarchy")
    difficulty_level: Optional[StandardLevel] = Field(None, description="Difficulty level")
    estimated_hours: Optional[float] = Field(None, description="Estimated teaching hours")
    is_core: bool = Field(True, description="Whether this is a core topic")

class CurriculumTopicUpdate(BaseModel):
    topic_name: Optional[str] = None
    topic_description: Optional[str] = None
    parent_topic_id: Optional[int] = None
    difficulty_level: Optional[StandardLevel] = None
    estimated_hours: Optional[float] = None
    is_core: Optional[bool] = None

# Response schemas
class CurriculumFrameworkResponse(BaseModel):
    framework_id: int
    name: str
    country: Optional[str]
    description: Optional[str]
    framework_type: str
    region: Optional[str]
    version: Optional[str]
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LearningOutcomeResponse(BaseModel):
    outcome_id: int
    standard_id: int
    outcome_type: LearningOutcomeType
    outcome_code: Optional[str]
    outcome_title: str
    outcome_description: str
    success_criteria: Optional[str]
    assessment_methods: Optional[List[str]]
    prerequisites: Optional[str]
    order_sequence: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CurriculumStandardResponse(BaseModel):
    standard_id: int
    framework_id: int
    subject: str
    grade_level: str
    standard_code: str
    standard_title: str
    standard_description: str
    level: Optional[StandardLevel]
    strand: Optional[str]
    sub_strand: Optional[str]
    content_area: Optional[str]
    is_core: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CurriculumStandardDetailResponse(CurriculumStandardResponse):
    framework: CurriculumFrameworkResponse
    learning_outcomes: List[LearningOutcomeResponse]

    class Config:
        from_attributes = True

class StandardMappingResponse(BaseModel):
    mapping_id: int
    standard_id: int
    lesson_plan_id: int
    mapping_type: str
    coverage_percentage: Optional[float]
    alignment_notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CurriculumTopicResponse(BaseModel):
    topic_id: int
    subject: str
    grade_level: str
    topic_name: str
    topic_description: Optional[str]
    parent_topic_id: Optional[int]
    difficulty_level: Optional[StandardLevel]
    estimated_hours: Optional[float]
    is_core: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CurriculumTopicDetailResponse(CurriculumTopicResponse):
    parent_topic: Optional['CurriculumTopicResponse']
    child_topics: List['CurriculumTopicResponse']

    class Config:
        from_attributes = True

# Comprehensive response schemas
class CurriculumMappingFullResponse(BaseModel):
    framework: CurriculumFrameworkResponse
    standard: CurriculumStandardDetailResponse
    mappings: List[StandardMappingResponse]

    class Config:
        from_attributes = True

class LessonPlanCurriculumResponse(BaseModel):
    lesson_plan_id: int
    lesson_title: str
    subject: str
    grade_level: str
    standard_mappings: List[StandardMappingResponse]
    coverage_summary: Dict[str, Any]  # Summary of curriculum coverage

    class Config:
        from_attributes = True

# Search and filter schemas
class CurriculumSearchParams(BaseModel):
    subject: Optional[str] = None
    grade_level: Optional[str] = None
    country: Optional[str] = None
    framework_type: Optional[CurriculumFrameworkType] = None
    strand: Optional[str] = None
    is_core: Optional[bool] = None
    is_active: Optional[bool] = None

class StandardMappingSearchParams(BaseModel):
    lesson_plan_id: Optional[int] = None
    standard_id: Optional[int] = None
    mapping_type: Optional[str] = None
    created_by: Optional[int] = None

# New Curriculum Schemas
class CurriculumCreate(BaseModel):
    country: str = Field(..., description="Country for the curriculum")
    grade_level: str = Field(..., description="Grade level (e.g., JSS1)")
    subject: str = Field(..., description="Subject area")
    theme: Optional[str] = Field(None, description="Theme of the curriculum")

class CurriculumUpdate(BaseModel):
    country: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None
    theme: Optional[str] = None

class TopicCreate(BaseModel):
    curriculum_id: int = Field(..., description="ID of the curriculum")
    topic_code: str = Field(..., description="Unique code for the topic")
    topic_title: str = Field(..., description="Title of the topic")
    description: Optional[str] = Field(None, description="Description of the topic")

class TopicUpdate(BaseModel):
    topic_code: Optional[str] = None
    topic_title: Optional[str] = None
    description: Optional[str] = None

class LearningObjectiveCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    objective: str = Field(..., description="Learning objective text")

class LearningObjectiveUpdate(BaseModel):
    objective: str = Field(..., description="Learning objective text")

class ContentCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    content_area: str = Field(..., description="Content area text")

class ContentUpdate(BaseModel):
    content_area: str = Field(..., description="Content area text")

class TeacherActivityCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    activity: str = Field(..., description="Teacher activity text")

class TeacherActivityUpdate(BaseModel):
    activity: str = Field(..., description="Teacher activity text")

class StudentActivityCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    activity: str = Field(..., description="Student activity text")

class StudentActivityUpdate(BaseModel):
    activity: str = Field(..., description="Student activity text")

class TeachingMaterialCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    material: str = Field(..., description="Teaching material text")

class TeachingMaterialUpdate(BaseModel):
    material: str = Field(..., description="Teaching material text")

class EvaluationGuideCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    guide: str = Field(..., description="Evaluation guide text")

class EvaluationGuideUpdate(BaseModel):
    guide: str = Field(..., description="Evaluation guide text")

# Response schemas for new curriculum models
class CurriculumResponse(BaseModel):
    id: int
    country: str
    grade_level: str
    subject: str
    theme: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LearningObjectiveResponse(BaseModel):
    id: int
    topic_id: int
    objective: str
    created_at: datetime

    class Config:
        from_attributes = True

class ContentResponse(BaseModel):
    id: int
    topic_id: int
    content_area: str
    created_at: datetime

    class Config:
        from_attributes = True

class TeacherActivityResponse(BaseModel):
    id: int
    topic_id: int
    activity: str
    created_at: datetime

    class Config:
        from_attributes = True

class StudentActivityResponse(BaseModel):
    id: int
    topic_id: int
    activity: str
    created_at: datetime

    class Config:
        from_attributes = True

class TeachingMaterialResponse(BaseModel):
    id: int
    topic_id: int
    material: str
    created_at: datetime

    class Config:
        from_attributes = True

class EvaluationGuideResponse(BaseModel):
    id: int
    topic_id: int
    guide: str
    created_at: datetime

    class Config:
        from_attributes = True

class TopicResponse(BaseModel):
    id: int
    standard_id: int
    topic_name: str
    topic_description: Optional[str]
    parent_topic_id: Optional[int]
    difficulty_level: Optional[str]
    estimated_hours: Optional[float]
    is_core: Optional[bool]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class TopicDetailResponse(TopicResponse):
    curriculum: CurriculumResponse
    learning_objectives: List[LearningObjectiveResponse]
    contents: List[ContentResponse]
    teacher_activities: List[TeacherActivityResponse]
    student_activities: List[StudentActivityResponse]
    teaching_materials: List[TeachingMaterialResponse]
    evaluation_guides: List[EvaluationGuideResponse]

    class Config:
        from_attributes = True

class CurriculumDetailResponse(CurriculumResponse):
    topics: List[TopicResponse]

    class Config:
        from_attributes = True

# Bulk creation schemas
class TopicBulkCreate(BaseModel):
    topic_code: str
    topic_title: str
    description: Optional[str] = None
    learning_objectives: List[str] = []
    contents: List[str] = []
    teacher_activities: List[str] = []
    student_activities: List[str] = []
    teaching_materials: List[str] = []
    evaluation_guides: List[str] = []

class CurriculumBulkCreate(BaseModel):
    country: str
    grade_level: str
    subject: str
    theme: Optional[str] = None
    topics: List[TopicBulkCreate]

# Search and filter schemas
class CurriculumSearchParams(BaseModel):
    country: Optional[str] = None
    grade_level: Optional[str] = None
    subject: Optional[str] = None
    theme: Optional[str] = None

class TopicSearchParams(BaseModel):
    curriculum_id: Optional[int] = None
    topic_code: Optional[str] = None
    topic_title: Optional[str] = None 