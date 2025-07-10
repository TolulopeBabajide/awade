"""
Curriculum mapping service for Awade.
Maps subjects and grade levels to curriculum standards.
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import Depends
from ..models import CurriculumMap
from ..database import get_db

class CurriculumService:
    """Service for curriculum mapping and standards lookup."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def map_curriculum(self, subject: str, grade_level: str, country: Optional[str] = None) -> Optional[CurriculumMap]:
        """
        Map subject and grade level to curriculum standards.
        
        Args:
            subject: Subject area (e.g., "Mathematics", "Science")
            grade_level: Grade level (e.g., "Grade 4", "Grade 7")
            country: Country for country-specific curricula (optional)
            
        Returns:
            CurriculumMap object or None if not found
        """
        query = self.db.query(CurriculumMap).filter(
            CurriculumMap.subject.ilike(f"%{subject}%"),
            CurriculumMap.grade_level == grade_level
        )
        
        if country:
            query = query.filter(CurriculumMap.country == country)
        
        return query.first()
    
    def get_curriculum_standards(self, subject: str, grade_level: str) -> List[Dict]:
        """
        Get all curriculum standards for a subject and grade level.
        
        Args:
            subject: Subject area
            grade_level: Grade level
            
        Returns:
            List of curriculum standards
        """
        standards = self.db.query(CurriculumMap).filter(
            CurriculumMap.subject.ilike(f"%{subject}%"),
            CurriculumMap.grade_level == grade_level
        ).all()
        
        return [
            {
                "curriculum_id": std.curriculum_id,
                "subject": std.subject,
                "grade_level": std.grade_level,
                "curriculum_standard": std.curriculum_standard,
                "description": std.description,
                "country": std.country
            }
            for std in standards
        ]
    
    def add_curriculum_standard(
        self,
        subject: str,
        grade_level: str,
        curriculum_standard: str,
        description: str,
        country: Optional[str] = None
    ) -> CurriculumMap:
        """
        Add a new curriculum standard.
        
        Args:
            subject: Subject area
            grade_level: Grade level
            curriculum_standard: The curriculum standard
            description: Description of the standard
            country: Country for country-specific curricula
            
        Returns:
            Created CurriculumMap object
        """
        curriculum = CurriculumMap(
            subject=subject,
            grade_level=grade_level,
            curriculum_standard=curriculum_standard,
            description=description,
            country=country
        )
        
        self.db.add(curriculum)
        self.db.commit()
        self.db.refresh(curriculum)
        
        return curriculum
    
    def get_subjects(self) -> List[str]:
        """Get all available subjects."""
        subjects = self.db.query(CurriculumMap.subject).distinct().all()
        return [subject[0] for subject in subjects]
    
    def get_grade_levels(self, subject: Optional[str] = None) -> List[str]:
        """Get all available grade levels for a subject."""
        query = self.db.query(CurriculumMap.grade_level).distinct()
        
        if subject:
            query = query.filter(CurriculumMap.subject.ilike(f"%{subject}%"))
        
        grades = query.all()
        return [grade[0] for grade in grades]

def get_curriculum_service(db: Session = Depends(get_db)) -> CurriculumService:
    """Dependency to get curriculum service."""
    return CurriculumService(db) 