"""
Curriculum API router for managing curriculum data and related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from ..services.curriculum_service import CurriculumService
from ..schemas.curriculum import (
    CurriculumCreate, CurriculumUpdate, CurriculumResponse, CurriculumDetailResponse,
    TopicCreate, TopicUpdate, TopicResponse, TopicDetailResponse,
    LearningObjectiveCreate, LearningObjectiveResponse,
    ContentCreate, ContentResponse,
    TeacherActivityCreate, TeacherActivityResponse,
    StudentActivityCreate, StudentActivityResponse,
    TeachingMaterialCreate, TeachingMaterialResponse,
    EvaluationGuideCreate, EvaluationGuideResponse,
    CurriculumBulkCreate, TopicBulkCreate,
    CurriculumSearchParams, TopicSearchParams
)

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

# Curriculum mapping endpoint
@router.get("/map")
def map_curriculum(
    subject: str = Query(..., description="Subject area"),
    grade_level: str = Query(..., description="Grade level"),
    country: str = Query("Nigeria", description="Country for curriculum mapping"),
    db: Session = Depends(get_db)
):
    """
    Map subject and grade level to curriculum standards.
    Returns curriculum_id and curriculum_description for lesson plan alignment.
    """
    service = CurriculumService(db)
    
    # Find matching curriculum
    curriculums = service.get_curriculums(
        subject=subject,
        grade_level=grade_level,
        country=country,
        limit=1
    )
    
    if not curriculums:
        raise HTTPException(
            status_code=404,
            detail=f"No curriculum found for {subject} {grade_level} in {country}"
        )
    
    curriculum = curriculums[0]
    
    return {
        "curriculum_id": curriculum.id,
        "curriculum_description": f"{curriculum.subject} curriculum for {curriculum.grade_level} in {curriculum.country}",
        "subject": curriculum.subject,
        "grade_level": curriculum.grade_level,
        "country": curriculum.country,
        "theme": curriculum.theme
    }

# Curriculum endpoints
@router.post("/", response_model=CurriculumResponse)
def create_curriculum(
    curriculum_data: CurriculumCreate,
    db: Session = Depends(get_db)
):
    """Create a new curriculum."""
    service = CurriculumService(db)
    return service.create_curriculum(curriculum_data)

@router.get("/", response_model=List[CurriculumResponse])
def get_curriculums(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    country: Optional[str] = None,
    grade_level: Optional[str] = None,
    subject: Optional[str] = None,
    theme: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get curricula with optional filtering."""
    service = CurriculumService(db)
    filters = {}
    if country:
        filters['country'] = country
    if grade_level:
        filters['grade_level'] = grade_level
    if subject:
        filters['subject'] = subject
    if theme:
        filters['theme'] = theme
    
    return service.get_curriculums(skip=skip, limit=limit, **filters)

@router.get("/{curriculum_id}", response_model=CurriculumDetailResponse)
def get_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    """Get a curriculum by ID with all its topics."""
    service = CurriculumService(db)
    curriculum = service.get_curriculum(curriculum_id)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum

@router.put("/{curriculum_id}", response_model=CurriculumResponse)
def update_curriculum(
    curriculum_id: int,
    curriculum_data: CurriculumUpdate,
    db: Session = Depends(get_db)
):
    """Update a curriculum."""
    service = CurriculumService(db)
    curriculum = service.update_curriculum(curriculum_id, curriculum_data)
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return curriculum

@router.delete("/{curriculum_id}")
def delete_curriculum(curriculum_id: int, db: Session = Depends(get_db)):
    """Delete a curriculum and all related data."""
    service = CurriculumService(db)
    success = service.delete_curriculum(curriculum_id)
    if not success:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return {"message": "Curriculum deleted successfully"}

# Topic endpoints
@router.post("/topics", response_model=TopicResponse)
def create_topic(topic_data: TopicCreate, db: Session = Depends(get_db)):
    """Create a new topic."""
    service = CurriculumService(db)
    return service.create_topic(topic_data)

@router.get("/topics", response_model=List[TopicResponse])
def get_topics(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    curriculum_id: Optional[int] = None,
    topic_code: Optional[str] = None,
    topic_title: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get topics with optional filtering."""
    service = CurriculumService(db)
    filters = {}
    if curriculum_id:
        filters['curriculum_id'] = curriculum_id
    if topic_code:
        filters['topic_code'] = topic_code
    if topic_title:
        filters['topic_title'] = topic_title
    
    return service.get_topics(skip=skip, limit=limit, **filters)

@router.get("/topics/{topic_id}", response_model=TopicDetailResponse)
def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get a topic by ID with all related data."""
    service = CurriculumService(db)
    topic = service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/topics/code/{topic_code}", response_model=TopicDetailResponse)
def get_topic_by_code(topic_code: str, db: Session = Depends(get_db)):
    """Get a topic by its unique code."""
    service = CurriculumService(db)
    topic = service.get_topic_by_code(topic_code)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.put("/topics/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db)
):
    """Update a topic."""
    service = CurriculumService(db)
    topic = service.update_topic(topic_id, topic_data)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.delete("/topics/{topic_id}")
def delete_topic(topic_id: int, db: Session = Depends(get_db)):
    """Delete a topic and all related data."""
    service = CurriculumService(db)
    success = service.delete_topic(topic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic deleted successfully"}

# Learning Objective endpoints
@router.post("/learning-objectives", response_model=LearningObjectiveResponse)
def create_learning_objective(
    objective_data: LearningObjectiveCreate,
    db: Session = Depends(get_db)
):
    """Create a new learning objective."""
    service = CurriculumService(db)
    return service.create_learning_objective(objective_data)

@router.get("/topics/{topic_id}/learning-objectives", response_model=List[LearningObjectiveResponse])
def get_learning_objectives(topic_id: int, db: Session = Depends(get_db)):
    """Get all learning objectives for a topic."""
    service = CurriculumService(db)
    return service.get_learning_objectives(topic_id)

@router.put("/learning-objectives/{objective_id}", response_model=LearningObjectiveResponse)
def update_learning_objective(
    objective_id: int,
    objective: str,
    db: Session = Depends(get_db)
):
    """Update a learning objective."""
    service = CurriculumService(db)
    objective_obj = service.update_learning_objective(objective_id, objective)
    if not objective_obj:
        raise HTTPException(status_code=404, detail="Learning objective not found")
    return objective_obj

@router.delete("/learning-objectives/{objective_id}")
def delete_learning_objective(objective_id: int, db: Session = Depends(get_db)):
    """Delete a learning objective."""
    service = CurriculumService(db)
    success = service.delete_learning_objective(objective_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learning objective not found")
    return {"message": "Learning objective deleted successfully"}

# Content endpoints
@router.post("/contents", response_model=ContentResponse)
def create_content(content_data: ContentCreate, db: Session = Depends(get_db)):
    """Create a new content area."""
    service = CurriculumService(db)
    return service.create_content(content_data)

@router.get("/topics/{topic_id}/contents", response_model=List[ContentResponse])
def get_contents(topic_id: int, db: Session = Depends(get_db)):
    """Get all content areas for a topic."""
    service = CurriculumService(db)
    return service.get_contents(topic_id)

@router.put("/contents/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content_area: str,
    db: Session = Depends(get_db)
):
    """Update a content area."""
    service = CurriculumService(db)
    content = service.update_content(content_id, content_area)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.delete("/contents/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):
    """Delete a content area."""
    service = CurriculumService(db)
    success = service.delete_content(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content not found")
    return {"message": "Content deleted successfully"}

# Teacher Activity endpoints
@router.post("/teacher-activities", response_model=TeacherActivityResponse)
def create_teacher_activity(
    activity_data: TeacherActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new teacher activity."""
    service = CurriculumService(db)
    return service.create_teacher_activity(activity_data)

@router.get("/topics/{topic_id}/teacher-activities", response_model=List[TeacherActivityResponse])
def get_teacher_activities(topic_id: int, db: Session = Depends(get_db)):
    """Get all teacher activities for a topic."""
    service = CurriculumService(db)
    return service.get_teacher_activities(topic_id)

@router.put("/teacher-activities/{activity_id}", response_model=TeacherActivityResponse)
def update_teacher_activity(
    activity_id: int,
    activity: str,
    db: Session = Depends(get_db)
):
    """Update a teacher activity."""
    service = CurriculumService(db)
    activity_obj = service.update_teacher_activity(activity_id, activity)
    if not activity_obj:
        raise HTTPException(status_code=404, detail="Teacher activity not found")
    return activity_obj

@router.delete("/teacher-activities/{activity_id}")
def delete_teacher_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete a teacher activity."""
    service = CurriculumService(db)
    success = service.delete_teacher_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Teacher activity not found")
    return {"message": "Teacher activity deleted successfully"}

# Student Activity endpoints
@router.post("/student-activities", response_model=StudentActivityResponse)
def create_student_activity(
    activity_data: StudentActivityCreate,
    db: Session = Depends(get_db)
):
    """Create a new student activity."""
    service = CurriculumService(db)
    return service.create_student_activity(activity_data)

@router.get("/topics/{topic_id}/student-activities", response_model=List[StudentActivityResponse])
def get_student_activities(topic_id: int, db: Session = Depends(get_db)):
    """Get all student activities for a topic."""
    service = CurriculumService(db)
    return service.get_student_activities(topic_id)

@router.put("/student-activities/{activity_id}", response_model=StudentActivityResponse)
def update_student_activity(
    activity_id: int,
    activity: str,
    db: Session = Depends(get_db)
):
    """Update a student activity."""
    service = CurriculumService(db)
    activity_obj = service.update_student_activity(activity_id, activity)
    if not activity_obj:
        raise HTTPException(status_code=404, detail="Student activity not found")
    return activity_obj

@router.delete("/student-activities/{activity_id}")
def delete_student_activity(activity_id: int, db: Session = Depends(get_db)):
    """Delete a student activity."""
    service = CurriculumService(db)
    success = service.delete_student_activity(activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student activity not found")
    return {"message": "Student activity deleted successfully"}

# Teaching Material endpoints
@router.post("/teaching-materials", response_model=TeachingMaterialResponse)
def create_teaching_material(
    material_data: TeachingMaterialCreate,
    db: Session = Depends(get_db)
):
    """Create a new teaching material."""
    service = CurriculumService(db)
    return service.create_teaching_material(material_data)

@router.get("/topics/{topic_id}/teaching-materials", response_model=List[TeachingMaterialResponse])
def get_teaching_materials(topic_id: int, db: Session = Depends(get_db)):
    """Get all teaching materials for a topic."""
    service = CurriculumService(db)
    return service.get_teaching_materials(topic_id)

@router.put("/teaching-materials/{material_id}", response_model=TeachingMaterialResponse)
def update_teaching_material(
    material_id: int,
    material: str,
    db: Session = Depends(get_db)
):
    """Update a teaching material."""
    service = CurriculumService(db)
    material_obj = service.update_teaching_material(material_id, material)
    if not material_obj:
        raise HTTPException(status_code=404, detail="Teaching material not found")
    return material_obj

@router.delete("/teaching-materials/{material_id}")
def delete_teaching_material(material_id: int, db: Session = Depends(get_db)):
    """Delete a teaching material."""
    service = CurriculumService(db)
    success = service.delete_teaching_material(material_id)
    if not success:
        raise HTTPException(status_code=404, detail="Teaching material not found")
    return {"message": "Teaching material deleted successfully"}

# Evaluation Guide endpoints
@router.post("/evaluation-guides", response_model=EvaluationGuideResponse)
def create_evaluation_guide(
    guide_data: EvaluationGuideCreate,
    db: Session = Depends(get_db)
):
    """Create a new evaluation guide."""
    service = CurriculumService(db)
    return service.create_evaluation_guide(guide_data)

@router.get("/topics/{topic_id}/evaluation-guides", response_model=List[EvaluationGuideResponse])
def get_evaluation_guides(topic_id: int, db: Session = Depends(get_db)):
    """Get all evaluation guides for a topic."""
    service = CurriculumService(db)
    return service.get_evaluation_guides(topic_id)

@router.put("/evaluation-guides/{guide_id}", response_model=EvaluationGuideResponse)
def update_evaluation_guide(
    guide_id: int,
    guide: str,
    db: Session = Depends(get_db)
):
    """Update an evaluation guide."""
    service = CurriculumService(db)
    guide_obj = service.update_evaluation_guide(guide_id, guide)
    if not guide_obj:
        raise HTTPException(status_code=404, detail="Evaluation guide not found")
    return guide_obj

@router.delete("/evaluation-guides/{guide_id}")
def delete_evaluation_guide(guide_id: int, db: Session = Depends(get_db)):
    """Delete an evaluation guide."""
    service = CurriculumService(db)
    success = service.delete_evaluation_guide(guide_id)
    if not success:
        raise HTTPException(status_code=404, detail="Evaluation guide not found")
    return {"message": "Evaluation guide deleted successfully"}

# Bulk operations
@router.post("/bulk", response_model=CurriculumDetailResponse)
def create_curriculum_with_topics(
    curriculum_data: CurriculumBulkCreate,
    db: Session = Depends(get_db)
):
    """Create a curriculum with all its topics and related data."""
    service = CurriculumService(db)
    return service.create_curriculum_with_topics(curriculum_data)

# Search endpoints
@router.get("/search/curriculums", response_model=List[CurriculumResponse])
def search_curriculums(
    search_term: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search curricula by country, subject, or theme."""
    service = CurriculumService(db)
    return service.search_curriculums(search_term)

@router.get("/search/topics", response_model=List[TopicResponse])
def search_topics(
    search_term: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
):
    """Search topics by title or description."""
    service = CurriculumService(db)
    return service.search_topics(search_term)

# Statistics endpoint
@router.get("/{curriculum_id}/statistics")
def get_curriculum_statistics(curriculum_id: int, db: Session = Depends(get_db)):
    """Get statistics for a curriculum."""
    service = CurriculumService(db)
    stats = service.get_curriculum_statistics(curriculum_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    return stats 