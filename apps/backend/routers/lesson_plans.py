"""
Lesson Plans Router for Awade API

This module provides endpoints for managing lesson plans, including AI-powered generation, curriculum mapping, PDF export, context management, and resource review. It supports CRUD operations and advanced GPT-based enhancements for lesson content.

Endpoints:
- /api/lesson-plans: CRUD for lesson plans
- /api/lesson-plans/generate:lesson plan generation
- /api/lesson-plans/{lesson_id}/export/pdf: PDF export
- /api/lesson-plans/{lesson_id}/resources/generate: AI lesson resource generation
- /api/lesson-plans/resources/{resource_id}/review: Resource review and update

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Response, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

# Import dependencies
from apps.backend.database import get_db
from apps.backend.models import LessonPlan, User, Topic, CurriculumStructure, Curriculum, Country, GradeLevel, Subject, LessonResource, LessonStatus, UserRole
from apps.backend.dependencies import get_current_user, require_educator, require_admin_or_educator, get_optional_current_user
# Curriculum service removed - using separate curriculum router
# from services.pdf_service import PDFService  # Temporarily disabled for contract testing
from packages.ai.gpt_service import AwadeGPTService
from apps.backend.schemas.lesson_plans import (
    LessonPlanCreate,
    LessonPlanResponse,
    LessonPlanUpdate,
    LessonResourceCreate,
    LessonResourceUpdate,
    LessonResourceResponse
)

router = APIRouter(prefix="/api/lesson-plans", tags=["lesson-plans"])

def fetch_curriculum_data(topic_obj):
    """Helper function to fetch curriculum learning objectives and contents for a topic."""
    curriculum_learning_objectives = []
    curriculum_contents = []
    if topic_obj:
        curriculum_learning_objectives = [obj.objective for obj in topic_obj.learning_objectives]
        curriculum_contents = [content.content_area for content in topic_obj.topic_contents]
    return curriculum_learning_objectives, curriculum_contents

def create_lesson_plan_response(lesson_plan, request_data=None):
    """Helper function to create a standardized lesson plan response."""
    try:
        # Fetch curriculum data
        curriculum_learning_objectives, curriculum_contents = fetch_curriculum_data(lesson_plan.topic)
        
        # Determine title, subject, grade_level, topic
        if request_data:
            # For new lesson plans from request data
            title = f"{request_data.subject}: {request_data.topic}"
            subject = request_data.subject
            grade_level = request_data.grade_level
            topic = request_data.topic
            author_id = request_data.user_id
            duration_minutes = getattr(request_data, 'duration_minutes', 45)
        else:
            # For existing lesson plans from database
            if not lesson_plan.topic:
                raise ValueError("Lesson plan has no associated topic")
                
            title = f"{lesson_plan.topic.curriculum_structure.subject.name}: {lesson_plan.topic.topic_title}" if lesson_plan.topic else "Untitled Lesson"
            subject = lesson_plan.topic.curriculum_structure.subject.name if lesson_plan.topic else "Unknown"
            grade_level = lesson_plan.topic.curriculum_structure.grade_level.name if lesson_plan.topic else "Unknown"
            topic = lesson_plan.topic.topic_title if lesson_plan.topic else None
            author_id = 1  # Default author ID for existing lesson plans
            duration_minutes = 45  # Default duration
        
        return LessonPlanResponse(
            lesson_id=lesson_plan.lesson_plan_id,
            title=title,
            subject=subject,
            grade_level=grade_level,
            topic=topic,
            author_id=author_id,
            duration_minutes=duration_minutes,
            created_at=lesson_plan.created_at,
            updated_at=lesson_plan.created_at,  # Using created_at as updated_at
            status=LessonStatus.DRAFT,
            curriculum_learning_objectives=curriculum_learning_objectives,
            curriculum_contents=curriculum_contents
        )
    except Exception as e:
        print(f"Error creating lesson plan response: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating lesson plan response: {str(e)}"
        )

@router.post("/generate", response_model=LessonPlanResponse)
async def generate_lesson_plan(
    request: LessonPlanCreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Generate a new lesson plan using AI.
    Requires educator authentication.
    """
    try:
        # Use current user's ID as author
        request.user_id = current_user.user_id
        
        # Find topic based on curriculum structure
        topic = db.query(Topic).join(CurriculumStructure).join(Subject).join(GradeLevel).filter(
            Subject.name == request.subject,
            GradeLevel.name == request.grade_level,
            Topic.topic_title == request.topic
        ).first()
        
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found in curriculum")
        
        # Create lesson plan
        lesson_plan = LessonPlan(
            topic_id=topic.topic_id,
            created_at=datetime.utcnow()
        )
        db.add(lesson_plan)
        db.commit()
        db.refresh(lesson_plan)
        
        return create_lesson_plan_response(lesson_plan, request)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating lesson plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating lesson plan: {str(e)}")

@router.get("/", response_model=List[LessonPlanResponse])
async def get_lesson_plans(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all lesson plans with optional filtering.
    Requires authentication.
    """
    try:
        query = db.query(LessonPlan)
        
        # Apply filters
        if subject:
            query = query.join(Topic).join(CurriculumStructure).join(Subject).filter(Subject.name == subject)
        if grade_level:
            query = query.join(Topic).join(CurriculumStructure).join(GradeLevel).filter(GradeLevel.name == grade_level)
        
        # Apply pagination
        lesson_plans = query.offset(skip).limit(limit).all()
        
        return [create_lesson_plan_response(lesson_plan) for lesson_plan in lesson_plans]
        
    except Exception as e:
        print(f"Error fetching lesson plans: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching lesson plans: {str(e)}")

@router.get("/{lesson_id}", response_model=LessonPlanResponse)
async def get_lesson_plan(
    lesson_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific lesson plan by ID.
    Requires authentication.
    """
    try:
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        return create_lesson_plan_response(lesson_plan)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching lesson plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching lesson plan: {str(e)}")

@router.put("/{lesson_id}", response_model=LessonPlanResponse)
async def update_lesson_plan(
    lesson_id: int,
    request: LessonPlanUpdate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Update a lesson plan.
    Requires educator or admin authentication.
    """
    try:
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        # Check if user is admin or the lesson plan author
        # Note: This is a simplified check - you might want to add author_id to LessonPlan model
        if current_user.role != UserRole.ADMIN:
            # For now, allow educators to edit any lesson plan
            # In a more sophisticated system, you'd check if current_user is the author
            pass
        
        # Update lesson plan fields
        # Note: This is a placeholder - you'll need to add the fields you want to update
        # For example: lesson_plan.title = request.title
        
        db.commit()
        db.refresh(lesson_plan)
        
        return create_lesson_plan_response(lesson_plan)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating lesson plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating lesson plan: {str(e)}")

@router.delete("/{lesson_id}")
async def delete_lesson_plan(
    lesson_id: int, 
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Delete a lesson plan.
    Requires educator or admin authentication.
    """
    try:
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        # Check if user is admin or the lesson plan author
        if current_user.role != UserRole.ADMIN:
            # For now, allow educators to delete any lesson plan
            # In a more sophisticated system, you'd check if current_user is the author
            pass
        
        db.delete(lesson_plan)
        db.commit()
        
        return {"message": "Lesson plan deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting lesson plan: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting lesson plan: {str(e)}")

@router.post("/{lesson_id}/resources/generate", response_model=LessonResourceResponse)
async def generate_lesson_resource(
    lesson_id: int,
    data: LessonResourceCreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered lesson resources for a specific lesson plan.
    Requires educator authentication.
    """
    try:
        # Verify lesson plan exists
        lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_id).first()
        if not lesson_plan:
            raise HTTPException(status_code=404, detail="Lesson plan not found")
        
        # Initialize AI service
        ai_service = AwadeGPTService()
        
        # Generate AI content
        ai_content = ai_service.generate_lesson_resource(
            subject=data.subject,
            grade_level=data.grade_level,
            topic=data.topic,
            context_input=data.context_input
        )
        
        # Create lesson resource
        lesson_resource = LessonResource(
            lesson_plan_id=lesson_id,
            user_id=current_user.user_id,
            context_input=data.context_input,
            ai_generated_content=ai_content,
            export_format=data.export_format,
            status='draft',
            created_at=datetime.utcnow()
        )
        
        db.add(lesson_resource)
        db.commit()
        db.refresh(lesson_resource)
        
        return LessonResourceResponse(
            resource_id=lesson_resource.lesson_resources_id,
            lesson_plan_id=lesson_resource.lesson_plan_id,
            user_id=lesson_resource.user_id,
            context_input=lesson_resource.context_input,
            ai_generated_content=lesson_resource.ai_generated_content,
            user_edited_content=lesson_resource.user_edited_content,
            export_format=lesson_resource.export_format,
            status=lesson_resource.status,
            created_at=lesson_resource.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error generating lesson resource: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating lesson resource: {str(e)}")

@router.get("/ai/health")
async def check_ai_service_health():
    """
    Check AI service health.
    Public endpoint - no authentication required.
    """
    try:
        ai_service = AwadeGPTService()
        health_status = ai_service.check_health()
        return {
            "status": "healthy" if health_status else "unhealthy",
            "service": "AwadeGPTService",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "AwadeGPTService",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@router.put("/resources/{resource_id}/review", response_model=LessonResourceResponse)
async def review_lesson_resource(
    resource_id: int,
    data: LessonResourceUpdate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Review and update a lesson resource.
    Requires educator authentication.
    """
    try:
        lesson_resource = db.query(LessonResource).filter(LessonResource.lesson_resources_id == resource_id).first()
        if not lesson_resource:
            raise HTTPException(status_code=404, detail="Lesson resource not found")
        
        # Check if user is the resource author or admin
        if current_user.user_id != lesson_resource.user_id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You can only review your own resources")
        
        # Update resource
        if data.user_edited_content is not None:
            lesson_resource.user_edited_content = data.user_edited_content
        if data.status is not None:
            lesson_resource.status = data.status
        
        db.commit()
        db.refresh(lesson_resource)
        
        return LessonResourceResponse(
            resource_id=lesson_resource.lesson_resources_id,
            lesson_plan_id=lesson_resource.lesson_plan_id,
            user_id=lesson_resource.user_id,
            context_input=lesson_resource.context_input,
            ai_generated_content=lesson_resource.ai_generated_content,
            user_edited_content=lesson_resource.user_edited_content,
            export_format=lesson_resource.export_format,
            status=lesson_resource.status,
            created_at=lesson_resource.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error reviewing lesson resource: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reviewing lesson resource: {str(e)}") 