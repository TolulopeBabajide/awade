"""
Lesson Plan Service for Awade

This module provides service methods for managing lesson plans, including CRUD operations,
AI-powered generation, and resource management. It handles all business logic related
to lesson plans, separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, UTC
from fastapi import HTTPException, status

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])
from apps.backend.models import (
    LessonPlan, User, Topic, CurriculumStructure, Curriculum, Country, 
    GradeLevel, Subject, LessonResource, LessonStatus, UserRole, Context
)
import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])
from apps.backend.schemas.lesson_plans import (
    LessonPlanCreate, LessonPlanResponse, LessonPlanUpdate,
    LessonResourceCreate, LessonResourceUpdate, LessonResourceResponse
)
from packages.ai.gpt_service import AwadeGPTService

class LessonPlanService:
    """Service class for lesson plan operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the LessonPlanService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def fetch_curriculum_data(self, topic_obj: Topic) -> tuple[List[str], List[str]]:
        """Helper function to fetch curriculum learning objectives and contents for a topic."""
        curriculum_learning_objectives = []
        curriculum_contents = []
        if topic_obj:
            curriculum_learning_objectives = [obj.objective for obj in topic_obj.learning_objectives]
            curriculum_contents = [content.content_area for content in topic_obj.topic_contents]
        return curriculum_learning_objectives, curriculum_contents
    
    def create_lesson_plan_response(self, lesson_plan: LessonPlan, request_data: Optional[LessonPlanCreate] = None) -> LessonPlanResponse:
        """Helper function to create a standardized lesson plan response."""
        try:
            # Fetch curriculum data
            curriculum_learning_objectives, curriculum_contents = self.fetch_curriculum_data(lesson_plan.topic)
            
            # Determine title, subject, grade_level, topic
            if request_data:
                # For new lesson plans from request data
                title = f"{request_data.subject}: {request_data.topic}"
                subject = request_data.subject
                grade_level = request_data.grade_level
                topic = request_data.topic
                author_id = request_data.user_id
                duration_minutes = getattr(request_data, 'duration_minutes', 45)
            else:
                # For existing lesson plans from database
                if not lesson_plan.topic:
                    raise ValueError("Lesson plan has no associated topic")
                    
                title = f"{lesson_plan.topic.curriculum_structure.subject.name}: {lesson_plan.topic.topic_title}" if lesson_plan.topic else "Untitled Lesson"
                subject = lesson_plan.topic.curriculum_structure.subject.name if lesson_plan.topic else "Unknown"
                grade_level = lesson_plan.topic.curriculum_structure.grade_level.name if lesson_plan.topic else "Unknown"
                topic = lesson_plan.topic.topic_title if lesson_plan.topic else None
                author_id = lesson_plan.user_id  # Use actual user_id from lesson plan
                duration_minutes = 45  # Default duration
            
            return LessonPlanResponse(
                lesson_id=lesson_plan.lesson_plan_id,
                title=title,
                subject=subject,
                grade_level=grade_level,
                topic=topic,
                author_id=author_id,
                duration_minutes=duration_minutes,
                created_at=lesson_plan.created_at,
                updated_at=lesson_plan.created_at,  # Using created_at as updated_at
                status=LessonStatus.DRAFT,
                curriculum_learning_objectives=curriculum_learning_objectives,
                curriculum_contents=curriculum_contents
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating lesson plan response: {str(e)}"
            )
    
    def generate_lesson_plan(self, request: LessonPlanCreate, current_user: User) -> LessonPlanResponse:
        """
        Generate a new lesson plan using AI.
        
        Args:
            request (LessonPlanCreate): Lesson plan creation request
            current_user (User): Current authenticated user
            
        Returns:
            LessonPlanResponse: Generated lesson plan response
            
        Raises:
            HTTPException: If topic not found or creation fails
        """
        try:
            # Use current user's ID as author
            request.user_id = current_user.user_id
            
            # Find topic based on curriculum structure
            topic = self.db.query(Topic).join(CurriculumStructure).join(Subject).join(GradeLevel).filter(
                Subject.name == request.subject,
                GradeLevel.name == request.grade_level,
                Topic.topic_title == request.topic
            ).first()
            
            if not topic:
                raise HTTPException(status_code=404, detail="Topic not found in curriculum")
            
            # Create lesson plan with user_id
            lesson_plan = LessonPlan(
                topic_id=topic.topic_id,
                user_id=current_user.user_id,
                created_at=datetime.now(UTC)
            )
            self.db.add(lesson_plan)
            self.db.commit()
            self.db.refresh(lesson_plan)
            
            return self.create_lesson_plan_response(lesson_plan, request)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while generating the lesson plan: {str(e)}"
            )
    
    def get_lesson_plans(
        self, 
        current_user: User, 
        skip: int = 0, 
        limit: int = 100, 
        subject: Optional[str] = None, 
        grade_level: Optional[str] = None
    ) -> List[LessonPlanResponse]:
        """
        Get lesson plans for the current user with optional filtering.
        
        Args:
            current_user (User): Current authenticated user
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            subject (Optional[str]): Filter by subject
            grade_level (Optional[str]): Filter by grade level
            
        Returns:
            List[LessonPlanResponse]: List of lesson plan responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # Start with lesson plans for the current user
            query = self.db.query(LessonPlan).filter(LessonPlan.user_id == current_user.user_id)
            
            # Apply additional filters
            if subject:
                query = query.join(Topic).join(CurriculumStructure).join(Subject).filter(Subject.name == subject)
            if grade_level:
                query = query.join(Topic).join(CurriculumStructure).join(GradeLevel).filter(GradeLevel.name == grade_level)
            
            # Apply pagination
            lesson_plans = query.offset(skip).limit(limit).all()
            
            return [self.create_lesson_plan_response(lesson_plan) for lesson_plan in lesson_plans]
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while retrieving lesson plans: {str(e)}"
            )
    
    def get_lesson_plan(self, lesson_id: int, current_user: User) -> LessonPlanResponse:
        """
        Get a specific lesson plan by ID.
        
        Args:
            lesson_id (int): Lesson plan ID
            current_user (User): Current authenticated user
            
        Returns:
            LessonPlanResponse: Lesson plan response
            
        Raises:
            HTTPException: If lesson plan not found or access denied
        """
        try:
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == lesson_id,
                LessonPlan.user_id == current_user.user_id
            ).first()
            
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")
            
            return self.create_lesson_plan_response(lesson_plan)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while retrieving the lesson plan: {str(e)}"
            )
    
    def update_lesson_plan(self, lesson_id: int, request: LessonPlanUpdate, current_user: User) -> LessonPlanResponse:
        """
        Update a lesson plan.
        
        Args:
            lesson_id (int): Lesson plan ID
            request (LessonPlanUpdate): Update data
            current_user (User): Current authenticated user
            
        Returns:
            LessonPlanResponse: Updated lesson plan response
            
        Raises:
            HTTPException: If lesson plan not found or update fails
        """
        try:
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == lesson_id,
                LessonPlan.user_id == current_user.user_id
            ).first()
            
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")
            
            # Update lesson plan fields
            # Note: This is a placeholder - you'll need to add the fields you want to update
            # For example: lesson_plan.title = request.title
            
            self.db.commit()
            self.db.refresh(lesson_plan)
            
            return self.create_lesson_plan_response(lesson_plan)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while updating the lesson plan: {str(e)}"
            )
    
    def delete_lesson_plan(self, lesson_id: int, current_user: User) -> Dict[str, str]:
        """
        Delete a lesson plan.
        
        Args:
            lesson_id (int): Lesson plan ID
            current_user (User): Current authenticated user
            
        Returns:
            Dict[str, str]: Success message
            
        Raises:
            HTTPException: If lesson plan not found or deletion fails
        """
        try:
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == lesson_id,
                LessonPlan.user_id == current_user.user_id
            ).first()
            
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")
            
            self.db.delete(lesson_plan)
            self.db.commit()
            
            return {"message": "Lesson plan deleted successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while deleting the lesson plan: {str(e)}"
            )
    
    def generate_lesson_resource(self, lesson_id: int, data: LessonResourceCreate, current_user: User) -> LessonResourceResponse:
        """
        Generate AI-powered lesson resources for a specific lesson plan.
        
        Args:
            lesson_id (int): Lesson plan ID
            data (LessonResourceCreate): Resource creation data
            current_user (User): Current authenticated user
            
        Returns:
            LessonResourceResponse: Generated lesson resource response
            
        Raises:
            HTTPException: If lesson plan not found or generation fails
        """
        try:
            # Verify lesson plan exists and user has access
            lesson_plan = self.db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_id).first()
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")
            
            # Check if user owns the lesson plan or is admin
            if lesson_plan.user_id != current_user.user_id and current_user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="You can only generate resources for your own lesson plans")
            
            # Get topic and curriculum data
            topic = self.db.query(Topic).filter(Topic.topic_id == lesson_plan.topic_id).first()
            if not topic:
                raise HTTPException(status_code=404, detail="Topic not found")
            
            # Get learning objectives
            objectives = [obj.objective for obj in topic.learning_objectives] if topic.learning_objectives else []
            
            # Get curriculum contents
            contents = [content.content_area for content in topic.topic_contents] if topic.topic_contents else []
            
            # Get subject and grade level from curriculum structure
            curriculum_structure = self.db.query(CurriculumStructure).filter(
                CurriculumStructure.curriculum_structure_id == topic.curriculum_structure_id
            ).first()
            
            subject = self.db.query(Subject).filter(Subject.subject_id == curriculum_structure.subject_id).first()
            grade_level = self.db.query(GradeLevel).filter(GradeLevel.grade_level_id == curriculum_structure.grade_level_id).first()
            
            # Get contexts from database for this lesson plan
            contexts = self.db.query(Context).filter(Context.lesson_plan_id == lesson_id).all()
            context_texts = [ctx.context_text for ctx in contexts]
            
            # Combine context from database with input context
            combined_context = ""
            if context_texts:
                combined_context += "Stored Context:\n" + "\n".join(context_texts) + "\n\n"
            if data.context_input:
                combined_context += "Additional Context:\n" + data.context_input
            
            # Initialize AI service
            ai_service = AwadeGPTService()
            
            # Generate AI content with all parameters
            ai_content = ai_service.generate_lesson_resource(
                subject=subject.name if subject else "Mathematics",
                grade=grade_level.name if grade_level else "JSS 1",
                topic=topic.topic_title,
                objectives=objectives,
                contents=contents,
                context=combined_context
            )
            
            # Create lesson resource
            lesson_resource = LessonResource(
                lesson_plan_id=lesson_id,
                user_id=current_user.user_id,
                context_input=data.context_input,
                ai_generated_content=ai_content,
                export_format=data.export_format,
                status='draft',
                created_at=datetime.now(UTC)
            )
            
            self.db.add(lesson_resource)
            self.db.commit()
            self.db.refresh(lesson_resource)
            
            return LessonResourceResponse(
                lesson_resources_id=lesson_resource.lesson_resources_id,
                lesson_plan_id=lesson_resource.lesson_plan_id,
                user_id=lesson_resource.user_id,
                context_input=lesson_resource.context_input,
                ai_generated_content=lesson_resource.ai_generated_content,
                user_edited_content=lesson_resource.user_edited_content,
                export_format=lesson_resource.export_format,
                status=lesson_resource.status,
                created_at=lesson_resource.created_at
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while generating lesson resource: {str(e)}"
            )
    
    def get_all_lesson_resources(self, current_user: User) -> List[LessonResourceResponse]:
        """
        Get all lesson resources for the current user.
        
        Args:
            current_user (User): Current authenticated user
            
        Returns:
            List[LessonResourceResponse]: List of lesson resource responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            lesson_resources = self.db.query(LessonResource).filter(
                LessonResource.user_id == current_user.user_id
            ).order_by(LessonResource.created_at.desc()).all()
            
            return [
                LessonResourceResponse(
                    lesson_resources_id=resource.lesson_resources_id,
                    lesson_plan_id=resource.lesson_plan_id,
                    user_id=resource.user_id,
                    context_input=resource.context_input,
                    ai_generated_content=resource.ai_generated_content,
                    user_edited_content=resource.user_edited_content,
                    export_format=resource.export_format,
                    status=resource.status,
                    created_at=resource.created_at
                )
                for resource in lesson_resources
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while retrieving lesson resources: {str(e)}"
            )
    
    def get_lesson_plan_resources(self, lesson_id: int, current_user: User) -> List[LessonResourceResponse]:
        """
        Get all resources for a specific lesson plan.
        
        Args:
            lesson_id (int): Lesson plan ID
            current_user (User): Current authenticated user
            
        Returns:
            List[LessonResourceResponse]: List of lesson resource responses
            
        Raises:
            HTTPException: If lesson plan not found or access denied
        """
        try:
            # First verify the lesson plan exists and user has access
            lesson_plan = self.db.query(LessonPlan).filter(LessonPlan.lesson_plan_id == lesson_id).first()
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")
            
            # Check if user is the lesson plan author or admin
            if current_user.user_id != lesson_plan.user_id and current_user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="You can only view resources for your own lesson plans")
            
            # Get all resources for this lesson plan
            lesson_resources = self.db.query(LessonResource).filter(
                LessonResource.lesson_plan_id == lesson_id
            ).order_by(LessonResource.created_at.desc()).all()
            
            return [
                LessonResourceResponse(
                    lesson_resources_id=resource.lesson_resources_id,
                    lesson_plan_id=resource.lesson_plan_id,
                    user_id=resource.user_id,
                    context_input=resource.context_input,
                    ai_generated_content=resource.ai_generated_content,
                    user_edited_content=resource.user_edited_content,
                    export_format=resource.export_format,
                    status=resource.status,
                    created_at=resource.created_at
                )
                for resource in lesson_resources
            ]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while retrieving lesson plan resources: {str(e)}"
            )

    def get_lesson_resource(self, resource_id: int, current_user: User) -> LessonResourceResponse:
        """
        Get a specific lesson resource.
        
        Args:
            resource_id (int): Resource ID
            current_user (User): Current authenticated user
            
        Returns:
            LessonResourceResponse: Lesson resource response
            
        Raises:
            HTTPException: If resource not found or access denied
        """
        try:
            lesson_resource = self.db.query(LessonResource).filter(LessonResource.lesson_resources_id == resource_id).first()
            if not lesson_resource:
                raise HTTPException(status_code=404, detail="Lesson resource not found")
            
            # Check if user is the resource author or admin
            if current_user.user_id != lesson_resource.user_id and current_user.role != UserRole.ADMIN:
                raise HTTPException(status_code=403, detail="You can only view your own resources")
            
            return LessonResourceResponse(
                lesson_resources_id=lesson_resource.lesson_resources_id,
                lesson_plan_id=lesson_resource.lesson_plan_id,
                user_id=lesson_resource.user_id,
                context_input=lesson_resource.context_input,
                ai_generated_content=lesson_resource.ai_generated_content,
                user_edited_content=lesson_resource.user_edited_content,
                export_format=lesson_resource.export_format,
                status=lesson_resource.status,
                created_at=lesson_resource.created_at
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"An error occurred while retrieving the lesson resource: {str(e)}"
            )
