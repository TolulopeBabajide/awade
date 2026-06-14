"""
Children Service for Awade

This module provides service methods for child profile management. Parents can
create, read, update, and delete child profiles, each linked to a specific
curriculum, grade level, and set of subjects.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import func as sqlfunc
from typing import Any, List, Optional, Type
from fastapi import HTTPException, status
import json
import logging

from pydantic import ValidationError

from packages.ai.gpt_service import AwadeGPTService, ParentGuideRequest
from apps.backend.models import (
    ChildProfile, ParentGuide, ParentalConsent, User, UserRole,
    Country, Curriculum, GradeLevel, Subject, Topic,
    CurriculumStructure
)
from apps.backend.schemas.children import (
    ChildProfileCreate, ChildProfileUpdate, ChildProfileResponse,
    ChildProfileListResponse, ParentGuideResponse, ParentGuideListResponse,
    ParentGuideAIContent, ParentalConsentResponse, ConsentStatusResponse
)

logger = logging.getLogger(__name__)


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

    # ── COPPA Consent (AWD-GRC-01) ────────────────────────────────────────────

    def get_consent_status(self, user: User) -> ConsentStatusResponse:
        """Return whether the parent has already given COPPA consent."""
        self._verify_parent(user)
        record = (
            self.db.query(ParentalConsent)
            .filter(ParentalConsent.parent_id == user.user_id)
            .first()
        )
        if record:
            return ConsentStatusResponse(
                has_consented=True,
                consent=ParentalConsentResponse.model_validate(record),
            )
        return ConsentStatusResponse(has_consented=False, consent=None)

    def record_consent(self, user: User, ip_address: Optional[str] = None) -> ParentalConsentResponse:
        """Record (or refresh) COPPA consent for the authenticated parent.

        Idempotent — calling again updates the timestamp and IP but does not
        create a duplicate row.
        """
        self._verify_parent(user)
        record = (
            self.db.query(ParentalConsent)
            .filter(ParentalConsent.parent_id == user.user_id)
            .first()
        )
        if record:
            # Update existing record (parent re-confirmed consent)
            record.consented_at = sqlfunc.now()
            record.ip_address = ip_address
        else:
            record = ParentalConsent(
                parent_id=user.user_id,
                ip_address=ip_address,
                consent_version='1.0',
            )
            self.db.add(record)
        try:
            self.db.commit()
            self.db.refresh(record)
        except HTTPException:
            raise
        except Exception:
            self.db.rollback()
            logger.error("Failed to record parental consent for user %s", user.user_id, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not save consent. Please try again.",
            )
        return ParentalConsentResponse.model_validate(record)

    def _require_consent(self, user: User) -> None:
        """Raise 403 if the parent has not yet given COPPA consent."""
        record = (
            self.db.query(ParentalConsent)
            .filter(ParentalConsent.parent_id == user.user_id)
            .first()
        )
        if not record:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Parental consent required. "
                    "Please accept the data collection disclosure before adding a child profile."
                ),
            )

    def _check_fk_exists(self, model: Type[Any], id_value: int, field_name: str) -> None:
        """Raise HTTP 400 if *id_value* does not reference an existing row in *model*.

        *field_name* must match both the data-dict key and the SQLAlchemy column
        attribute on *model* (e.g. ``'country_id'`` → ``Country.country_id``).
        Used by :meth:`_validate_profile_fks` to eliminate repeated query boilerplate
        for single-row FK checks (AWD-M-184).

        Raises :exc:`ValueError` if *field_name* is not an attribute on *model*,
        which indicates a programming error at the call site (AWD-M-187).
        """
        if not hasattr(model, field_name):
            raise ValueError(
                f"{model.__name__} has no attribute '{field_name}' "
                f"— check _validate_profile_fks call sites (AWD-M-187)"
            )
        pk_col = getattr(model, field_name)
        if not self.db.query(model).filter(pk_col == id_value).first():
            raise HTTPException(status_code=400, detail=f"Invalid {field_name}")

    def _validate_profile_fks(self, data: dict) -> None:
        """Validate that FK IDs in *data* reference existing rows.

        Raises HTTP 400 if any referenced foreign key is not found in the DB.
        *data* is a plain dict (e.g. from ``model_dump(exclude_unset=True)``).
        Only keys that are present **and** non-None are validated, so callers
        can safely pass a sparse update dict without triggering spurious checks.

        Single-FK checks (country, curricula, grade level) delegate to
        :meth:`_check_fk_exists`. Subject validation is kept inline because it
        uses a batch ``IN`` query rather than a per-row lookup.

        Note: subject serialisation (list → JSON string) is the caller's
        responsibility and is intentionally excluded from this helper.
        """
        if data.get('country_id') is not None:
            self._check_fk_exists(Country, data['country_id'], 'country_id')

        if data.get('curricula_id') is not None:
            self._check_fk_exists(Curriculum, data['curricula_id'], 'curricula_id')

        if data.get('grade_level_id') is not None:
            self._check_fk_exists(GradeLevel, data['grade_level_id'], 'grade_level_id')

        if data.get('subjects') is not None:
            found = (
                self.db.query(Subject.subject_id)
                .filter(Subject.subject_id.in_(data['subjects']))
                .all()
            )
            found_ids = {row[0] for row in found}
            invalid = [sid for sid in data['subjects'] if sid not in found_ids]
            if invalid:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid subject_id: {invalid[0]}",
                )

    # ── Child Profile CRUD ────────────────────────────────────────────────────

    def create_child(self, user: User, data: ChildProfileCreate) -> ChildProfileResponse:
        """Create a new child profile for the authenticated parent.

        Requires prior COPPA consent (AWD-GRC-01).
        """
        self._verify_parent(user)
        self._require_consent(user)
        self._validate_profile_fks(data.model_dump(exclude_unset=True))

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
        try:
            self.db.add(child)
            self.db.commit()
            self.db.refresh(child)
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create child profile: %s", e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create child profile",
            )

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
        self._validate_profile_fks(update_data)

        # Serialize subjects list to JSON string for storage
        if 'subjects' in update_data and update_data['subjects'] is not None:
            update_data['subjects'] = json.dumps(update_data['subjects'])

        for field, value in update_data.items():
            setattr(child, field, value)

        try:
            self.db.commit()
            self.db.refresh(child)
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to update child profile %s: %s", child_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update child profile",
            )

        child = self._get_child_or_404(child_id, user.user_id)
        return self._to_response(child)

    def delete_child(self, user: User, child_id: int) -> dict:
        """Delete a child profile and all associated guides."""
        self._verify_parent(user)
        child = self._get_child_or_404(child_id, user.user_id)

        try:
            self.db.delete(child)
            self.db.commit()
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to delete child profile %s: %s", child_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete child profile",
            )

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
            .options(
                joinedload(Topic.curriculum_structure).joinedload(CurriculumStructure.subject)
            )
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
        curriculum_title = cs.curriculum.curricula_title if cs and cs.curriculum else "National Curriculum"
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

        # Reload with relationships for the response (AWD-M-188: guard against None)
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
                joinedload(Topic.student_activities),
                joinedload(Topic.teaching_learning_materials),
                joinedload(Topic.evaluation_guides),
            )
            .filter(Topic.topic_id == topic_id)
            .first()
        )
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        # Call AI service
        ai_service = AwadeGPTService()
        ai_content, is_valid = ai_service.generate_parent_guide(
            self._build_guide_ai_payload(child, topic)
        )

        if not is_valid:
            logger.warning(f"Parent guide for topic {topic_id} failed light validation: AI key check")

        # Validate JSON shape against Pydantic schema before persisting (H-06)
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
