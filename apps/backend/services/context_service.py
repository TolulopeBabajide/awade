"""
Context Service for Awade

This module provides service methods for managing context information for lesson plans,
including CRUD operations and context retrieval. It handles all business logic related
to contexts, separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status

from apps.backend.models import Context, LessonPlan
from apps.backend.schemas.contexts import (
    ContextCreate, 
    ContextUpdate, 
    ContextResponse, 
    ContextListResponse,
    ContextSubmissionRequest
)

class ContextService:
    """Service class for context operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the ContextService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def create_context(self, context_data: ContextCreate) -> ContextResponse:
        """
        Create a new context for a lesson plan.
        
        Args:
            context_data (ContextCreate): Context creation data
            
        Returns:
            ContextResponse: Created context response
            
        Raises:
            HTTPException: If lesson plan not found or creation fails
        """
        try:
            # Verify lesson plan exists
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == context_data.lesson_plan_id
            ).first()
            if not lesson_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson plan not found"
                )
            
            # Create new context
            context = Context(
                lesson_plan_id=context_data.lesson_plan_id,
                context_text=context_data.context_text,
                context_type=context_data.context_type,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            self.db.add(context)
            self.db.commit()
            self.db.refresh(context)
            
            return self._create_context_response(context)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while creating the context: {str(e)}"
            )
    
    def get_contexts_by_lesson_plan(self, lesson_plan_id: int) -> ContextListResponse:
        """
        Get all contexts for a specific lesson plan.
        
        Args:
            lesson_plan_id (int): Lesson plan ID
            
        Returns:
            ContextListResponse: List of contexts with total count
            
        Raises:
            HTTPException: If lesson plan not found
        """
        try:
            # Verify lesson plan exists
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == lesson_plan_id
            ).first()
            if not lesson_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lesson plan not found"
                )
            
            contexts = self.db.query(Context).filter(
                Context.lesson_plan_id == lesson_plan_id
            ).all()
            
            return ContextListResponse(
                contexts=[self._create_context_response(context) for context in contexts],
                total=len(contexts)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving contexts: {str(e)}"
            )
    
    def get_context(self, context_id: int) -> ContextResponse:
        """
        Get a specific context by ID.
        
        Args:
            context_id (int): Context ID
            
        Returns:
            ContextResponse: Context response
            
        Raises:
            HTTPException: If context not found
        """
        try:
            context = self.db.query(Context).filter(Context.context_id == context_id).first()
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Context not found"
                )
            
            return self._create_context_response(context)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving the context: {str(e)}"
            )
    
    def update_context(self, context_id: int, context_data: ContextUpdate) -> ContextResponse:
        """
        Update a specific context.
        
        Args:
            context_id (int): Context ID
            context_data (ContextUpdate): Update data
            
        Returns:
            ContextResponse: Updated context response
            
        Raises:
            HTTPException: If context not found or update fails
        """
        try:
            context = self.db.query(Context).filter(Context.context_id == context_id).first()
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Context not found"
                )
            
            # Update context fields
            update_data = context_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(context, field, value)
            
            # Update timestamp
            context.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(context)
            
            return self._create_context_response(context)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the context: {str(e)}"
            )
    
    def delete_context(self, context_id: int) -> dict:
        """
        Delete a specific context.
        
        Args:
            context_id (int): Context ID
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If context not found or deletion fails
        """
        try:
            context = self.db.query(Context).filter(Context.context_id == context_id).first()
            if not context:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Context not found"
                )
            
            self.db.delete(context)
            self.db.commit()
            
            return {"message": "Context deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while deleting the context: {str(e)}"
            )
    
    def get_all_contexts(self, skip: int = 0, limit: int = 100) -> List[ContextResponse]:
        """
        Get all contexts with pagination.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[ContextResponse]: List of context responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            contexts = self.db.query(Context).offset(skip).limit(limit).all()
            return [self._create_context_response(context) for context in contexts]
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving contexts: {str(e)}"
            )
    
    def _create_context_response(self, context: Context) -> ContextResponse:
        """
        Create a context response from a Context model.
        
        Args:
            context (Context): Context model instance
            
        Returns:
            ContextResponse: Context response object
        """
        try:
            return ContextResponse(
                context_id=context.context_id,
                lesson_plan_id=context.lesson_plan_id,
                context_text=context.context_text,
                context_type=context.context_type,
                created_at=context.created_at,
                updated_at=context.updated_at
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating context response: {str(e)}"
            )
