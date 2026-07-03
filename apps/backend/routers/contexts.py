"""
Context Router for Awade API

This module provides endpoints for managing context information for lesson plans,
including CRUD operations and context retrieval. It delegates business logic to
the ContextService for clean separation of concerns.

All endpoints require an authenticated EDUCATOR, ADMIN, or SUPER_ADMIN user.
Educators may only access contexts that belong to their own lesson plans.

Endpoints:
- /api/contexts: CRUD for contexts
- /api/contexts/lesson-plan/{lesson_plan_id}: Get contexts by lesson plan
- /api/contexts/{context_id}: Get, update, delete specific context

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.orm import Session
from typing import List

from apps.backend.database import get_db
from apps.backend.limiter import limiter
from apps.backend.models import Context, LessonPlan, User, UserRole
from apps.backend.dependencies import require_admin_or_educator
from apps.backend.services.context_service import ContextService
from apps.backend.schemas.contexts import (
    ContextCreate,
    ContextUpdate,
    ContextResponse,
    ContextListResponse,
    ContextSubmissionRequest
)

router = APIRouter(prefix="/api/contexts", tags=["contexts"])


def _is_admin(user: User) -> bool:
    """Return True if the user has admin-level access."""
    return user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)


def _get_lesson_plan_or_404(lesson_plan_id: int, db: Session) -> LessonPlan:
    """Fetch a lesson plan by ID or raise 404."""
    lesson_plan = db.query(LessonPlan).filter(
        LessonPlan.lesson_plan_id == lesson_plan_id
    ).first()
    if not lesson_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson plan not found"
        )
    return lesson_plan


def _assert_lesson_plan_ownership(lesson_plan: LessonPlan, current_user: User) -> None:
    """Raise 403 if an educator tries to access another user's lesson plan."""
    if not _is_admin(current_user) and lesson_plan.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )


def _get_context_with_ownership(
    context_id: int, current_user: User, db: Session
) -> Context:
    """Fetch a context and verify ownership, raising 404 or 403 as appropriate."""
    context = db.query(Context).filter(Context.context_id == context_id).first()
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Context not found"
        )
    lesson_plan = _get_lesson_plan_or_404(context.lesson_plan_id, db)
    _assert_lesson_plan_ownership(lesson_plan, current_user)
    return context


@router.post("/", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_context(
    request: Request,
    context_data: ContextCreate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Create a new context for a lesson plan. Educators may only add contexts to their own lesson plans."""
    lesson_plan = _get_lesson_plan_or_404(context_data.lesson_plan_id, db)
    _assert_lesson_plan_ownership(lesson_plan, current_user)
    service = ContextService(db)
    return service.create_context(context_data)


@router.get("/lesson-plan/{lesson_plan_id}", response_model=ContextListResponse)
@limiter.limit("60/minute")
async def get_contexts_by_lesson_plan(
    request: Request,
    lesson_plan_id: int,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Get all contexts for a specific lesson plan. Educators may only access their own lesson plans."""
    lesson_plan = _get_lesson_plan_or_404(lesson_plan_id, db)
    _assert_lesson_plan_ownership(lesson_plan, current_user)
    service = ContextService(db)
    return service.get_contexts_by_lesson_plan(lesson_plan_id)


@router.get("/", response_model=List[ContextResponse])
@limiter.limit("60/minute")
async def get_all_contexts(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Get contexts with pagination.
    Admins receive all contexts; educators receive only contexts for their own lesson plans."""
    service = ContextService(db)
    if _is_admin(current_user):
        return service.get_all_contexts(skip, limit)
    return service.get_contexts_for_user(current_user.user_id, skip, limit)


@router.get("/{context_id}", response_model=ContextResponse)
@limiter.limit("60/minute")
async def get_context(
    request: Request,
    context_id: int,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Get a specific context by ID. Educators may only access contexts for their own lesson plans."""
    _get_context_with_ownership(context_id, current_user, db)
    service = ContextService(db)
    return service.get_context(context_id)


@router.put("/{context_id}", response_model=ContextResponse)
@limiter.limit("30/minute")
async def update_context(
    request: Request,
    context_id: int,
    context_data: ContextUpdate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Update a specific context. Educators may only update contexts for their own lesson plans."""
    _get_context_with_ownership(context_id, current_user, db)
    service = ContextService(db)
    return service.update_context(context_id, context_data)


@router.delete("/{context_id}")
@limiter.limit("30/minute")
async def delete_context(
    request: Request,
    context_id: int,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Delete a specific context. Educators may only delete contexts for their own lesson plans."""
    _get_context_with_ownership(context_id, current_user, db)
    service = ContextService(db)
    return service.delete_context(context_id)


@router.post(
    "/lesson-plan/{lesson_plan_id}/submit",
    response_model=ContextResponse,
    status_code=status.HTTP_201_CREATED
)
@limiter.limit("30/minute")
async def submit_context(
    request: Request,
    lesson_plan_id: int,
    context_data: ContextSubmissionRequest,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """Submit context for a lesson plan (frontend endpoint).
    Educators may only submit contexts for their own lesson plans."""
    lesson_plan = _get_lesson_plan_or_404(lesson_plan_id, db)
    _assert_lesson_plan_ownership(lesson_plan, current_user)
    context_create_data = ContextCreate(
        lesson_plan_id=lesson_plan_id,
        context_text=context_data.context_text,
        context_type=context_data.context_type
    )
    service = ContextService(db)
    return service.create_context(context_create_data)
