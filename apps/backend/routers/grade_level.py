from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apps.backend.database import get_db
from apps.backend.models import GradeLevel
from pydantic import BaseModel

router = APIRouter(prefix="/api/grade-levels", tags=["grade-levels"])

class GradeLevelCreate(BaseModel):
    name: str

class GradeLevelResponse(BaseModel):
    grade_level_id: int
    name: str
    class Config:
        orm_mode = True

@router.get("/", response_model=List[GradeLevelResponse])
def list_grade_levels(db: Session = Depends(get_db)):
    """
    Retrieve a list of all grade levels.

    Args:
        db (Session): Database session dependency.

    Returns:
        List[GradeLevelResponse]: List of grade levels.
    """
    return db.query(GradeLevel).all()

@router.post("/", response_model=GradeLevelResponse)
def create_grade_level(grade_level: GradeLevelCreate, db: Session = Depends(get_db)):
    """
    Create a new grade level.

    Args:
        grade_level (GradeLevelCreate): The grade level data to create.
        db (Session): Database session dependency.

    Returns:
        GradeLevelResponse: The created grade level.
    """
    db_grade_level = GradeLevel(**grade_level.dict())
    db.add(db_grade_level)
    db.commit()
    db.refresh(db_grade_level)
    return db_grade_level 