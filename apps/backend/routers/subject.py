from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from apps.backend.database import get_db
from apps.backend.models import Subject
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
def list_subjects(db: Session = Depends(get_db)):
    return db.query(Subject).all()

@router.post("/", response_model=SubjectResponse)
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    db_subject = Subject(**subject.dict())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject 