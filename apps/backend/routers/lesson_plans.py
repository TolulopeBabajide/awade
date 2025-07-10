"""
Lesson plans router with enhanced functionality.
Includes curriculum mapping, PDF export, and context management.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from apps.backend.database import get_db
from apps.backend.models import LessonPlan, LessonSection, ResourceLink, LessonContext, User
from apps.backend.services.curriculum_service import CurriculumService, get_curriculum_service
from apps.backend.services.pdf_service import PDFService
from packages.ai.gpt_service import AwadeGPTService
from apps.backend.schemas.lesson_plans import (
    LessonPlanCreate,
    LessonPlanResponse,
    LessonPlanUpdate,
    LessonContextCreate,
    CurriculumMapResponse
)

router = APIRouter(prefix="/api/lesson-plans", tags=["lesson-plans"])

@router.post("/generate", response_model=LessonPlanResponse)
async def generate_lesson_plan(
    request: LessonPlanCreate,
    db: Session = Depends(get_db),
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """
    Generate an AI-powered lesson plan with curriculum mapping.
    """
    # Map curriculum standards
    curriculum = curriculum_service.map_curriculum(
        subject=request.subject,
        grade_level=request.grade_level,
        country=request.country
    )
    
    # Generate lesson plan using AI
    gpt_service = AwadeGPTService()
    ai_response = gpt_service.generate_lesson_plan(
        subject=request.subject,
        grade=request.grade_level,
        objectives=request.objectives,
        duration=request.duration_minutes,
        language=request.language,
        cultural_context=request.cultural_context or "African"
    )
    
    # Create lesson plan in database
    lesson_plan = LessonPlan(
        title=ai_response.get("title", f"{request.subject} Lesson Plan"),
        subject=request.subject,
        grade_level=request.grade_level,
        author_id=request.author_id,  # This should come from authenticated user
        context_description=request.local_context,
        duration_minutes=request.duration_minutes,
        status="draft"
    )
    
    db.add(lesson_plan)
    db.commit()
    db.refresh(lesson_plan)
    
    # Add context if provided
    if request.local_context:
        context = LessonContext(
            lesson_id=lesson_plan.lesson_id,
            context_key="local_context",
            context_value=request.local_context
        )
        db.add(context)
        db.commit()
    
    return LessonPlanResponse.from_orm(lesson_plan)

@router.get("/", response_model=List[LessonPlanResponse])
async def get_lesson_plans(
    skip: int = 0,
    limit: int = 100,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all lesson plans with optional filtering.
    """
    query = db.query(LessonPlan)
    
    if subject:
        query = query.filter(LessonPlan.subject.ilike(f"%{subject}%"))
    if grade_level:
        query = query.filter(LessonPlan.grade_level == grade_level)
    
    lesson_plans = query.offset(skip).limit(limit).all()
    return [LessonPlanResponse.from_orm(plan) for plan in lesson_plans]

@router.get("/{lesson_id}", response_model=LessonPlanResponse)
async def get_lesson_plan(lesson_id: int, db: Session = Depends(get_db)):
    """
    Get a specific lesson plan by ID.
    """
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_id == lesson_id).first()
    if not lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    
    return LessonPlanResponse.from_orm(lesson_plan)

@router.put("/{lesson_id}", response_model=LessonPlanResponse)
async def update_lesson_plan(
    lesson_id: int,
    request: LessonPlanUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a lesson plan.
    """
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_id == lesson_id).first()
    if not lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    
    # Update fields
    for field, value in request.dict(exclude_unset=True).items():
        setattr(lesson_plan, field, value)
    
    lesson_plan.updated_at = datetime.now()
    db.commit()
    db.refresh(lesson_plan)
    
    return LessonPlanResponse.from_orm(lesson_plan)

@router.delete("/{lesson_id}")
async def delete_lesson_plan(lesson_id: int, db: Session = Depends(get_db)):
    """
    Delete a lesson plan.
    """
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_id == lesson_id).first()
    if not lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    
    db.delete(lesson_plan)
    db.commit()
    
    return {"message": "Lesson plan deleted successfully"}

@router.get("/{lesson_id}/export/pdf")
async def export_lesson_plan_pdf(lesson_id: int, db: Session = Depends(get_db)):
    """
    Export lesson plan as PDF.
    """
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_id == lesson_id).first()
    if not lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    
    # Get sections and resources
    sections = db.query(LessonSection).filter(
        LessonSection.lesson_id == lesson_id
    ).order_by(LessonSection.order_number).all()
    
    resources = db.query(ResourceLink).filter(
        ResourceLink.lesson_id == lesson_id
    ).all()
    
    # Generate PDF
    pdf_service = PDFService()
    pdf_content = pdf_service.generate_lesson_plan_pdf(lesson_plan, sections, resources)
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=lesson_plan_{lesson_id}.pdf"
        }
    )

@router.post("/{lesson_id}/context")
async def add_lesson_context(
    lesson_id: int,
    context: LessonContextCreate,
    db: Session = Depends(get_db)
):
    """
    Add context information to a lesson plan.
    """
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_id == lesson_id).first()
    if not lesson_plan:
        raise HTTPException(status_code=404, detail="Lesson plan not found")
    
    lesson_context = LessonContext(
        lesson_id=lesson_id,
        context_key=context.context_key,
        context_value=context.context_value
    )
    
    db.add(lesson_context)
    db.commit()
    db.refresh(lesson_context)
    
    return {"message": "Context added successfully", "context_id": lesson_context.context_id}

@router.get("/{lesson_id}/context")
async def get_lesson_context(lesson_id: int, db: Session = Depends(get_db)):
    """
    Get all context information for a lesson plan.
    """
    contexts = db.query(LessonContext).filter(
        LessonContext.lesson_id == lesson_id
    ).all()
    
    return [
        {
            "context_id": ctx.context_id,
            "context_key": ctx.context_key,
            "context_value": ctx.context_value,
            "created_at": ctx.created_at
        }
        for ctx in contexts
    ] 