from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apps.backend.database import get_db
from apps.backend.models import CurriculumStructure, Curriculum, GradeLevel, Subject
from pydantic import BaseModel

router = APIRouter(prefix="/api/curriculum-structures", tags=["curriculum-structures"])

class CurriculumStructureCreate(BaseModel):
    """Schema for creating a new curriculum structure."""
    curricula_id: int
    grade_level_id: int
    subject_id: int

class CurriculumStructureResponse(BaseModel):
    """Schema for curriculum structure response data."""
    curriculum_structure_id: int
    curricula_id: int
    grade_level_id: int
    subject_id: int
    class Config:
        """Pydantic configuration for ORM mode."""
        orm_mode = True

@router.get("/", response_model=List[CurriculumStructureResponse])
def list_curriculum_structures(db: Session = Depends(get_db)):
    """
    Retrieve a list of all curriculum structures.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[CurriculumStructureResponse]: List of curriculum structures.
    """
    return db.query(CurriculumStructure).all()

@router.post("/", response_model=CurriculumStructureResponse)
def create_curriculum_structure(structure: CurriculumStructureCreate, db: Session = Depends(get_db)):
    """
    Create a new curriculum structure record.

    Args:
        structure (CurriculumStructureCreate): The curriculum structure data to create.
        db (Session): Database session dependency.

    Returns:
        CurriculumStructureResponse: The created curriculum structure.
    """
    db_structure = CurriculumStructure(**structure.dict())
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure 