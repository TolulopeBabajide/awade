"""
Context router for handling context-related API endpoints.

This module provides endpoints for creating, reading, updating, and deleting
context information for lesson plans.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import Context, LessonPlan
from ..schemas.contexts import (
    ContextCreate, 
    ContextUpdate, 
    ContextResponse, 
    ContextListResponse,
    ContextSubmissionRequest
)

router = APIRouter(prefix="/contexts", tags=["contexts"])

@router.post("/", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def create_context(
    context_data: ContextCreate,
    db: Session = Depends(get_db)
):
    """Create a new context for a lesson plan."""
    # Verify lesson plan exists
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == context_data.lesson_plan_id).first()
    if not lesson_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson plan not found"
        )
    
    # Create new context
    context = Context(
        lesson_plan_id=context_data.lesson_plan_id,
        context_text=context_data.context_text,
        context_type=context_data.context_type
    )
    
    db.add(context)
    db.commit()
    db.refresh(context)
    
    return context

@router.get("/lesson-plan/{lesson_plan_id}", response_model=ContextListResponse)
async def get_contexts_by_lesson_plan(
    lesson_plan_id: int,
    db: Session = Depends(get_db)
):
    """Get all contexts for a specific lesson plan."""
    # Verify lesson plan exists
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_plan_id).first()
    if not lesson_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson plan not found"
        )
    
    contexts = db.query(Context).filter(Context.lesson_plan_id == lesson_plan_id).all()
    
    return ContextListResponse(
        contexts=contexts,
        total=len(contexts)
    )

@router.get("/{context_id}", response_model=ContextResponse)
async def get_context(
    context_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific context by ID."""
    context = db.query(Context).filter(Context.context_id == context_id).first()
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )
    
    return context

@router.put("/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: int,
    context_data: ContextUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific context."""
    context = db.query(Context).filter(Context.context_id == context_id).first()
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )
    
    # Update fields if provided
    if context_data.context_text is not None:
        context.context_text = context_data.context_text
    if context_data.context_type is not None:
        context.context_type = context_data.context_type
    
    context.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(context)
    
    return context

@router.delete("/{context_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_context(
    context_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific context."""
    context = db.query(Context).filter(Context.context_id == context_id).first()
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )
    
    db.delete(context)
    db.commit()
    
    return None

@router.post("/lesson-plan/{lesson_plan_id}/submit", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def submit_context(
    lesson_plan_id: int,
    context_data: ContextSubmissionRequest,
    db: Session = Depends(get_db)
):
    """Submit context for a lesson plan (frontend endpoint)."""
    # Verify lesson plan exists
    lesson_plan = db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_plan_id).first()
    if not lesson_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson plan not found"
        )
    
    # Create new context
    context = Context(
        lesson_plan_id=lesson_plan_id,
        context_text=context_data.context_text,
        context_type=context_data.context_type
    )
    
    db.add(context)
    db.commit()
    db.refresh(context)
    
    return context 