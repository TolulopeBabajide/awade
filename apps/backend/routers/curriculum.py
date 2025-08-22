"""
Curriculum API Router for Awade

This module provides endpoints for managing curriculum data, topics, learning objectives, and content areas in the Awade platform. It supports CRUD operations and curriculum mapping for educational content.

Endpoints:
- /api/curriculum: CRUD for curriculum
- /api/curriculum/topics: CRUD for topics
- /api/curriculum/learning-objectives: CRUD for learning objectives
- /api/curriculum/contents: CRUD for content areas

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator, get_optional_current_user
from apps.backend.services.curriculum_service import CurriculumService
from apps.backend.schemas.curriculum import (
    CurriculumCreate, CurriculumResponse, TopicCreate, TopicResponse,
    LearningObjectiveCreate, LearningObjectiveUpdate, LearningObjectiveResponse,
    ContentCreate, ContentUpdate, ContentResponse,
    # TeacherActivityCreate, TeacherActivityUpdate, TeacherActivityResponse,
    # StudentActivityCreate, StudentActivityUpdate, StudentActivityResponse,
    # TeachingMaterialCreate, TeachingMaterialUpdate, TeachingMaterialResponse,
    # EvaluationGuideCreate, EvaluationGuideUpdate, EvaluationGuideResponse
)
from apps.backend.models import Topic, User

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

# Curriculum endpoints
@router.post("/", response_model=CurriculumResponse)
def create_curriculum(
    curriculum_data: CurriculumCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new curriculum record.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.create_curriculum(curriculum_data)

@router.get("/", response_model=List[CurriculumResponse])
def get_curriculums(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of curriculums, optionally filtered by country.
    Requires authentication.
    """
    service = CurriculumService(db)
    return service.get_curriculums(skip=skip, limit=limit, country_id=country_id)

# Topic endpoints
@router.post("/topics", response_model=TopicResponse)
def create_topic(
    topic_data: TopicCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new topic within a curriculum structure.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.create_topic(topic_data)

@router.get("/topics", response_model=List[TopicResponse])
def get_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    curriculum_structure_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of topics, optionally filtered by curriculum structure.
    Requires authentication.
    """
    service = CurriculumService(db)
    return service.get_topics(skip=skip, limit=limit, curriculum_structure_id=curriculum_structure_id)

@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic(
    topic_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific topic by ID.
    Requires authentication.
    """
    service = CurriculumService(db)
    return service.get_topic(topic_id)

# Learning Objective endpoints
@router.post("/learning-objectives", response_model=LearningObjectiveResponse)
def create_learning_objective(
    objective_data: LearningObjectiveCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new learning objective for a topic.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.create_learning_objective(objective_data)

@router.get("/topics/{topic_id}/learning-objectives", response_model=List[LearningObjectiveResponse])
def get_learning_objectives(
    topic_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve learning objectives for a specific topic.
    Requires authentication.
    """
    service = CurriculumService(db)
    return service.get_learning_objectives(topic_id)

@router.put("/learning-objectives/{objective_id}", response_model=LearningObjectiveResponse)
def update_learning_objective(
    objective_id: int,
    objective_data: LearningObjectiveUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a learning objective.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.update_learning_objective(objective_id, objective_data)

@router.delete("/learning-objectives/{objective_id}")
def delete_learning_objective(
    objective_id: int, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a learning objective.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.delete_learning_objective(objective_id)

# Content endpoints
@router.post("/contents", response_model=ContentResponse)
def create_content(
    content_data: ContentCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new content area for a topic.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.create_content(content_data)

@router.get("/topics/{topic_id}/contents", response_model=List[ContentResponse])
def get_contents(
    topic_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve content areas for a specific topic.
    Requires authentication.
    """
    service = CurriculumService(db)
    return service.get_contents(topic_id)

@router.put("/contents/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_data: ContentUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a content area.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.update_content(content_id, content_data)

@router.delete("/contents/{content_id}")
def delete_content(
    content_id: int, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a content area.
    Requires admin authentication.
    """
    service = CurriculumService(db)
    return service.delete_content(content_id)

@router.get("/{curriculum_id}", response_model=CurriculumResponse)
def get_curriculum(
    curriculum_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific curriculum by ID.
    Requires authentication.
    """
    service = CurriculumService(db)
    return service.get_curriculum(curriculum_id) 