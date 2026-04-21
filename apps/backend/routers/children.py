"""
Children Router for Awade API

This module provides endpoints for managing child profiles and parent guides.
Parents can add children, view their curriculum topics, and access saved guides.

Endpoints:
- POST   /api/children              — Create a child profile
- GET    /api/children              — List all children for the current parent
- GET    /api/children/{child_id}   — Get a single child profile
- PUT    /api/children/{child_id}   — Update a child profile
- DELETE /api/children/{child_id}   — Delete a child profile
- GET    /api/children/{child_id}/topics  — Get curriculum topics for a child
- GET    /api/children/{child_id}/guides  — List guides for a child
- GET    /api/guides/{guide_id}           — Get a single guide
- POST   /api/guides/{guide_id}/bookmark  — Toggle guide bookmark

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from apps.backend.database import get_db
from apps.backend.models import User
from apps.backend.dependencies import get_current_active_user
from apps.backend.schemas.children import (
    ChildProfileCreate,
    ChildProfileUpdate,
    ChildProfileResponse,
    ChildProfileListResponse,
    ParentGuideResponse,
    ParentGuideListResponse,
)
from apps.backend.services.children_service import ChildrenService

router = APIRouter(prefix="/api", tags=["children"])


# ── Child Profile CRUD ────────────────────────────────────────────────

@router.post("/children", response_model=ChildProfileResponse, status_code=201)
def create_child(
    data: ChildProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new child profile for the current parent."""
    service = ChildrenService(db)
    return service.create_child(current_user, data)


@router.get("/children", response_model=ChildProfileListResponse)
def list_children(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all child profiles for the current parent."""
    service = ChildrenService(db)
    return service.list_children(current_user)


@router.get("/children/{child_id}", response_model=ChildProfileResponse)
def get_child(
    child_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a single child profile by ID."""
    service = ChildrenService(db)
    return service.get_child(current_user, child_id)


@router.put("/children/{child_id}", response_model=ChildProfileResponse)
def update_child(
    child_id: int,
    data: ChildProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a child profile."""
    service = ChildrenService(db)
    return service.update_child(current_user, child_id, data)


@router.delete("/children/{child_id}")
def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a child profile and all associated guides."""
    service = ChildrenService(db)
    return service.delete_child(current_user, child_id)


# ── Child's Curriculum Topics ─────────────────────────────────────────

@router.get("/children/{child_id}/topics")
def get_child_topics(
    child_id: int,
    subject_id: Optional[int] = Query(None, description="Filter topics by subject ID"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get curriculum topics available for a child based on their
    curriculum and grade level. Optionally filter by subject.
    """
    service = ChildrenService(db)
    return service.get_child_topics(current_user, child_id, subject_id)


# ── Parent Guides ─────────────────────────────────────────────────────

@router.get("/children/{child_id}/guides", response_model=ParentGuideListResponse)
def list_child_guides(
    child_id: int,
    bookmarked: bool = Query(False, description="Only return bookmarked guides"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all parent guides for a child."""
    service = ChildrenService(db)
    return service.list_guides(current_user, child_id, bookmarked_only=bookmarked)


@router.post("/children/{child_id}/guides/generate", response_model=ParentGuideResponse, status_code=201)
def generate_guide(
    child_id: int,
    topic_id: int = Query(..., description="Topic ID to generate a guide for"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Generate (or retrieve existing) a 'How to Help' guide for a child and topic.
    If a guide already exists for this child+topic, returns the existing one.
    """
    service = ChildrenService(db)
    return service.generate_guide(current_user, child_id, topic_id)


@router.get("/guides/{guide_id}", response_model=ParentGuideResponse)
def get_guide(
    guide_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a single parent guide by ID."""
    service = ChildrenService(db)
    return service.get_guide(current_user, guide_id)


@router.post("/guides/{guide_id}/bookmark", response_model=ParentGuideResponse)
def toggle_bookmark(
    guide_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Toggle the bookmark status of a guide."""
    service = ChildrenService(db)
    return service.toggle_bookmark(current_user, guide_id)
