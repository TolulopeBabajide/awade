"""
Context Router for Awade API

This module provides endpoints for managing context information for lesson plans,
including CRUD operations and context retrieval. It delegates business logic to
the ContextService for clean separation of concerns.

Endpoints:
- /api/contexts: CRUD for contexts
- /api/contexts/lesson-plan/{lesson_plan_id}: Get contexts by lesson plan
- /api/contexts/{context_id}: Get, update, delete specific context

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin_or_educator
from apps.backend.services.context_service import ContextService
from apps.backend.schemas.contexts import (
    ContextCreate, 
    ContextUpdate, 
    ContextResponse, 
    ContextListResponse,
    ContextSubmissionRequest
)

router = APIRouter(prefix="/api/contexts", tags=["contexts"])

@router.post("/", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def create_context(
    context_data: ContextCreate,
    db: Session = Depends(get_db)
):
    """Create a new context for a lesson plan."""
    service = ContextService(db)
    return service.create_context(context_data)

@router.get("/lesson-plan/{lesson_plan_id}", response_model=ContextListResponse)
async def get_contexts_by_lesson_plan(
    lesson_plan_id: int,
    db: Session = Depends(get_db)
):
    """Get all contexts for a specific lesson plan."""
    service = ContextService(db)
    return service.get_contexts_by_lesson_plan(lesson_plan_id)

@router.get("/", response_model=List[ContextResponse])
async def get_all_contexts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all contexts with pagination."""
    service = ContextService(db)
    return service.get_all_contexts(skip, limit)

@router.get("/{context_id}", response_model=ContextResponse)
async def get_context(
    context_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific context by ID."""
    service = ContextService(db)
    return service.get_context(context_id)

@router.put("/{context_id}", response_model=ContextResponse)
async def update_context(
    context_id: int,
    context_data: ContextUpdate,
    db: Session = Depends(get_db)
):
    """Update a specific context."""
    service = ContextService(db)
    return service.update_context(context_id, context_data)

@router.delete("/{context_id}")
async def delete_context(
    context_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific context."""
    service = ContextService(db)
    return service.delete_context(context_id)

@router.post("/lesson-plan/{lesson_plan_id}/submit", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
async def submit_context(
    lesson_plan_id: int,
    context_data: ContextSubmissionRequest,
    db: Session = Depends(get_db)
):
    """Submit context for a lesson plan (frontend endpoint)."""
    # Convert ContextSubmissionRequest to ContextCreate by adding lesson_plan_id
    context_create_data = ContextCreate(
        lesson_plan_id=lesson_plan_id,
        context_text=context_data.context_text,
        context_type=context_data.context_type
    )
    
    service = ContextService(db)
    return service.create_context(context_create_data) 