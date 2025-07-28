from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator, get_optional_current_user
from apps.backend.models import CurriculumStructure, Curriculum, GradeLevel, Subject, User
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
def list_curriculum_structures(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all curriculum structures.
    Requires authentication.
    """
    return db.query(CurriculumStructure).all()

@router.post("/", response_model=CurriculumStructureResponse)
def create_curriculum_structure(
    structure: CurriculumStructureCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new curriculum structure record.
    Requires admin authentication.
    """
    # Validate that curriculum exists
    curriculum = db.query(Curriculum).filter(Curriculum.curricula_id == structure.curricula_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Validate that grade level exists
    grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == structure.grade_level_id).first()
    if not grade_level:
        raise HTTPException(status_code=404, detail="Grade level not found")
    
    # Validate that subject exists
    subject = db.query(Subject).filter(Subject.subject_id == structure.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check if curriculum structure already exists
    existing_structure = db.query(CurriculumStructure).filter(
        CurriculumStructure.curricula_id == structure.curricula_id,
        CurriculumStructure.grade_level_id == structure.grade_level_id,
        CurriculumStructure.subject_id == structure.subject_id
    ).first()
    if existing_structure:
        raise HTTPException(status_code=400, detail="Curriculum structure already exists")
    
    db_structure = CurriculumStructure(**structure.dict())
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure

@router.get("/{structure_id}", response_model=CurriculumStructureResponse)
def get_curriculum_structure(
    structure_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific curriculum structure by ID.
    Requires authentication.
    """
    structure = db.query(CurriculumStructure).filter(CurriculumStructure.curriculum_structure_id == structure_id).first()
    if not structure:
        raise HTTPException(status_code=404, detail="Curriculum structure not found")
    return structure

@router.put("/{structure_id}", response_model=CurriculumStructureResponse)
def update_curriculum_structure(
    structure_id: int,
    structure: CurriculumStructureCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a curriculum structure record.
    Requires admin authentication.
    """
    db_structure = db.query(CurriculumStructure).filter(CurriculumStructure.curriculum_structure_id == structure_id).first()
    if not db_structure:
        raise HTTPException(status_code=404, detail="Curriculum structure not found")
    
    # Validate that curriculum exists
    curriculum = db.query(Curriculum).filter(Curriculum.curricula_id == structure.curricula_id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    
    # Validate that grade level exists
    grade_level = db.query(GradeLevel).filter(GradeLevel.grade_level_id == structure.grade_level_id).first()
    if not grade_level:
        raise HTTPException(status_code=404, detail="Grade level not found")
    
    # Validate that subject exists
    subject = db.query(Subject).filter(Subject.subject_id == structure.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check if new structure conflicts with existing one
    existing_structure = db.query(CurriculumStructure).filter(
        CurriculumStructure.curricula_id == structure.curricula_id,
        CurriculumStructure.grade_level_id == structure.grade_level_id,
        CurriculumStructure.subject_id == structure.subject_id,
        CurriculumStructure.curriculum_structure_id != structure_id
    ).first()
    if existing_structure:
        raise HTTPException(status_code=400, detail="Curriculum structure already exists")
    
    # Update fields
    db_structure.curricula_id = structure.curricula_id
    db_structure.grade_level_id = structure.grade_level_id
    db_structure.subject_id = structure.subject_id
    
    db.commit()
    db.refresh(db_structure)
    return db_structure

@router.delete("/{structure_id}")
def delete_curriculum_structure(
    structure_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a curriculum structure record.
    Requires admin authentication.
    """
    db_structure = db.query(CurriculumStructure).filter(CurriculumStructure.curriculum_structure_id == structure_id).first()
    if not db_structure:
        raise HTTPException(status_code=404, detail="Curriculum structure not found")
    
    # Check if structure is being used by topics
    if db_structure.topics:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete curriculum structure that has associated topics"
        )
    
    db.delete(db_structure)
    db.commit()
    return {"message": "Curriculum structure deleted successfully"} 