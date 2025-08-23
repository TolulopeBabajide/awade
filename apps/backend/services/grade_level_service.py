"""
Grade Level Service for Awade

This module provides service methods for managing grade level data, including CRUD operations
and grade level information retrieval. It handles all business logic related to grade levels,
separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

from apps.backend.models import GradeLevel
from apps.backend.schemas.grade_level import GradeLevelCreate, GradeLevelResponse, GradeLevelUpdate

class GradeLevelService:
    """Service class for grade level operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the GradeLevelService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def get_grade_levels(self, skip: int = 0, limit: int = 100) -> List[GradeLevelResponse]:
        """
        Get all grade levels with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[GradeLevelResponse]: List of grade level responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            grade_levels = self.db.query(GradeLevel).offset(skip).limit(limit).all()
            return [self._create_grade_level_response(grade_level) for grade_level in grade_levels]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving grade levels: {str(e)}"
            )
    
    def get_grade_level(self, grade_level_id: int) -> GradeLevelResponse:
        """
        Get a specific grade level by ID.
        
        Args:
            grade_level_id (int): Grade level ID
            
        Returns:
            GradeLevelResponse: Grade level response
            
        Raises:
            HTTPException: If grade level not found
        """
        try:
            grade_level = self.db.query(GradeLevel).filter(
                GradeLevel.grade_level_id == grade_level_id
            ).first()
            if not grade_level:
                raise HTTPException(status_code=404, detail="Grade level not found")
            
            return self._create_grade_level_response(grade_level)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving the grade level: {str(e)}"
            )
    
    def create_grade_level(self, grade_level_data: GradeLevelCreate) -> GradeLevelResponse:
        """
        Create a new grade level record.
        
        Args:
            grade_level_data (GradeLevelCreate): Grade level creation data
            
        Returns:
            GradeLevelResponse: Created grade level response
            
        Raises:
            HTTPException: If grade level already exists or creation fails
        """
        try:
            # Check if grade level already exists
            existing_grade_level = self.db.query(GradeLevel).filter(
                GradeLevel.name == grade_level_data.name
            ).first()
            if existing_grade_level:
                raise HTTPException(status_code=400, detail="Grade level already exists")
            
            # Create new grade level
            grade_level = GradeLevel(**grade_level_data.dict())
            self.db.add(grade_level)
            self.db.commit()
            self.db.refresh(grade_level)
            
            return self._create_grade_level_response(grade_level)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while creating the grade level: {str(e)}"
            )
    
    def update_grade_level(self, grade_level_id: int, grade_level_data: GradeLevelUpdate) -> GradeLevelResponse:
        """
        Update a grade level record.
        
        Args:
            grade_level_id (int): Grade level ID
            grade_level_data (GradeLevelUpdate): Update data
            
        Returns:
            GradeLevelResponse: Updated grade level response
            
        Raises:
            HTTPException: If grade level not found or update fails
        """
        try:
            grade_level = self.db.query(GradeLevel).filter(
                GradeLevel.grade_level_id == grade_level_id
            ).first()
            if not grade_level:
                raise HTTPException(status_code=404, detail="Grade level not found")
            
            # Check if new name conflicts with existing grade level
            if grade_level_data.name:
                existing_grade_level = self.db.query(GradeLevel).filter(
                    GradeLevel.name == grade_level_data.name,
                    GradeLevel.grade_level_id != grade_level_id
                ).first()
                if existing_grade_level:
                    raise HTTPException(status_code=400, detail="Grade level name already exists")
            
            # Update fields
            update_data = grade_level_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(grade_level, field, value)
            
            self.db.commit()
            self.db.refresh(grade_level)
            
            return self._create_grade_level_response(grade_level)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the grade level: {str(e)}"
            )
    
    def delete_grade_level(self, grade_level_id: int) -> dict:
        """
        Delete a grade level record.
        
        Args:
            grade_level_id (int): Grade level ID
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If grade level not found or deletion fails
        """
        try:
            grade_level = self.db.query(GradeLevel).filter(
                GradeLevel.grade_level_id == grade_level_id
            ).first()
            if not grade_level:
                raise HTTPException(status_code=404, detail="Grade level not found")
            
            # Check if grade level is referenced by other entities
            # This would need to be implemented based on your database constraints
            
            self.db.delete(grade_level)
            self.db.commit()
            
            return {"message": "Grade level deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while deleting the grade level: {str(e)}"
            )
    
    def search_grade_levels(self, search_term: str, skip: int = 0, limit: int = 100) -> List[GradeLevelResponse]:
        """
        Search grade levels by name.
        
        Args:
            search_term (str): Search term
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[GradeLevelResponse]: List of matching grade level responses
            
        Raises:
            HTTPException: If search fails
        """
        try:
            grade_levels = self.db.query(GradeLevel).filter(
                GradeLevel.name.ilike(f"%{search_term}%")
            ).offset(skip).limit(limit).all()
            
            return [self._create_grade_level_response(grade_level) for grade_level in grade_levels]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while searching grade levels: {str(e)}"
            )
    
    def get_grade_levels_by_curriculum(self, curriculum_id: int, skip: int = 0, limit: int = 100) -> List[GradeLevelResponse]:
        """
        Get grade levels by curriculum.
        
        Args:
            curriculum_id (int): Curriculum ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[GradeLevelResponse]: List of grade level responses in the curriculum
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            from apps.backend.models import CurriculumStructure
            
            grade_levels = self.db.query(GradeLevel).join(CurriculumStructure).filter(
                CurriculumStructure.curricula_id == curriculum_id
            ).distinct().offset(skip).limit(limit).all()
            
            return [self._create_grade_level_response(grade_level) for grade_level in grade_levels]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving grade levels by curriculum: {str(e)}"
            )
    
    def get_grade_levels_by_subject(self, subject_id: int, skip: int = 0, limit: int = 100) -> List[GradeLevelResponse]:
        """
        Get grade levels by subject.
        
        Args:
            subject_id (int): Subject ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[GradeLevelResponse]: List of grade level responses for the subject
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            from apps.backend.models import CurriculumStructure
            
            grade_levels = self.db.query(GradeLevel).join(CurriculumStructure).filter(
                CurriculumStructure.subject_id == subject_id
            ).distinct().offset(skip).limit(limit).all()
            
            return [self._create_grade_level_response(grade_level) for grade_level in grade_levels]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving grade levels by subject: {str(e)}"
            )
    
    def _create_grade_level_response(self, grade_level: GradeLevel) -> GradeLevelResponse:
        """
        Create a grade level response from a GradeLevel model.
        
        Args:
            grade_level (GradeLevel): Grade level model instance
            
        Returns:
            GradeLevelResponse: Grade level response object
        """
        try:
            return GradeLevelResponse(
                grade_level_id=grade_level.grade_level_id,
                name=grade_level.name
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating grade level response: {str(e)}"
            )
