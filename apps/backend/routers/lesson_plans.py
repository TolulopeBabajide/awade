"""
Lesson Plans Router for Awade API

This module provides endpoints for managing lesson plans, including AI-powered generation, 
curriculum mapping, PDF export, context management, and resource review. It delegates
business logic to the LessonPlanService for clean separation of concerns.

Endpoints:
- /api/lesson-plans: CRUD for lesson plans
- /api/lesson-plans/generate: lesson plan generation
- /api/lesson-plans/{lesson_id}/export/pdf: PDF export
- /api/lesson-plans/{lesson_id}/resources/generate: AI lesson resource generation
- /api/lesson-plans/resources/{resource_id}/review: Resource review and update

Author: Tolulope Babajide
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from apps.backend.database import get_db
from apps.backend.models import User
from apps.backend.dependencies import get_current_user, require_educator, require_admin_or_educator
from apps.backend.limiter import limiter
from apps.backend.services.lesson_plan_service import LessonPlanService
from apps.backend.services.lesson_resource_service import LessonResourceService
from apps.backend.schemas.lesson_plans import (
    LessonPlanCreate,
    LessonPlanResponse,
    LessonPlanUpdate,
    LessonResourceCreate,
    LessonResourceUpdate,
    LessonResourceResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/lesson-plans", tags=["lesson-plans"])

@router.post("/generate", response_model=LessonPlanResponse)
@limiter.limit("5/minute")
async def generate_lesson_plan(
    request: Request,
    data: LessonPlanCreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Generate a new lesson plan using AI.
    Requires educator authentication.
    """
    service = LessonPlanService(db)
    return service.generate_lesson_plan(data, current_user)

@router.get("/resources", response_model=List[LessonResourceResponse])
async def get_all_lesson_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all lesson resources for the current user.
    Requires authentication.
    """
    service = LessonResourceService(db)
    return service.get_all_lesson_resources(current_user)

@router.get("/resources/{resource_id}", response_model=LessonResourceResponse)
async def get_lesson_resource(
    resource_id: int,
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific lesson resource.
    Requires authentication.
    """
    # Prevent caching of polling results
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"

    service = LessonResourceService(db)
    return service.get_lesson_resource(resource_id, current_user)

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
    Get lesson plans for the current user with optional filtering.
    Requires authentication.
    """
    service = LessonPlanService(db)
    return service.get_lesson_plans(current_user, skip, limit, subject, grade_level)

@router.get("/{lesson_id}", response_model=LessonPlanResponse)
async def get_lesson_plan(
    lesson_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific lesson plan by ID.
    Requires authentication and ownership.
    """
    service = LessonPlanService(db)
    return service.get_lesson_plan(lesson_id, current_user)

@router.put("/{lesson_id}", response_model=LessonPlanResponse)
async def update_lesson_plan(
    lesson_id: int,
    request: LessonPlanUpdate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Update a lesson plan.
    Requires educator or admin authentication and ownership.
    """
    service = LessonPlanService(db)
    return service.update_lesson_plan(lesson_id, request, current_user)

@router.delete("/{lesson_id}")
async def delete_lesson_plan(
    lesson_id: int, 
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Delete a lesson plan.
    Requires educator or admin authentication and ownership.
    """
    service = LessonPlanService(db)
    return service.delete_lesson_plan(lesson_id, current_user)

@router.get("/{lesson_id}/resources", response_model=List[LessonResourceResponse])
async def get_lesson_plan_resources(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all resources for a specific lesson plan.
    Requires authentication and ownership.
    """
    service = LessonResourceService(db)
    return service.get_lesson_plan_resources(lesson_id, current_user)

@router.post("/{lesson_id}/resources/generate", response_model=LessonResourceResponse)
@limiter.limit("3/minute")
async def generate_lesson_resource(
    lesson_id: int,
    data: LessonResourceCreate,
    request: Request,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered lesson resources for a specific lesson plan.
    Requires educator authentication.
    """
    redis_pool = getattr(request.app.state, "redis", None)
    service = LessonResourceService(db, redis_pool)
    return await service.generate_lesson_resource(lesson_id, data, current_user)

@router.post("/resources/{resource_id}/export")
async def export_lesson_resource(
    resource_id: int,
    format_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a lesson resource to PDF or DOCX format.
    Requires authentication and ownership.
    """
    from apps.backend.services.pdf_service import PDFService

    # AWD-M-70: delegate access-control to LessonResourceService so the
    # ADMIN/SUPER_ADMIN/owner-scoped query lives in one place. AWD-M-67
    # (uniform 404 for unauthorised callers) and AWD-H-61 (SUPER_ADMIN bypass)
    # are enforced inside the service helper — see get_lesson_resource_orm().
    lesson_resource = LessonResourceService(db).get_lesson_resource_orm(
        resource_id, current_user
    )
    
    # Get export format
    export_format = format_data.get("format", "pdf").lower()
    
    # Initialize PDF service
    pdf_service = PDFService()
    
    try:
        if export_format == "pdf":
            pdf_content = pdf_service.generate_lesson_resource_pdf(lesson_resource, db)
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=lesson_resource_{resource_id}.pdf"}
            )
        elif export_format == "docx":
            docx_content = pdf_service.export_to_docx(lesson_resource, db)
            return Response(
                content=docx_content,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename=lesson_resource_{resource_id}.docx"}
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format. Use 'pdf' or 'docx'")
            
    except HTTPException:
        raise
    except Exception:
        logger.error(
            "Unexpected error exporting lesson resource %s", resource_id, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while exporting the resource."
        )

# Additional endpoints can be added here as needed 