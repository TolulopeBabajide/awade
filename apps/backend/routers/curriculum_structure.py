from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import literal, select, union_all
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import List, Optional
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator
from apps.backend.limiter import limiter
from apps.backend.models import CurriculumStructure, Curriculum, GradeLevel, Subject, User
from apps.backend.schemas.curriculum_structure import CurriculumStructureCreate, CurriculumStructureResponse

router = APIRouter(prefix="/api/curriculum-structures", tags=["curriculum-structures"])


def _validate_fk_targets(
    db: Session,
    curricula_id: int,
    grade_level_id: int,
    subject_id: int,
) -> None:
    """
    Verify that the Curriculum, GradeLevel and Subject referenced by a curriculum
    structure all exist, in a single database round-trip (AWD-M-63).

    Replaces three sequential ``db.query(...).first()`` calls with one
    ``UNION ALL`` query whose result set names the entities found. Same 404
    responses as the previous implementation; ordering matches: curriculum
    first, then grade level, then subject.
    """
    rows = db.execute(
        union_all(
            select(literal("curriculum").label("entity"))
            .select_from(Curriculum)
            .where(Curriculum.curricula_id == curricula_id),
            select(literal("grade_level").label("entity"))
            .select_from(GradeLevel)
            .where(GradeLevel.grade_level_id == grade_level_id),
            select(literal("subject").label("entity"))
            .select_from(Subject)
            .where(Subject.subject_id == subject_id),
        )
    ).fetchall()
    found = {row[0] for row in rows}

    if "curriculum" not in found:
        raise HTTPException(status_code=404, detail="Curriculum not found")
    if "grade_level" not in found:
        raise HTTPException(status_code=404, detail="Grade level not found")
    if "subject" not in found:
        raise HTTPException(status_code=404, detail="Subject not found")

@router.get("/", response_model=List[CurriculumStructureResponse])
@limiter.limit("60/minute")
def list_curriculum_structures(
    request: Request,
    curricula_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of curriculum structures, optionally filtered by curricula_id.
    Requires authentication.
    """
    query = db.query(CurriculumStructure)
    if curricula_id:
        query = query.filter(CurriculumStructure.curricula_id == curricula_id)
    return query.all()

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
    # Validate FK targets in a single round-trip (AWD-M-63)
    _validate_fk_targets(
        db,
        structure.curricula_id,
        structure.grade_level_id,
        structure.subject_id,
    )

    # Check if curriculum structure already exists
    existing_structure = db.query(CurriculumStructure).filter(
        CurriculumStructure.curricula_id == structure.curricula_id,
        CurriculumStructure.grade_level_id == structure.grade_level_id,
        CurriculumStructure.subject_id == structure.subject_id
    ).first()
    if existing_structure:
        raise HTTPException(status_code=400, detail="Curriculum structure already exists")
    
    db_structure = CurriculumStructure(**structure.model_dump())
    db.add(db_structure)
    db.commit()
    db.refresh(db_structure)
    return db_structure

@router.get("/{structure_id}", response_model=CurriculumStructureResponse)
@limiter.limit("60/minute")
def get_curriculum_structure(
    request: Request,
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

    # Validate FK targets in a single round-trip (AWD-M-63)
    _validate_fk_targets(
        db,
        structure.curricula_id,
        structure.grade_level_id,
        structure.subject_id,
    )

    # Check if new structure conflicts with existing one
    existing_structure = db.query(CurriculumStructure).filter(
        CurriculumStructure.curricula_id == structure.curricula_id,
        CurriculumStructure.grade_level_id == structure.grade_level_id,
        CurriculumStructure.subject_id == structure.subject_id,
        CurriculumStructure.curriculum_structure_id != structure_id
    ).first()
    if existing_structure:
        raise HTTPException(status_code=400, detail="Curriculum structure already exists")
    
    for key, value in structure.model_dump().items():
        setattr(db_structure, key, value)
    
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
    

    try:
        db.delete(db_structure)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete — this curriculum structure has associated records.",
        )
    return {"message": "Curriculum structure deleted successfully"}