"""
Subject Router for Awade API

This module provides endpoints for managing subject data, including CRUD operations
and subject information retrieval. It delegates business logic to the SubjectService
for clean separation of concerns.

Endpoints:
- /api/subjects: CRUD for subjects
- /api/subjects/search: Search subjects
- /api/subjects/curriculum/{curriculum_id}: Get subjects by curriculum

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator
from apps.backend.services.subject_service import SubjectService
from apps.backend.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from apps.backend.models import User

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

@router.get("/", response_model=List[SubjectResponse])
def list_subjects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all subjects with pagination.
    Requires authentication.
    """
    service = SubjectService(db)
    return service.get_subjects(skip, limit)

@router.post("/", response_model=SubjectResponse)
def create_subject(
    subject: SubjectCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new subject record.
    Requires admin authentication.
    """
    service = SubjectService(db)
    return service.create_subject(subject)

@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific subject by ID.
    Requires authentication.
    """
    service = SubjectService(db)
    return service.get_subject(subject_id)

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject: SubjectUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a subject record.
    Requires admin authentication.
    """
    service = SubjectService(db)
    return service.update_subject(subject_id, subject)

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a subject record.
    Requires admin authentication.
    """
    service = SubjectService(db)
    return service.delete_subject(subject_id)

@router.get("/search", response_model=List[SubjectResponse])
def search_subjects(
    q: str = Query(..., description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search subjects by name.
    Requires authentication.
    """
    service = SubjectService(db)
    return service.search_subjects(q, skip, limit)

@router.get("/curriculum/{curriculum_id}", response_model=List[SubjectResponse])
def get_subjects_by_curriculum(
    curriculum_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get subjects by curriculum.
    Requires authentication.
    """
    service = SubjectService(db)
    return service.get_subjects_by_curriculum(curriculum_id, skip, limit) 