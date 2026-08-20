"""
Parent Guide Service for Awade

Extracted from ChildrenService as part of AWD-M-214
(children_service.py over 600 lines after AWD-M-208 NERDC additions).
Handles guide generation, retrieval, bookmarking, and response serialization.

ChildProfile CRUD and consent management remain in ChildrenService.

Author: Tolulope Babajide
"""

import logging

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session, joinedload

from packages.ai.gpt_service import AwadeGPTService, ParentGuideRequest
from apps.backend.models import (
    ChildProfile, ParentGuide, User, UserRole, Topic, CurriculumStructure
)
from apps.backend.schemas.children import (
    ParentGuideAIContent, ParentGuideListResponse, ParentGuideResponse
)
from apps.backend.services.children_shared import (
    verify_parent as _verify_parent_shared,
    get_child_or_404 as _get_child_or_404_shared,
)

logger = logging.getLogger(__name__)


class ParentGuideService:
    """Service class for parent guide operations."""

    def __init__(self, db: Session):
        self.db = db

    def _verify_parent(self, user: User) -> None:
        """Ensure the user has the PARENT role."""
        _verify_parent_shared(user)

    def _get_child_or_404(self, child_id: int, parent_id: int) -> ChildProfile:
        """Fetch a child profile that belongs to the given parent, or raise 404."""
        return _get_child_or_404_shared(self.db, child_id, parent_id)

    def list_guides(self, user: User, child_id: int, bookmarked_only: bool = False) -> ParentGuideListResponse:
        """List all parent guides for a child."""
        self._verify_parent(user)
        self._get_child_or_404(child_id, user.user_id)

        query = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .filter(ParentGuide.child_id == child_id)
        )

        if bookmarked_only:
            query = query.filter(ParentGuide.is_bookmarked.is_(True))

        guides = query.order_by(ParentGuide.created_at.desc()).all()

        return ParentGuideListResponse(
            guides=[self._guide_to_response(g) for g in guides],
            total=len(guides),
        )

    def get_guide(self, user: User, guide_id: int) -> ParentGuideResponse:
        """Get a single parent guide by ID."""
        self._verify_parent(user)

        guide = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .join(ChildProfile)
            .filter(
                ParentGuide.guide_id == guide_id,
                ChildProfile.parent_id == user.user_id,
            )
            .first()
        )
        if not guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Guide not found"
            )

        return self._guide_to_response(guide)

    def toggle_bookmark(self, user: User, guide_id: int) -> ParentGuideResponse:
        """Toggle the bookmark status of a guide."""
        self._verify_parent(user)

        guide = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .join(ChildProfile)
            .filter(
                ParentGuide.guide_id == guide_id,
                ChildProfile.parent_id == user.user_id,
            )
            .first()
        )
        if not guide:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Guide not found"
            )

        guide.is_bookmarked = not guide.is_bookmarked
        try:
            self.db.commit()
            self.db.refresh(guide)
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to toggle bookmark for guide %s: %s", guide_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update bookmark",
            )

        return self._guide_to_response(guide)

    def _build_guide_ai_payload(self, child: ChildProfile, topic: Topic) -> ParentGuideRequest:
        """Assemble the ParentGuideRequest for AwadeGPTService.generate_parent_guide().

        Extracted from generate_guide (AWD-M-185) to reduce cyclomatic complexity.
        Typed as ParentGuideRequest (AWD-H-98) for call-site type safety.
        """
        cs = topic.curriculum_structure
        subject_name = cs.subject.name if cs and cs.subject else "Unknown Subject"
        grade_name = cs.grade_level.name if cs and cs.grade_level else "Unknown Grade"
        curriculum_title = cs.curriculum.curriculum_title if cs and cs.curriculum else "National Curriculum"
        country_name = child.country.country_name if child.country else "Nigeria"
        objectives = [obj.objective for obj in topic.learning_objectives]
        contents = [c.content_area for c in topic.topic_contents]
        student_activities = [a.activity for a in topic.student_activities]
        teaching_materials = [m.material for m in topic.teaching_learning_materials]
        evaluation_guide = [e.guide_item for e in topic.evaluation_guides]
        return {
            "subject": subject_name,
            "grade": grade_name,
            "topic": topic.topic_title,
            "country": country_name,
            "curriculum": curriculum_title,
            "objectives": objectives,
            "contents": contents,
            "student_activities": student_activities,
            "teaching_learning_materials": teaching_materials,
            "evaluation_guide": evaluation_guide,
        }

    def _persist_guide(self, child_id: int, topic_id: int, ai_content: str) -> ParentGuide:
        """
        Create, commit, and reload a ParentGuide row with its topic relationship.

        Extracted from generate_guide (AWD-M-185) to reduce cyclomatic complexity.
        Raises HTTP 500 on DB failure (rollback included).
        """
        guide = ParentGuide(
            child_id=child_id,
            topic_id=topic_id,
            ai_generated_content=ai_content,
        )
        try:
            self.db.add(guide)
            self.db.commit()
            self.db.refresh(guide)
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to persist guide for topic %s: %s", topic_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save generated guide",
            )

        reloaded = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .filter(ParentGuide.guide_id == guide.guide_id)
            .first()
        )
        if reloaded is None:
            logger.error(
                "Guide %s disappeared immediately after persist for topic %s",
                guide.guide_id,
                topic_id,
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reload saved guide",
            )
        return reloaded

    def generate_guide(self, user: User, child_id: int, topic_id: int) -> ParentGuideResponse:
        """
        Generate a 'How to Help' guide for a specific topic and child.

        If a guide already exists for this child+topic combination, return the
        existing one instead of generating a new one (idempotent).
        """
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)

        existing = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .filter(
                ParentGuide.child_id == child_id,
                ParentGuide.topic_id == topic_id,
            )
            .first()
        )
        if existing:
            return self._guide_to_response(existing)

        topic = (
            self.db.query(Topic)
            .options(
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.subject),
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.curriculum),
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.grade_level),
                joinedload(Topic.learning_objectives),
                joinedload(Topic.topic_contents),
                joinedload(Topic.student_activities),
                joinedload(Topic.teaching_learning_materials),
                joinedload(Topic.evaluation_guides),
            )
            .filter(Topic.topic_id == topic_id)
            .first()
        )
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        ai_service = AwadeGPTService()
        ai_content, is_valid = ai_service.generate_parent_guide(
            self._build_guide_ai_payload(child, topic)
        )

        if not is_valid:
            logger.warning(
                "Parent guide for topic %s failed safety/structural validation — rejecting",
                topic_id,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI service returned content that did not pass safety checks. Please try again.",
            )

        try:
            ParentGuideAIContent.model_validate_json(ai_content)
        except (ValidationError, ValueError) as exc:
            logger.error(
                "Parent guide schema validation failed for topic %s: %s",
                topic_id,
                exc,
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI service returned content that did not match the expected structure. Please try again.",
            )

        guide = self._persist_guide(child_id, topic_id, ai_content)
        return self._guide_to_response(guide)

    def _guide_to_response(self, guide: ParentGuide) -> ParentGuideResponse:
        """Convert a ParentGuide ORM object to a response schema."""
        topic = guide.topic
        subject_name = None
        if topic and topic.curriculum_structure and topic.curriculum_structure.subject:
            subject_name = topic.curriculum_structure.subject.name

        return ParentGuideResponse(
            guide_id=guide.guide_id,
            child_id=guide.child_id,
            topic_id=guide.topic_id,
            topic_title=topic.topic_title if topic else None,
            subject_name=subject_name,
            ai_generated_content=guide.ai_generated_content,
            user_edited_content=guide.user_edited_content,
            is_bookmarked=guide.is_bookmarked,
            created_at=guide.created_at,
            updated_at=guide.updated_at,
        )
