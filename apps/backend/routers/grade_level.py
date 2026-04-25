"""
Grade Level Router for Awade API

This module provides endpoints for managing grade level data, including CRUD operations
and grade level information retrieval. It delegates business logic to the GradeLevelService
for clean separation of concerns.

Endpoints:
- /api/grade-levels: CRUD for grade levels
- /api/grade-levels/search: Search grade levels
- /api/grade-levels/curriculum/{curriculum_id}: Get grade levels by curriculum
- /api/grade-levels/subject/{subject_id}: Get grade levels by subject

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator
from apps.backend.services.grade_level_service import GradeLevelService
from apps.backend.schemas.grade_level import GradeLevelCreate, GradeLevelResponse, GradeLevelUpdate
from apps.backend.models import User

router = APIRouter(prefix="/api/grade-levels", tags=["grade-levels"])

@router.get("/", response_model=List[GradeLevelResponse])
def list_grade_levels(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all grade levels with pagination.
    Requires authentication.
    """
    service = GradeLevelService(db)
    return service.get_grade_levels(skip, limit)

@router.post("/", response_model=GradeLevelResponse)
def create_grade_level(
    grade_level: GradeLevelCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new grade level record.
    Requires admin authentication.
    """
    service = GradeLevelService(db)
    return service.create_grade_level(grade_level)

@router.get("/{grade_level_id}", response_model=GradeLevelResponse)
def get_grade_level(
    grade_level_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific grade level by ID.
    Requires authentication.
    """
    service = GradeLevelService(db)
    return service.get_grade_level(grade_level_id)

@router.put("/{grade_level_id}", response_model=GradeLevelResponse)
def update_grade_level(
    grade_level_id: int,
    grade_level: GradeLevelUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a grade level record.
    Requires admin authentication.
    """
    service = GradeLevelService(db)
    return service.update_grade_level(grade_level_id, grade_level)

@router.delete("/{grade_level_id}")
def delete_grade_level(
    grade_level_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a grade level record.
    Requires admin authentication.
    """
    service = GradeLevelService(db)
    return service.delete_grade_level(grade_level_id)

@router.get("/search", response_model=List[GradeLevelResponse])
def search_grade_levels(
    q: str = Query(..., description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search grade levels by name.
    Requires authentication.
    """
    service = GradeLevelService(db)
    return service.search_grade_levels(q, skip, limit)

@router.get("/curriculum/{curriculum_id}", response_model=List[GradeLevelResponse])
def get_grade_levels_by_curriculum(
    curriculum_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get grade levels by curriculum.
    Requires authentication.
    """
    service = GradeLevelService(db)
    return service.get_grade_levels_by_curriculum(curriculum_id, skip, limit)

@router.get("/subject/{subject_id}", response_model=List[GradeLevelResponse])
def get_grade_levels_by_subject(
    subject_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get grade levels by subject.
    Requires authentication.
    """
    service = GradeLevelService(db)
    return service.get_grade_levels_by_subject(subject_id, skip, limit) 