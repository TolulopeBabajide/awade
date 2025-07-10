"""
Curriculum router for managing curriculum standards and mapping.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from apps.backend.database import get_db
from apps.backend.services.curriculum_service import CurriculumService, get_curriculum_service
from apps.backend.schemas.lesson_plans import CurriculumMapResponse

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])

@router.get("/map")
async def map_curriculum(
    subject: str,
    grade_level: str,
    country: Optional[str] = None,
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """
    Map subject and grade level to curriculum standards.
    """
    curriculum = curriculum_service.map_curriculum(subject, grade_level, country)
    
    if not curriculum:
        raise HTTPException(
            status_code=404,
            detail=f"No curriculum standards found for {subject} - {grade_level}"
        )
    
    return CurriculumMapResponse.from_orm(curriculum)

@router.get("/standards")
async def get_curriculum_standards(
    subject: str,
    grade_level: str,
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """
    Get all curriculum standards for a subject and grade level.
    """
    standards = curriculum_service.get_curriculum_standards(subject, grade_level)
    return standards

@router.post("/standards")
async def add_curriculum_standard(
    subject: str,
    grade_level: str,
    curriculum_standard: str,
    description: str,
    country: Optional[str] = None,
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """
    Add a new curriculum standard.
    """
    curriculum = curriculum_service.add_curriculum_standard(
        subject=subject,
        grade_level=grade_level,
        curriculum_standard=curriculum_standard,
        description=description,
        country=country
    )
    
    return CurriculumMapResponse.from_orm(curriculum)

@router.get("/subjects")
async def get_subjects(
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """
    Get all available subjects.
    """
    subjects = curriculum_service.get_subjects()
    return {"subjects": subjects}

@router.get("/grade-levels")
async def get_grade_levels(
    subject: Optional[str] = None,
    curriculum_service: CurriculumService = Depends(get_curriculum_service)
):
    """
    Get all available grade levels, optionally filtered by subject.
    """
    grade_levels = curriculum_service.get_grade_levels(subject)
    return {"grade_levels": grade_levels} 