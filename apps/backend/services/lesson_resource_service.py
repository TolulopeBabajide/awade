"""
Lesson Resource Service for Awade

Extracted from LessonPlanService as part of AWD-M-117 (service over 400-line threshold).
Handles all business logic related to lesson resources: generation, retrieval,
access control, and ORM-level helpers used by the export router.

Author: Tolulope Babajide
"""

import logging

logger = logging.getLogger(__name__)

from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import HTTPException
from arq import ArqRedis

from apps.backend.models import (
    LessonPlan, User, Topic, LessonResource, UserRole, Context
)
from apps.backend.schemas.lesson_plans import (
    LessonResourceCreate, LessonResourceResponse
)


def _to_lesson_resource_response(resource: LessonResource) -> LessonResourceResponse:
    """AWD-M-118: Single source of truth for ORM → response-DTO mapping.

    The same 9-kwarg constructor was previously duplicated 4× across
    ``generate_lesson_resource``, ``get_all_lesson_resources``,
    ``get_lesson_plan_resources``, and ``get_lesson_resource``. Adding a new
    field to ``LessonResource`` would require updating every call site (classic
    shotgun surgery). This helper centralises the mapping so the change lands
    in one place.

    Moved to this module as part of AWD-M-117 (LessonResourceService extraction).
    Re-exported from ``lesson_plan_service`` for backward compatibility.

    Args:
        resource (LessonResource): ORM object to convert.

    Returns:
        LessonResourceResponse: Pydantic response schema instance.
    """
    return LessonResourceResponse(
        lesson_resources_id=resource.lesson_resources_id,
        lesson_plan_id=resource.lesson_plan_id,
        user_id=resource.user_id,
        context_input=resource.context_input,
        ai_generated_content=resource.ai_generated_content,
        user_edited_content=resource.user_edited_content,
        export_format=resource.export_format,
        status=resource.status,
        created_at=resource.created_at,
    )


class LessonResourceService:
    """Service class for lesson resource operations.

    AWD-M-117: Extracted from LessonPlanService to keep each module under the
    400-line threshold. Takes the same (db, redis_pool) constructor so callers
    can swap the class name without changing instantiation patterns.
    """

    def __init__(self, db: Session, redis_pool: Optional[ArqRedis] = None):
        """
        Initialise with a database session and optional Redis pool.

        Args:
            db (Session): SQLAlchemy database session.
            redis_pool (Optional[ArqRedis]): Arq Redis connection pool for async tasks.
        """
        self.db = db
        self.redis = redis_pool

    async def generate_lesson_resource(
        self,
        lesson_id: int,
        data: LessonResourceCreate,
        current_user: User,
    ) -> LessonResourceResponse:
        """
        Generate AI-powered lesson resources for a specific lesson plan.

        Args:
            lesson_id (int): Lesson plan ID.
            data (LessonResourceCreate): Resource creation data.
            current_user (User): Current authenticated user.

        Returns:
            LessonResourceResponse: Generated lesson resource response.

        Raises:
            HTTPException: If lesson plan not found or generation fails.
        """
        try:
            # Verify lesson plan exists and user has access
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == lesson_id
            ).first()
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            # Check if user owns the lesson plan or is admin
            # AWD-H-62: SUPER_ADMIN has the same elevated access as ADMIN.
            if lesson_plan.user_id != current_user.user_id and current_user.role not in (
                UserRole.ADMIN, UserRole.SUPER_ADMIN
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can only generate resources for your own lesson plans",
                )

            # Get topic and curriculum data
            topic = self.db.query(Topic).filter(
                Topic.topic_id == lesson_plan.topic_id
            ).first()
            if not topic:
                raise HTTPException(status_code=404, detail="Topic not found")

            # Get learning objectives and curriculum contents
            objectives = (
                [obj.objective for obj in topic.learning_objectives]
                if topic.learning_objectives
                else []
            )
            contents = (
                [content.content_area for content in topic.topic_contents]
                if topic.topic_contents
                else []
            )

            # Get contexts from database for this lesson plan
            contexts = self.db.query(Context).filter(
                Context.lesson_plan_id == lesson_id
            ).all()
            context_texts = [ctx.context_text for ctx in contexts]

            # Combine context from database with input context
            combined_context = ""
            if context_texts:
                combined_context += "Stored Context:\n" + "\n".join(context_texts) + "\n\n"
            if data.context_input:
                combined_context += "Additional Context:\n" + data.context_input

            # Create lesson resource with 'processing' status
            lesson_resource = LessonResource(
                lesson_plan_id=lesson_id,
                user_id=current_user.user_id,
                context_input=data.context_input,
                ai_generated_content=None,  # Content will be generated async
                export_format=data.export_format,
                status="processing",
                created_at=datetime.now(timezone.utc),
            )

            self.db.add(lesson_resource)
            self.db.commit()
            self.db.refresh(lesson_resource)

            # Enqueue async task if redis pool is available
            if self.redis:
                try:
                    await self.redis.enqueue_job(
                        "generate_lesson_resource_task",
                        resource_id=lesson_resource.lesson_resources_id,
                    )
                except Exception:
                    # Log error but don't fail request; worker can retry
                    logger.error("Failed to enqueue job", exc_info=True)

            return _to_lesson_resource_response(lesson_resource)

        except HTTPException:
            raise
        except Exception:
            logger.error(
                "Failed to initiate lesson resource generation for lesson %s",
                lesson_id,
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail="An error occurred while initiating lesson resource generation",
            )

    def get_all_lesson_resources(self, current_user: User) -> List[LessonResourceResponse]:
        """
        Get all lesson resources for the current user.

        Args:
            current_user (User): Current authenticated user.

        Returns:
            List[LessonResourceResponse]: List of lesson resource responses.

        Raises:
            HTTPException: If retrieval fails.
        """
        try:
            lesson_resources = (
                self.db.query(LessonResource)
                .filter(LessonResource.user_id == current_user.user_id)
                .order_by(LessonResource.created_at.desc())
                .all()
            )
            return [_to_lesson_resource_response(r) for r in lesson_resources]

        except Exception:
            logger.error("Failed to retrieve lesson resources for user", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving lesson resources",
            )

    def get_lesson_plan_resources(
        self, lesson_id: int, current_user: User
    ) -> List[LessonResourceResponse]:
        """
        Get all resources for a specific lesson plan.

        Args:
            lesson_id (int): Lesson plan ID.
            current_user (User): Current authenticated user.

        Returns:
            List[LessonResourceResponse]: List of lesson resource responses.

        Raises:
            HTTPException: If lesson plan not found or access denied.
        """
        try:
            # Verify the lesson plan exists and user has access
            lesson_plan = self.db.query(LessonPlan).filter(
                LessonPlan.lesson_plan_id == lesson_id
            ).first()
            if not lesson_plan:
                raise HTTPException(status_code=404, detail="Lesson plan not found")

            # Check if user is the lesson plan author or admin
            # AWD-H-62: SUPER_ADMIN has the same elevated access as ADMIN.
            if current_user.user_id != lesson_plan.user_id and current_user.role not in (
                UserRole.ADMIN, UserRole.SUPER_ADMIN
            ):
                raise HTTPException(
                    status_code=403,
                    detail="You can only view resources for your own lesson plans",
                )

            lesson_resources = (
                self.db.query(LessonResource)
                .filter(LessonResource.lesson_plan_id == lesson_id)
                .order_by(LessonResource.created_at.desc())
                .all()
            )
            return [_to_lesson_resource_response(r) for r in lesson_resources]

        except HTTPException:
            raise
        except Exception:
            logger.error(
                "Failed to retrieve resources for lesson plan %s", lesson_id, exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving lesson plan resources",
            )

    def get_lesson_resource_orm(self, resource_id: int, current_user: User) -> LessonResource:
        """
        Get a specific lesson resource as the raw ORM object, scoped to the
        current user's role. Centralises access control so callers (router
        endpoints, exports, etc.) cannot drift from the canonical rules.

        AWD-M-67: scope query to user_id for non-admins so unauthorized IDs
        return 404 regardless of whether the resource exists, preventing
        existence leakage via 403/404 discrepancy.
        AWD-H-61: SUPER_ADMIN has the same elevated access as ADMIN.

        Args:
            resource_id (int): Resource ID.
            current_user (User): Current authenticated user.

        Returns:
            LessonResource: ORM object for the requested resource.

        Raises:
            HTTPException: 404 if resource not found or not accessible to user.
        """
        if current_user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            lesson_resource = self.db.query(LessonResource).filter(
                LessonResource.lesson_resources_id == resource_id
            ).first()
        else:
            lesson_resource = self.db.query(LessonResource).filter(
                LessonResource.lesson_resources_id == resource_id,
                LessonResource.user_id == current_user.user_id,
            ).first()
        if not lesson_resource:
            raise HTTPException(status_code=404, detail="Lesson resource not found")
        return lesson_resource

    def get_lesson_resource(
        self, resource_id: int, current_user: User
    ) -> LessonResourceResponse:
        """
        Get a specific lesson resource.

        Args:
            resource_id (int): Resource ID.
            current_user (User): Current authenticated user.

        Returns:
            LessonResourceResponse: Lesson resource response.

        Raises:
            HTTPException: If resource not found or access denied.
        """
        try:
            # AWD-M-70: delegate access-control to get_lesson_resource_orm so
            # the ADMIN/SUPER_ADMIN/owner-scoped query lives in one place.
            lesson_resource = self.get_lesson_resource_orm(resource_id, current_user)
            return _to_lesson_resource_response(lesson_resource)

        except HTTPException:
            raise
        except Exception:
            logger.error(
                "Failed to retrieve lesson resource %s", resource_id, exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving the lesson resource",
            )
