"""
Lesson Plan Service for Awade

This module provides service methods for managing lesson plans, including CRUD operations
and AI-powered generation. Resource management has been extracted to
``lesson_resource_service.LessonResourceService`` (AWD-M-117).

Author: Tolulope Babajide
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, status
from arq import ArqRedis

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

from apps.backend.models import (
    LessonPlan, User, Topic, CurriculumStructure, Curriculum, Country,
    GradeLevel, Subject, LessonResource, LessonStatus, UserRole, Context
)
from apps.backend.schemas.lesson_plans import (
    LessonPlanCreate, LessonPlanResponse, LessonPlanUpdate,
    LessonResourceCreate, LessonResourceUpdate, LessonResourceResponse
)
from packages.ai.gpt_service import AwadeGPTService

# AWD-M-117: _to_lesson_resource_response moved to lesson_resource_service.
# Re-exported here so existing imports (tests, etc.) continue to work.
from apps.backend.services.lesson_resource_service import (  # noqa: F401
    _to_lesson_resource_response,
)


class LessonPlanService:
    """Service class for lesson plan operations."""

    def __init__(self, db: Session, redis_pool: Optional[ArqRedis] = None):
        """
        Initialize the LessonPlanService with a database session and optional Redis pool.

        Args:
            db (Session): SQLAlchemy database session
            redis_pool (Optional[ArqRedis]): Arq Redis connection pool for async tasks
        """
        self.db = db
        self.redis = redis_pool

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
                    # Retrieve topic if lazy loaded but None (shouldn't happen if foreign key enforced)
                    # But for response creation we handle gracefully
                    title = "Untitled Lesson"
                    subject = "Unknown"
                    grade_level = "Unknown"
                    topic = None
                else:
                    title = f"{lesson_plan.topic.curriculum_structure.subject.name}: {lesson_plan.topic.topic_title}"
                    subject = lesson_plan.topic.curriculum_structure.subject.name
                    grade_level = lesson_plan.topic.curriculum_structure.grade_level.name
                    topic = lesson_plan.topic.topic_title

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
                status=LessonStatus.DRAFT.value,  # Pass string value to match schema
                curriculum_learning_objectives=curriculum_learning_objectives,
                curriculum_contents=curriculum_contents
            )
        except Exception as e:
            logger.error("Unexpected error in create_lesson_plan_response", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error creating lesson plan response"
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
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(lesson_plan)
            self.db.commit()
            self.db.refresh(lesson_plan)

            return self.create_lesson_plan_response(lesson_plan, request)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Unexpected error in generate_lesson_plan", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while generating the lesson plan"
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

        except Exception:
            logger.error("Failed to retrieve lesson plans", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving lesson plans"
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
        except Exception:
            logger.error("Failed to retrieve lesson plan %s", lesson_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving the lesson plan"
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
        except Exception:
            logger.error("Failed to update lesson plan %s", lesson_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while updating the lesson plan"
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
        except Exception:
            logger.error("Failed to delete lesson plan %s", lesson_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while deleting the lesson plan"
            )
