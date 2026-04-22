"""
Subject Service for Awade

This module provides service methods for managing subject data, including CRUD operations
and subject information retrieval. It handles all business logic related to subjects,
separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])
from apps.backend.models import Subject
import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])
from apps.backend.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate

class SubjectService:
    """Service class for subject operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the SubjectService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def get_subjects(self, skip: int = 0, limit: int = 100) -> List[SubjectResponse]:
        """
        Get all subjects with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[SubjectResponse]: List of subject responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            subjects = self.db.query(Subject).offset(skip).limit(limit).all()
            return [self._create_subject_response(subject) for subject in subjects]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving subjects: {str(e)}"
            )
    
    def get_subject(self, subject_id: int) -> SubjectResponse:
        """
        Get a specific subject by ID.
        
        Args:
            subject_id (int): Subject ID
            
        Returns:
            SubjectResponse: Subject response
            
        Raises:
            HTTPException: If subject not found
        """
        try:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")
            
            return self._create_subject_response(subject)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving the subject: {str(e)}"
            )
    
    def create_subject(self, subject_data: SubjectCreate) -> SubjectResponse:
        """
        Create a new subject record.
        
        Args:
            subject_data (SubjectCreate): Subject creation data
            
        Returns:
            SubjectResponse: Created subject response
            
        Raises:
            HTTPException: If subject already exists or creation fails
        """
        try:
            # Check if subject already exists
            existing_subject = self.db.query(Subject).filter(
                Subject.name == subject_data.name
            ).first()
            if existing_subject:
                raise HTTPException(status_code=400, detail="Subject already exists")
            
            # Create new subject
            subject = Subject(**subject_data.dict())
            self.db.add(subject)
            self.db.commit()
            self.db.refresh(subject)
            
            return self._create_subject_response(subject)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while creating the subject: {str(e)}"
            )
    
    def update_subject(self, subject_id: int, subject_data: SubjectUpdate) -> SubjectResponse:
        """
        Update a subject record.
        
        Args:
            subject_id (int): Subject ID
            subject_data (SubjectUpdate): Update data
            
        Returns:
            SubjectResponse: Updated subject response
            
        Raises:
            HTTPException: If subject not found or update fails
        """
        try:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")
            
            # Check if new name conflicts with existing subject
            if subject_data.name:
                existing_subject = self.db.query(Subject).filter(
                    Subject.name == subject_data.name,
                    Subject.subject_id != subject_id
                ).first()
                if existing_subject:
                    raise HTTPException(status_code=400, detail="Subject name already exists")
            
            # Update fields
            update_data = subject_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(subject, field, value)
            
            self.db.commit()
            self.db.refresh(subject)
            
            return self._create_subject_response(subject)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the subject: {str(e)}"
            )
    
    def delete_subject(self, subject_id: int) -> dict:
        """
        Delete a subject record.
        
        Args:
            subject_id (int): Subject ID
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If subject not found or deletion fails
        """
        try:
            subject = self.db.query(Subject).filter(Subject.subject_id == subject_id).first()
            if not subject:
                raise HTTPException(status_code=404, detail="Subject not found")
            
            # Check if subject is referenced by other entities
            # This would need to be implemented based on your database constraints
            
            self.db.delete(subject)
            self.db.commit()
            
            return {"message": "Subject deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while deleting the subject: {str(e)}"
            )
    
    def search_subjects(self, search_term: str, skip: int = 0, limit: int = 100) -> List[SubjectResponse]:
        """
        Search subjects by name.
        
        Args:
            search_term (str): Search term
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[SubjectResponse]: List of matching subject responses
            
        Raises:
            HTTPException: If search fails
        """
        try:
            subjects = self.db.query(Subject).filter(
                Subject.name.ilike(f"%{search_term}%")
            ).offset(skip).limit(limit).all()
            
            return [self._create_subject_response(subject) for subject in subjects]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while searching subjects: {str(e)}"
            )
    
    def get_subjects_by_curriculum(self, curriculum_id: int, skip: int = 0, limit: int = 100) -> List[SubjectResponse]:
        """
        Get subjects by curriculum.
        
        Args:
            curriculum_id (int): Curriculum ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[SubjectResponse]: List of subject responses in the curriculum
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            from apps.backend.models import CurriculumStructure
            
            subjects = self.db.query(Subject).join(CurriculumStructure).filter(
                CurriculumStructure.curricula_id == curriculum_id
            ).distinct().offset(skip).limit(limit).all()
            
            return [self._create_subject_response(subject) for subject in subjects]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving subjects by curriculum: {str(e)}"
            )
    
    def _create_subject_response(self, subject: Subject) -> SubjectResponse:
        """
        Create a subject response from a Subject model.
        
        Args:
            subject (Subject): Subject model instance
            
        Returns:
            SubjectResponse: Subject response object
        """
        try:
            return SubjectResponse(
                subject_id=subject.subject_id,
                name=subject.name
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating subject response: {str(e)}"
            )
