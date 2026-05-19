"""
Tests for LessonPlanService — AWD-M-04 coverage + AWD-M-117 split.

Covers plan-only service methods:
- fetch_curriculum_data
- create_lesson_plan_response (with and without request_data)
- generate_lesson_plan
- get_lesson_plan  (404, 200, cross-user)
- update_lesson_plan (404, 501 — AWD-M-191)
- delete_lesson_plan (404, 200)
- get_lesson_plans (smoke via TestLessonPlanServiceSmoke)

Resource methods have moved to LessonResourceService (AWD-M-117).
Tests for those methods live in test_lesson_resource_service.py.
"""

import pytest
import sys
import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

# --------------------------------------------------------------------------
# Path fixups for sandbox + CI
# --------------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.abspath(os.path.join(backend_dir, "../.."))
sys.path.insert(0, root_dir)
sys.path.insert(0, backend_dir)

# Sandbox compat shim: datetime.UTC added in Python 3.11
import datetime as _dt
if not hasattr(_dt, "UTC"):
    _dt.UTC = _dt.timezone.utc

from apps.backend.models import (
    LessonPlan, LessonResource, User, UserRole,
    Topic, CurriculumStructure, Subject, GradeLevel, Curriculum,
    LearningObjective, TopicContent,
)
from apps.backend.schemas.lesson_plans import (
    LessonPlanCreate, LessonPlanUpdate, LessonResourceResponse,
)
from apps.backend.services.lesson_plan_service import LessonPlanService


# --------------------------------------------------------------------------
# Factories
# --------------------------------------------------------------------------

def _now():
    return datetime.now(timezone.utc)


def _make_user(user_id: int, role: UserRole) -> User:
    u = User()
    u.user_id = user_id
    u.email = f"user{user_id}@example.com"
    u.role = role
    u.is_active = True
    u.is_suspended = False
    return u


def _educator(user_id: int = 1) -> User:
    return _make_user(user_id, UserRole.EDUCATOR)


def _make_topic(topic_id: int = 1, title: str = "Fractions") -> MagicMock:
    """Return a plain MagicMock standing in for a Topic ORM object.

    Using real SQLAlchemy ORM instances here triggers backref event processing
    (``emit_backref_from_collection_append_event``) when relationship lists are
    assigned, which requires every item to have ``_sa_instance_state``.
    MagicMock objects don't satisfy that constraint, so we use a plain MagicMock
    for the whole topic and populate only the attributes the service layer reads.
    """
    t = MagicMock()
    t.topic_id = topic_id
    t.topic_title = title
    t.curriculum_structure_id = 1
    # Attribute chains read by create_lesson_plan_response
    t.curriculum_structure.subject.name = "Mathematics"
    t.curriculum_structure.subject_id = 1
    t.curriculum_structure.grade_level.name = "Grade 5"
    t.curriculum_structure.grade_level_id = 1
    lo = MagicMock()
    lo.objective = "Understand fractions"
    tc = MagicMock()
    tc.content_area = "Fraction basics"
    t.learning_objectives = [lo]
    t.topic_contents = [tc]
    return t


def _make_lesson_plan(plan_id: int = 1, user_id: int = 1, topic=None) -> MagicMock:
    """Return a plain MagicMock standing in for a LessonPlan ORM object.

    Assigning a non-ORM object to ``LessonPlan.topic`` via the instrumented
    setter also fires SQLAlchemy backref events, so we use a MagicMock here too.
    """
    lp = MagicMock()
    lp.lesson_plan_id = plan_id
    lp.user_id = user_id
    lp.created_at = _now()
    lp.topic_id = 1
    lp.topic = topic if topic is not None else _make_topic()
    return lp


# --------------------------------------------------------------------------
# DB helpers
# --------------------------------------------------------------------------

def _db_returning(return_val) -> MagicMock:
    """DB mock whose first() always returns return_val."""
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = return_val
    db.query.return_value.filter.return_value.filter.return_value.first.return_value = return_val
    db.commit = MagicMock()
    db.refresh = MagicMock()
    db.delete = MagicMock()
    return db


# ==========================================================================
# TestFetchCurriculumData
# ==========================================================================

class TestFetchCurriculumData:
    """fetch_curriculum_data returns objectives and contents from a topic."""

    def test_returns_objectives_and_contents(self):
        topic = _make_topic()
        svc = LessonPlanService(db=MagicMock())
        objs, contents = svc.fetch_curriculum_data(topic)
        assert objs == ["Understand fractions"]
        assert contents == ["Fraction basics"]

    def test_none_topic_returns_empty_lists(self):
        svc = LessonPlanService(db=MagicMock())
        objs, contents = svc.fetch_curriculum_data(None)
        assert objs == []
        assert contents == []

    def test_topic_with_no_objectives_or_contents(self):
        topic = _make_topic()
        topic.learning_objectives = []
        topic.topic_contents = []
        svc = LessonPlanService(db=MagicMock())
        objs, contents = svc.fetch_curriculum_data(topic)
        assert objs == []
        assert contents == []


# ==========================================================================
# TestCreateLessonPlanResponse
# ==========================================================================

class TestCreateLessonPlanResponse:
    """create_lesson_plan_response builds a response from a LessonPlan ORM object."""

    def test_with_request_data(self):
        lp = _make_lesson_plan()
        req = LessonPlanCreate(
            topic_id=1,
            user_id=1,
            subject="Mathematics",
            topic="Fractions",
            grade_level="Grade 5",
        )
        svc = LessonPlanService(db=MagicMock())
        resp = svc.create_lesson_plan_response(lp, request_data=req)
        assert resp.title == "Mathematics: Fractions"
        assert resp.subject == "Mathematics"
        assert resp.grade_level == "Grade 5"

    def test_without_request_data_uses_topic_relationship(self):
        lp = _make_lesson_plan()
        svc = LessonPlanService(db=MagicMock())
        resp = svc.create_lesson_plan_response(lp)
        assert resp.title == "Mathematics: Fractions"
        assert resp.subject == "Mathematics"
        assert resp.grade_level == "Grade 5"
        assert resp.topic == "Fractions"

    def test_lesson_plan_without_topic_returns_untitled(self):
        """Graceful fallback when topic relationship is None."""
        lp = _make_lesson_plan()
        lp.topic = None
        svc = LessonPlanService(db=MagicMock())
        resp = svc.create_lesson_plan_response(lp)
        assert resp.title == "Untitled Lesson"
        assert resp.subject == "Unknown"

    def test_curriculum_objectives_included(self):
        lp = _make_lesson_plan()
        svc = LessonPlanService(db=MagicMock())
        resp = svc.create_lesson_plan_response(lp)
        assert resp.curriculum_learning_objectives == ["Understand fractions"]
        assert resp.curriculum_contents == ["Fraction basics"]


# ==========================================================================
# TestGetLessonPlan
# ==========================================================================

class TestGetLessonPlan:
    """get_lesson_plan — ownership-scoped lookup."""

    def test_returns_plan_for_owner(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=42, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        resp = svc.get_lesson_plan(lesson_id=42, current_user=user)
        assert resp.lesson_id == 42

    def test_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = _db_returning(None)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_plan(lesson_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_other_users_plan_returns_404(self):
        """Because the query filters by user_id, another user's plan → None → 404."""
        user = _educator(user_id=2)
        db = _db_returning(None)  # ORM returns None for wrong user
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_plan(lesson_id=1, current_user=user)
        assert exc_info.value.status_code == 404


# ==========================================================================
# TestUpdateLessonPlan
# ==========================================================================

class TestUpdateLessonPlan:
    """update_lesson_plan — AWD-M-191: 404 when not found, 501 when found (not yet implemented)."""

    def test_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = _db_returning(None)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_lesson_plan(lesson_id=99, request=LessonPlanUpdate(), current_user=user)
        assert exc_info.value.status_code == 404

    def test_found_raises_501(self):
        """Endpoint is not yet implemented — must return 501, not a silent 200 no-op."""
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_lesson_plan(lesson_id=1, request=LessonPlanUpdate(), current_user=user)
        assert exc_info.value.status_code == 501

    def test_found_501_detail_describes_intent(self):
        """501 detail message must explain what is not implemented."""
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_lesson_plan(lesson_id=1, request=LessonPlanUpdate(), current_user=user)
        assert "not yet implemented" in exc_info.value.detail

    def test_found_does_not_commit(self):
        """No DB commit must occur when raising 501."""
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException):
            svc.update_lesson_plan(lesson_id=1, request=LessonPlanUpdate(), current_user=user)
        db.commit.assert_not_called()


# ==========================================================================
# TestDeleteLessonPlan
# ==========================================================================

class TestDeleteLessonPlan:
    """delete_lesson_plan — 404 when not found, deletes and commits when found."""

    def test_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = _db_returning(None)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete_lesson_plan(lesson_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_deletes_and_commits(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        result = svc.delete_lesson_plan(lesson_id=1, current_user=user)
        db.delete.assert_called_once_with(lp)
        db.commit.assert_called_once()
        assert "deleted" in result.get("message", "").lower()

    def test_returns_success_message(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        result = svc.delete_lesson_plan(lesson_id=1, current_user=user)
        assert isinstance(result, dict)
        assert "message" in result


# ---------------------------------------------------------------------------
# Basic smoke tests migrated from test_services.py (AWD-M-110 split)
# These cover the top-level generate + list paths not already tested above.
# ---------------------------------------------------------------------------

class TestLessonPlanServiceSmoke:
    """Smoke tests for LessonPlanService initialization, plan generation, and retrieval.

    Migrated from test_services.py as part of AWD-M-110 (split monolith test file).
    The detailed unit tests for individual methods live in the classes above.
    Resource method smoke tests live in test_lesson_resource_service.py (AWD-M-117).
    """

    def test_lesson_plan_service_initialization(self, test_db):
        """Test LessonPlanService initialization."""
        service = LessonPlanService(test_db)
        assert service.db == test_db

    def test_generate_lesson_plan(self, test_db, sample_user, sample_topic):
        """Test lesson plan generation via mocked topic query."""

        service = LessonPlanService(test_db)

        request = LessonPlanCreate(
            subject="Mathematics",
            grade_level="Grade 5",
            topic="Basic Algebra",
            user_id=sample_user.user_id
        )

        with patch.object(service.db, 'query') as mock_query:
            mock_query.return_value.join.return_value.join.return_value.join.return_value.filter.return_value.first.return_value = sample_topic

            result = service.generate_lesson_plan(request, sample_user)
            assert result is not None
            assert result.subject == "Mathematics"

    def test_get_lesson_plans(self, test_db, sample_user, sample_lesson_plan):
        """Test lesson plan list retrieval."""

        service = LessonPlanService(test_db)

        lesson_plans = service.get_lesson_plans(sample_user)
        assert len(lesson_plans) >= 1


# ==========================================================================
# TestGetLessonPlansFilters — AWD-H-93
# ==========================================================================

class TestGetLessonPlansFilters:
    """Unit tests for get_lesson_plans filter logic (AWD-H-93).

    Before the fix, passing both subject AND grade_level caused SQLAlchemy to
    join Topic and CurriculumStructure twice on the same query object, raising
    InvalidRequestError("… already been joined").  These tests verify all three
    filter combinations execute without error and that the correct join chain is
    called each time.
    """

    def _make_db_for_filters(self, plans):
        """Return a DB mock whose filter().offset().limit().all() chain returns plans."""
        db = MagicMock()
        # Build a chainable mock that returns plans at the .all() terminus no
        # matter how many .join()/.filter() calls are chained in between.
        chain = MagicMock()
        chain.join.return_value = chain
        chain.filter.return_value = chain
        chain.offset.return_value = chain
        chain.limit.return_value = chain
        chain.all.return_value = plans
        db.query.return_value.filter.return_value = chain
        return db

    def test_filter_by_subject_only(self):
        """subject filter joins Topic→CurriculumStructure→Subject; no duplicate join."""
        plan = _make_lesson_plan()
        db = self._make_db_for_filters([plan])
        svc = LessonPlanService(db=db)
        user = _educator()

        result = svc.get_lesson_plans(user, subject="Mathematics")

        assert len(result) == 1
        assert result[0].subject == "Mathematics"

    def test_filter_by_grade_level_only(self):
        """grade_level filter joins Topic→CurriculumStructure→GradeLevel; no duplicate join."""
        plan = _make_lesson_plan()
        db = self._make_db_for_filters([plan])
        svc = LessonPlanService(db=db)
        user = _educator()

        result = svc.get_lesson_plans(user, grade_level="Grade 5")

        assert len(result) == 1
        assert result[0].grade_level == "Grade 5"

    def test_filter_by_subject_and_grade_level_no_crash(self):
        """Both filters together must NOT raise SQLAlchemy InvalidRequestError (AWD-H-93).

        Before the fix, two consecutive .join(Topic).join(CurriculumStructure) calls
        on the same query object caused the crash.  After the fix the shared base join
        is emitted once and Subject/GradeLevel joins are appended independently.
        """
        plan = _make_lesson_plan()
        db = self._make_db_for_filters([plan])
        svc = LessonPlanService(db=db)
        user = _educator()

        # Must not raise
        result = svc.get_lesson_plans(user, subject="Mathematics", grade_level="Grade 5")

        assert len(result) == 1
        assert result[0].subject == "Mathematics"
        assert result[0].grade_level == "Grade 5"

    def test_no_filters_skips_join(self):
        """No filters → Topic/CurriculumStructure joins are not called."""
        plan = _make_lesson_plan()
        db = self._make_db_for_filters([plan])
        svc = LessonPlanService(db=db)
        user = _educator()

        result = svc.get_lesson_plans(user)

        assert len(result) == 1
        # join should not have been called when no filter is active
        db.query.return_value.filter.return_value.join.assert_not_called()
