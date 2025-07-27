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
from apps.backend.models import Topic

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

# Curriculum endpoints
@router.post("/", response_model=CurriculumResponse)
def create_curriculum(
    curriculum_data: CurriculumCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new curriculum record.

    Args:
        curriculum_data (CurriculumCreate): The curriculum data to create.
        db (Session): Database session dependency.

    Returns:
        CurriculumResponse: The created curriculum.
    """
    service = CurriculumService(db)
    return service.create_curriculum(curriculum_data)

@router.get("/", response_model=List[CurriculumResponse])
def get_curriculums(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of curriculums, optionally filtered by country.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        country_id (Optional[int]): Filter by country ID.
        db (Session): Database session dependency.

    Returns:
        List[CurriculumResponse]: List of curriculums.
    """
    service = CurriculumService(db)
    return service.get_curriculums(skip=skip, limit=limit, country_id=country_id)

# Topic endpoints
@router.post("/topics", response_model=TopicResponse)
def create_topic(
    topic_data: TopicCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new topic within a curriculum structure.

    Args:
        topic_data (TopicCreate): The topic data to create.
        db (Session): Database session dependency.

    Returns:
        TopicResponse: The created topic.
    """
    service = CurriculumService(db)
    return service.create_topic(topic_data)

@router.get("/topics", response_model=List[TopicResponse])
def get_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    curriculum_structure_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of topics, optionally filtered by curriculum structure.

    Args:
        skip (int): Number of records to skip.
        limit (int): Maximum number of records to return.
        curriculum_structure_id (Optional[int]): Filter by curriculum structure ID.
        db (Session): Database session dependency.

    Returns:
        List[TopicResponse]: List of topics.
    """
    service = CurriculumService(db)
    return service.get_topics(skip=skip, limit=limit, curriculum_structure_id=curriculum_structure_id)

@router.get("/topics/{topic_id}", response_model=TopicResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a topic by its ID.

    Args:
        topic_id (int): The topic ID.
        db (Session): Database session dependency.

    Returns:
        TopicResponse: The topic record.
    """
    service = CurriculumService(db)
    topic = service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

# Learning Objective endpoints
@router.post("/learning-objectives", response_model=LearningObjectiveResponse)
def create_learning_objective(
    objective_data: LearningObjectiveCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new learning objective for a topic.

    Args:
        objective_data (LearningObjectiveCreate): The learning objective data to create.
        db (Session): Database session dependency.

    Returns:
        LearningObjectiveResponse: The created learning objective.
    """
    service = CurriculumService(db)
    return service.create_learning_objective(objective_data)

@router.get("/topics/{topic_id}/learning-objectives", response_model=List[LearningObjectiveResponse])
def get_learning_objectives(topic_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all learning objectives for a given topic.

    Args:
        topic_id (int): The topic ID.
        db (Session): Database session dependency.

    Returns:
        List[LearningObjectiveResponse]: List of learning objectives.
    """
    service = CurriculumService(db)
    return service.get_learning_objectives(topic_id)

@router.put("/learning-objectives/{objective_id}", response_model=LearningObjectiveResponse)
def update_learning_objective(
    objective_id: int,
    objective_data: LearningObjectiveUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a learning objective by its ID.

    Args:
        objective_id (int): The learning objective ID.
        objective_data (LearningObjectiveUpdate): The updated objective data.
        db (Session): Database session dependency.

    Returns:
        LearningObjectiveResponse: The updated learning objective.
    """
    service = CurriculumService(db)
    objective = service.update_learning_objective(objective_id, objective_data.objective)
    if not objective:
        raise HTTPException(status_code=404, detail="Learning objective not found")
    return objective

@router.delete("/learning-objectives/{objective_id}")
def delete_learning_objective(objective_id: int, db: Session = Depends(get_db)):
    """
    Delete a learning objective by ID.
    
    Args:
        objective_id: The ID of the learning objective to delete
        db: Database session dependency
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        HTTPException: 404 if learning objective not found
    """
    service = CurriculumService(db)
    success = service.delete_learning_objective(objective_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learning objective not found")
    return {"message": "Learning objective deleted successfully"}

# Content endpoints
@router.post("/contents", response_model=ContentResponse)
def create_content(content_data: ContentCreate, db: Session = Depends(get_db)):
    """
    Create a new content item for a topic.
    
    Args:
        content_data: Content creation data including topic_id and content_area
        db: Database session dependency
        
    Returns:
        ContentResponse: The created content item
    """
    service = CurriculumService(db)
    return service.create_content(content_data)

@router.get("/topics/{topic_id}/contents", response_model=List[ContentResponse])
def get_contents(topic_id: int, db: Session = Depends(get_db)):
    """
    Get all content items for a specific topic.
    
    Args:
        topic_id: The ID of the topic to get contents for
        db: Database session dependency
        
    Returns:
        List[ContentResponse]: List of content items for the topic
    """
    service = CurriculumService(db)
    return service.get_contents(topic_id)

@router.put("/contents/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_data: ContentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a content item by ID.
    
    Args:
        content_id: The ID of the content item to update
        content_data: Updated content data
        db: Database session dependency
        
    Returns:
        ContentResponse: The updated content item
        
    Raises:
        HTTPException: 404 if content not found
    """
    service = CurriculumService(db)
    content = service.update_content(content_id, content_data.content_area)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.delete("/contents/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):
    """
    Delete a content item by ID.
    
    Args:
        content_id: The ID of the content item to delete
        db: Database session dependency
        
    Returns:
        dict: Success message confirming deletion
        
    Raises:
        HTTPException: 404 if content not found
    """
    service = CurriculumService(db)
    success = service.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"message": "Content deleted successfully"}

# Teacher Activity endpoints
# @router.post("/teacher-activities", response_model=TeacherActivityResponse)
# def create_teacher_activity(
#     activity_data: TeacherActivityCreate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     return service.create_teacher_activity(activity_data)

# @router.get("/topics/{topic_id}/teacher-activities", response_model=List[TeacherActivityResponse])
# def get_teacher_activities(topic_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     return service.get_teacher_activities(topic_id)

# @router.put("/teacher-activities/{activity_id}", response_model=TeacherActivityResponse)
# def update_teacher_activity(
#     activity_id: int,
#     activity_data: TeacherActivityUpdate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     activity = service.update_teacher_activity(activity_id, activity_data.activity)
#     if not activity:
#         raise HTTPException(status_code=404, detail="Teacher activity not found")
#     return activity

# @router.delete("/teacher-activities/{activity_id}")
# def delete_teacher_activity(activity_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     success = service.delete_teacher_activity(activity_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Teacher activity not found")
#     return {"message": "Teacher activity deleted successfully"}

# Student Activity endpoints
# @router.post("/student-activities", response_model=StudentActivityResponse)
# def create_student_activity(
#     activity_data: StudentActivityCreate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     return service.create_student_activity(activity_data)

# @router.get("/topics/{topic_id}/student-activities", response_model=List[StudentActivityResponse])
# def get_student_activities(topic_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     return service.get_student_activities(topic_id)

# @router.put("/student-activities/{activity_id}", response_model=StudentActivityResponse)
# def update_student_activity(
#     activity_id: int,
#     activity_data: StudentActivityUpdate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     activity = service.update_student_activity(activity_id, activity_data.activity)
#     if not activity:
#         raise HTTPException(status_code=404, detail="Student activity not found")
#     return activity

# @router.delete("/student-activities/{activity_id}")
# def delete_student_activity(activity_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     success = service.delete_student_activity(activity_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Student activity not found")
#     return {"message": "Student activity deleted successfully"}

# Teaching Material endpoints
# @router.post("/teaching-materials", response_model=TeachingMaterialResponse)
# def create_teaching_material(
#     material_data: TeachingMaterialCreate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     return service.create_teaching_material(material_data)

# @router.get("/topics/{topic_id}/teaching-materials", response_model=List[TeachingMaterialResponse])
# def get_teaching_materials(topic_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     return service.get_teaching_materials(topic_id)

# @router.put("/teaching-materials/{material_id}", response_model=TeachingMaterialResponse)
# def update_teaching_material(
#     material_id: int,
#     material_data: TeachingMaterialUpdate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     material = service.update_teaching_material(material_id, material_data.material)
#     if not material:
#         raise HTTPException(status_code=404, detail="Teaching material not found")
#     return material

# @router.delete("/teaching-materials/{material_id}")
# def delete_teaching_material(material_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     success = service.delete_teaching_material(material_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Teaching material not found")
#     return {"message": "Teaching material deleted successfully"}

# Evaluation Guide endpoints
# @router.post("/evaluation-guides", response_model=EvaluationGuideResponse)
# def create_evaluation_guide(
#     guide_data: EvaluationGuideCreate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     return service.create_evaluation_guide(guide_data)

# @router.get("/topics/{topic_id}/evaluation-guides", response_model=List[EvaluationGuideResponse])
# def get_evaluation_guides(topic_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     return service.get_evaluation_guides(topic_id)

# @router.put("/evaluation-guides/{guide_id}", response_model=EvaluationGuideResponse)
# def update_evaluation_guide(
#     guide_id: int,
#     guide_data: EvaluationGuideUpdate,
#     db: Session = Depends(get_db)
# ):
#     service = CurriculumService(db)
#     guide = service.update_evaluation_guide(guide_id, guide_data.guide)
#     if not guide:
#         raise HTTPException(status_code=404, detail="Evaluation guide not found")
#     return guide

# @router.delete("/evaluation-guides/{guide_id}")
# def delete_evaluation_guide(guide_id: int, db: Session = Depends(get_db)):
#     service = CurriculumService(db)
#     success = service.delete_evaluation_guide(guide_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Evaluation guide not found")
#     return {"message": "Evaluation guide deleted successfully"}

# Curriculum ID endpoint (moved after specific routes to avoid conflicts)
@router.get("/{curriculum_id}", response_model=CurriculumResponse)
def get_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a curriculum by its ID.

    Args:
        curriculum_id (int): The curriculum ID.
        db (Session): Database session dependency.

    Returns:
        CurriculumResponse: The curriculum record.
    """
    service = CurriculumService(db)
    curriculum = service.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum 