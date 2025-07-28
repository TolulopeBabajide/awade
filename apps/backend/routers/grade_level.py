from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator, get_optional_current_user
from apps.backend.models import GradeLevel, User
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
def list_grade_levels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all grade levels.
    Requires authentication.
    """
    return db.query(GradeLevel).all()

@router.post("/", response_model=GradeLevelResponse)
def create_grade_level(
    grade_level: GradeLevelCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new grade level.
    Requires admin authentication.
    """
    # Check if grade level already exists
    existing_grade_level = db.query(GradeLevel).filter(GradeLevel.name == grade_level.name).first()
    if existing_grade_level:
        raise HTTPException(status_code=400, detail="Grade level already exists")
    
    db_grade_level = GradeLevel(**grade_level.dict())
    db.add(db_grade_level)
    db.commit()
    db.refresh(db_grade_level)
    return db_grade_level

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
    grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == grade_level_id).first()
    if not grade_level:
        raise HTTPException(status_code=404, detail="Grade level not found")
    return grade_level

@router.put("/{grade_level_id}", response_model=GradeLevelResponse)
def update_grade_level(
    grade_level_id: int,
    grade_level: GradeLevelCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a grade level.
    Requires admin authentication.
    """
    db_grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == grade_level_id).first()
    if not db_grade_level:
        raise HTTPException(status_code=404, detail="Grade level not found")
    
    # Check if new name conflicts with existing grade level
    existing_grade_level = db.query(GradeLevel).filter(
        GradeLevel.name == grade_level.name,
        GradeLevel.grade_level_id != grade_level_id
    ).first()
    if existing_grade_level:
        raise HTTPException(status_code=400, detail="Grade level name already exists")
    
    # Update name
    db_grade_level.name = grade_level.name
    
    db.commit()
    db.refresh(db_grade_level)
    return db_grade_level

@router.delete("/{grade_level_id}")
def delete_grade_level(
    grade_level_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a grade level.
    Requires admin authentication.
    """
    db_grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == grade_level_id).first()
    if not db_grade_level:
        raise HTTPException(status_code=404, detail="Grade level not found")
    
    # Check if grade level is being used by curriculum structures
    if db_grade_level.curriculum_structures:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete grade level that has associated curriculum structures"
        )
    
    db.delete(db_grade_level)
    db.commit()
    return {"message": "Grade level deleted successfully"} 