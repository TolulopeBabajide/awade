"""
Pydantic schemas for curriculum mapping API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# New normalized curriculum schemas
class CurriculumBase(BaseModel):
    """Base schema for curriculum data."""
    curricula_title: str
    country_id: int

class CurriculumCreate(CurriculumBase):
    """Schema for creating a new curriculum."""
    pass

class CurriculumResponse(CurriculumBase):
    """Schema for curriculum response data."""
    curricula_id: int
    class Config:
        """Pydantic configuration for ORM mode."""
        orm_mode = True

class TopicBase(BaseModel):
    """Base schema for topic data."""
    curriculum_structure_id: int
    topic_title: str

class TopicCreate(TopicBase):
    """Schema for creating a new topic."""
    pass

class TopicResponse(TopicBase):
    """Schema for topic response data."""
    topic_id: int
    class Config:
        """Pydantic configuration for ORM mode."""
        orm_mode = True

# Learning Objective schemas
class LearningObjectiveCreate(BaseModel):
    topic_id: int = Field(..., description="ID of the topic")
    objective: str = Field(..., description="Learning objective text")

class LearningObjectiveUpdate(BaseModel):
    objective: str = Field(..., description="Learning objective text")

class LearningObjectiveResponse(BaseModel):
    learning_objective_id: int
    topic_id: int
    objective: str

    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True

# Content schemas
class ContentCreate(BaseModel):
    """Schema for creating content."""
    topic_id: int = Field(..., description="ID of the topic")
    content_area: str = Field(..., description="Content area text")

class ContentUpdate(BaseModel):
    """Schema for updating content."""
    content_area: str = Field(..., description="Content area text")

class ContentResponse(BaseModel):
    """Schema for content response data."""
    topic_contents_id: int
    topic_id: int
    content_area: str

    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True

# Teacher Activity schemas
# class TeacherActivityCreate(BaseModel):
#     topic_id: int = Field(..., description="ID of the topic")
#     activity: str = Field(..., description="Teacher activity text")

# class TeacherActivityUpdate(BaseModel):
#     activity: str = Field(..., description="Teacher activity text")

# class TeacherActivityResponse(BaseModel):
#     id: int
#     topic_id: int
#     activity: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# Student Activity schemas
# class StudentActivityCreate(BaseModel):
#     topic_id: int = Field(..., description="ID of the topic")
#     activity: str = Field(..., description="Student activity text")

# class StudentActivityUpdate(BaseModel):
#     activity: str = Field(..., description="Student activity text")

# class StudentActivityResponse(BaseModel):
#     id: int
#     topic_id: int
#     activity: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# Teaching Material schemas
# class TeachingMaterialCreate(BaseModel):
#     topic_id: int = Field(..., description="ID of the topic")
#     material: str = Field(..., description="Teaching material text")

# class TeachingMaterialUpdate(BaseModel):
#     material: str = Field(..., description="Teaching material text")

# class TeachingMaterialResponse(BaseModel):
#     id: int
#     topic_id: int
#     material: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# Evaluation Guide schemas
# class EvaluationGuideCreate(BaseModel):
#     topic_id: int = Field(..., description="ID of the topic")
#     guide: str = Field(..., description="Evaluation guide text")

# class EvaluationGuideUpdate(BaseModel):
#     guide: str = Field(..., description="Evaluation guide text")

# class EvaluationGuideResponse(BaseModel):
#     id: int
#     topic_id: int
#     guide: str
#     created_at: datetime

#     class Config:
#         from_attributes = True

# Topic Detail Response
class TopicDetailResponse(TopicResponse):
    """Schema for detailed topic response with learning objectives and contents."""
    learning_objectives: List[LearningObjectiveResponse]
    contents: List[ContentResponse]
    # teacher_activities: List[TeacherActivityResponse]
    # student_activities: List[StudentActivityResponse]
    # teaching_materials: List[TeachingMaterialResponse]
    # evaluation_guides: List[EvaluationGuideResponse]

    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True

# Curriculum Detail Response
class CurriculumDetailResponse(CurriculumResponse):
    """Schema for detailed curriculum response with topics."""
    topics: List[TopicResponse]

    class Config:
        """Pydantic configuration for attribute access."""
        from_attributes = True 