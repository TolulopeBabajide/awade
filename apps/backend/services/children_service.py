"""
Children Service for Awade

This module provides service methods for child profile management. Parents can
create, read, update, and delete child profiles, each linked to a specific
curriculum, grade level, and set of subjects.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from fastapi import HTTPException, status
import json
import logging

from apps.backend.models import (
    ChildProfile, ParentGuide, User, UserRole,
    Country, Curriculum, GradeLevel, Subject, Topic,
    CurriculumStructure
)

logger = logging.getLogger(__name__)
from apps.backend.schemas.children import (
    ChildProfileCreate, ChildProfileUpdate, ChildProfileResponse,
    ChildProfileListResponse, ParentGuideResponse, ParentGuideListResponse
)


class ChildrenService:
    """Service class for child profile operations."""

    def __init__(self, db: Session):
        self.db = db

    def _verify_parent(self, user: User) -> None:
        """Ensure the user has the PARENT role."""
        if user.role not in (UserRole.PARENT, UserRole.ADMIN, UserRole.SUPER_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only parent accounts can manage child profiles"
            )

    def _get_child_or_404(self, child_id: int, parent_id: int) -> ChildProfile:
        """Fetch a child profile that belongs to the given parent, or raise 404."""
        child = (
            self.db.query(ChildProfile)
            .options(
                joinedload(ChildProfile.country),
                joinedload(ChildProfile.curriculum),
                joinedload(ChildProfile.grade_level),
            )
            .filter(
                ChildProfile.child_id == child_id,
                ChildProfile.parent_id == parent_id,
            )
            .first()
        )
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child profile not found"
            )
        return child

    def _to_response(self, child: ChildProfile) -> ChildProfileResponse:
        """Convert a ChildProfile ORM object to a response schema."""
        subjects_list = None
        if child.subjects:
            try:
                subjects_list = json.loads(child.subjects)
            except (json.JSONDecodeError, TypeError):
                subjects_list = None

        return ChildProfileResponse(
            child_id=child.child_id,
            parent_id=child.parent_id,
            name=child.name,
            age=child.age,
            school_name=child.school_name,
            country_id=child.country_id,
            country_name=child.country.country_name if child.country else None,
            curricula_id=child.curricula_id,
            curricula_title=child.curriculum.curricula_title if child.curriculum else None,
            grade_level_id=child.grade_level_id,
            grade_level_name=child.grade_level.name if child.grade_level else None,
            subjects=subjects_list,
            created_at=child.created_at,
            updated_at=child.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────────────

    def create_child(self, user: User, data: ChildProfileCreate) -> ChildProfileResponse:
        """Create a new child profile for the authenticated parent."""
        self._verify_parent(user)

        # Validate foreign keys if provided
        if data.country_id:
            country = self.db.query(Country).filter(Country.country_id == data.country_id).first()
            if not country:
                raise HTTPException(status_code=400, detail="Invalid country_id")

        if data.curricula_id:
            curriculum = self.db.query(Curriculum).filter(Curriculum.curricula_id == data.curricula_id).first()
            if not curriculum:
                raise HTTPException(status_code=400, detail="Invalid curricula_id")

        if data.grade_level_id:
            grade = self.db.query(GradeLevel).filter(GradeLevel.grade_level_id == data.grade_level_id).first()
            if not grade:
                raise HTTPException(status_code=400, detail="Invalid grade_level_id")

        if data.subjects:
            for sid in data.subjects:
                subj = self.db.query(Subject).filter(Subject.subject_id == sid).first()
                if not subj:
                    raise HTTPException(status_code=400, detail=f"Invalid subject_id: {sid}")

        child = ChildProfile(
            parent_id=user.user_id,
            name=data.name,
            age=data.age,
            school_name=data.school_name,
            country_id=data.country_id,
            curricula_id=data.curricula_id,
            grade_level_id=data.grade_level_id,
            subjects=json.dumps(data.subjects) if data.subjects else None,
        )
        self.db.add(child)
        self.db.commit()
        self.db.refresh(child)

        # Eager-load relationships for the response
        child = self._get_child_or_404(child.child_id, user.user_id)
        return self._to_response(child)

    def list_children(self, user: User) -> ChildProfileListResponse:
        """List all child profiles for the authenticated parent."""
        self._verify_parent(user)

        children = (
            self.db.query(ChildProfile)
            .options(
                joinedload(ChildProfile.country),
                joinedload(ChildProfile.curriculum),
                joinedload(ChildProfile.grade_level),
            )
            .filter(ChildProfile.parent_id == user.user_id)
            .order_by(ChildProfile.created_at.desc())
            .all()
        )

        return ChildProfileListResponse(
            children=[self._to_response(c) for c in children],
            total=len(children),
        )

    def get_child(self, user: User, child_id: int) -> ChildProfileResponse:
        """Get a single child profile by ID."""
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)
        return self._to_response(child)

    def update_child(self, user: User, child_id: int, data: ChildProfileUpdate) -> ChildProfileResponse:
        """Update an existing child profile."""
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)

        update_data = data.model_dump(exclude_unset=True)

        # Validate foreign keys if being updated
        if 'country_id' in update_data and update_data['country_id'] is not None:
            if not self.db.query(Country).filter(Country.country_id == update_data['country_id']).first():
                raise HTTPException(status_code=400, detail="Invalid country_id")

        if 'curricula_id' in update_data and update_data['curricula_id'] is not None:
            if not self.db.query(Curriculum).filter(Curriculum.curricula_id == update_data['curricula_id']).first():
                raise HTTPException(status_code=400, detail="Invalid curricula_id")

        if 'grade_level_id' in update_data and update_data['grade_level_id'] is not None:
            if not self.db.query(GradeLevel).filter(GradeLevel.grade_level_id == update_data['grade_level_id']).first():
                raise HTTPException(status_code=400, detail="Invalid grade_level_id")

        if 'subjects' in update_data and update_data['subjects'] is not None:
            for sid in update_data['subjects']:
                if not self.db.query(Subject).filter(Subject.subject_id == sid).first():
                    raise HTTPException(status_code=400, detail=f"Invalid subject_id: {sid}")
            update_data['subjects'] = json.dumps(update_data['subjects'])

        for field, value in update_data.items():
            setattr(child, field, value)

        self.db.commit()
        self.db.refresh(child)

        child = self._get_child_or_404(child_id, user.user_id)
        return self._to_response(child)

    def delete_child(self, user: User, child_id: int) -> dict:
        """Delete a child profile and all associated guides."""
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)

        self.db.delete(child)
        self.db.commit()

        return {"message": "Child profile deleted successfully"}

    # ── Child's curriculum topics ─────────────────────────────────────

    def get_child_topics(self, user: User, child_id: int, subject_id: Optional[int] = None) -> list:
        """
        Get curriculum topics available for a child based on their
        curriculum and grade level. Optionally filter by subject.
        """
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)

        if not child.curricula_id or not child.grade_level_id:
            return []

        query = (
            self.db.query(Topic)
            .join(CurriculumStructure)
            .filter(
                CurriculumStructure.curricula_id == child.curricula_id,
                CurriculumStructure.grade_level_id == child.grade_level_id,
            )
        )

        if subject_id:
            query = query.filter(CurriculumStructure.subject_id == subject_id)

        topics = query.all()

        return [
            {
                "topic_id": t.topic_id,
                "topic_title": t.topic_title,
                "subject_name": t.curriculum_structure.subject.name if t.curriculum_structure and t.curriculum_structure.subject else None,
                "subject_id": t.curriculum_structure.subject_id if t.curriculum_structure else None,
            }
            for t in topics
        ]

    # ── Parent guides ─────────────────────────────────────────────────

    def list_guides(self, user: User, child_id: int, bookmarked_only: bool = False) -> ParentGuideListResponse:
        """List all parent guides for a child."""
        self._verify_parent(user)
        # Verify child belongs to this parent
        self._get_child_or_404(child_id, user.user_id)

        query = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .filter(ParentGuide.child_id == child_id)
        )

        if bookmarked_only:
            query = query.filter(ParentGuide.is_bookmarked == 1)

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

        guide.is_bookmarked = 0 if guide.is_bookmarked else 1
        self.db.commit()
        self.db.refresh(guide)

        return self._guide_to_response(guide)

    def generate_guide(self, user: User, child_id: int, topic_id: int) -> ParentGuideResponse:
        """
        Generate a 'How to Help' guide for a specific topic and child.

        If a guide already exists for this child+topic combination, return the
        existing one instead of generating a new one (idempotent).
        """
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)

        # Check for existing guide
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

        # Fetch topic with curriculum context
        topic = (
            self.db.query(Topic)
            .options(
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.subject),
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.curriculum),
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.grade_level),
                joinedload(Topic.learning_objectives),
                joinedload(Topic.topic_contents),
            )
            .filter(Topic.topic_id == topic_id)
            .first()
        )
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Gather curriculum metadata
        cs = topic.curriculum_structure
        subject_name = cs.subject.name if cs and cs.subject else "Unknown Subject"
        grade_name = cs.grade_level.name if cs and cs.grade_level else "Unknown Grade"
        curriculum_title = cs.curriculum.curricula_title if cs and cs.curriculum else "National Curriculum"
        country_name = child.country.country_name if child.country else "Nigeria"

        objectives = [obj.objective for obj in topic.learning_objectives]
        contents = [c.content_area for c in topic.topic_contents]

        # Call AI service
        from packages.ai.gpt_service import AwadeGPTService

        ai_service = AwadeGPTService()
        ai_content, is_valid = ai_service.generate_parent_guide(
            subject=subject_name,
            grade=grade_name,
            topic=topic.topic_title,
            country=country_name,
            curriculum=curriculum_title,
            objectives=objectives,
            contents=contents,
        )

        if not is_valid:
            logger.warning(f"Parent guide for topic {topic_id} generated but failed validation")

        # Persist the guide
        guide = ParentGuide(
            child_id=child_id,
            topic_id=topic_id,
            ai_generated_content=ai_content,
        )
        self.db.add(guide)
        self.db.commit()
        self.db.refresh(guide)

        # Reload with relationships for the response
        guide = (
            self.db.query(ParentGuide)
            .options(joinedload(ParentGuide.topic))
            .filter(ParentGuide.guide_id == guide.guide_id)
            .first()
        )

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
            is_bookmarked=bool(guide.is_bookmarked),
            created_at=guide.created_at,
            updated_at=guide.updated_at,
        )
