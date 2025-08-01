from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator, get_optional_current_user
from apps.backend.models import Subject, User
from pydantic import BaseModel

router = APIRouter(prefix="/api/subjects", tags=["subjects"])

class SubjectCreate(BaseModel):
    name: str

class SubjectResponse(BaseModel):
    subject_id: int
    name: str
    class Config:
        orm_mode = True

@router.get("/", response_model=List[SubjectResponse])
def list_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of all subjects.
    Requires authentication.
    """
    return db.query(Subject).all()

@router.post("/", response_model=SubjectResponse)
def create_subject(
    subject: SubjectCreate, 
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Create a new subject.
    Requires admin authentication.
    """
    # Check if subject already exists
    existing_subject = db.query(Subject).filter(Subject.name == subject.name).first()
    if existing_subject:
        raise HTTPException(status_code=400, detail="Subject already exists")
    
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

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
    subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    subject: SubjectCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update a subject.
    Requires admin authentication.
    """
    db_subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check if new name conflicts with existing subject
    existing_subject = db.query(Subject).filter(
        Subject.name == subject.name,
        Subject.subject_id != subject_id
    ).first()
    if existing_subject:
        raise HTTPException(status_code=400, detail="Subject name already exists")
    
    # Update name
    db_subject.name = subject.name
    
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a subject.
    Requires admin authentication.
    """
    db_subject = db.query(Subject).filter(Subject.subject_id == subject_id).first()
    if not db_subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Check if subject is being used by curriculum structures
    if db_subject.curriculum_structures:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete subject that has associated curriculum structures"
        )
    
    db.delete(db_subject)
    db.commit()
    return {"message": "Subject deleted successfully"} 