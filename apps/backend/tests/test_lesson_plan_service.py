"""
Tests for AWD-M-04 — shore up LessonPlanService coverage.

Covers untested service methods:
- fetch_curriculum_data
- create_lesson_plan_response (with and without request_data)
- get_lesson_plan  (404, 200)
- update_lesson_plan (404, 200)
- delete_lesson_plan (404, 200)
- get_all_lesson_resources (empty, populated)
- get_lesson_plan_resources (404 no plan, 403 wrong user, 200, admin bypass)
- get_lesson_resource (404, 404 cross-user, 200, admin bypass)
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


def _admin(user_id: int = 99) -> User:
    return _make_user(user_id, UserRole.ADMIN)


def _make_topic(topic_id: int = 1, title: str = "Fractions") -> Topic:
    t = Topic()
    t.topic_id = topic_id
    t.topic_title = title
    cs = CurriculumStructure()
    subj = Subject()
    subj.name = "Mathematics"
    gl = GradeLevel()
    gl.name = "Grade 5"
    cs.subject = subj
    cs.grade_level = gl
    t.curriculum_structure = cs
    lo = MagicMock(spec=LearningObjective)
    lo.objective = "Understand fractions"
    tc = MagicMock(spec=TopicContent)
    tc.content_area = "Fraction basics"
    t.learning_objectives = [lo]
    t.topic_contents = [tc]
    return t


def _make_lesson_plan(plan_id: int = 1, user_id: int = 1, topic: Topic = None) -> LessonPlan:
    lp = LessonPlan()
    lp.lesson_plan_id = plan_id
    lp.user_id = user_id
    lp.created_at = _now()
    lp.topic = topic or _make_topic()
    return lp


def _make_resource(resource_id: int = 1, lesson_plan_id: int = 1, user_id: int = 1) -> LessonResource:
    r = LessonResource()
    r.lesson_resources_id = resource_id
    r.lesson_plan_id = lesson_plan_id
    r.user_id = user_id
    r.context_input = "Some context"
    r.ai_generated_content = "AI content"
    r.user_edited_content = None
    r.export_format = None
    r.status = "draft"
    r.created_at = _now()
    return r


# --------------------------------------------------------------------------
# Helpers
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


def _db_all_returning(items) -> MagicMock:
    """DB mock whose all() returns items."""
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = items
    db.query.return_value.filter.return_value.all.return_value = items
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
    """update_lesson_plan — 404 when not found, commits when found."""

    def test_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = _db_returning(None)
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_lesson_plan(lesson_id=99, request=LessonPlanUpdate(), current_user=user)
        assert exc_info.value.status_code == 404

    def test_commits_on_successful_update(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        svc.update_lesson_plan(lesson_id=1, request=LessonPlanUpdate(), current_user=user)
        db.commit.assert_called_once()

    def test_returns_response_on_success(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = _db_returning(lp)
        svc = LessonPlanService(db=db)
        resp = svc.update_lesson_plan(lesson_id=1, request=LessonPlanUpdate(), current_user=user)
        assert resp.lesson_id == 1


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


# ==========================================================================
# TestGetAllLessonResources
# ==========================================================================

class TestGetAllLessonResources:
    """get_all_lesson_resources — returns user's resources ordered by created_at."""

    def test_empty_returns_empty_list(self):
        user = _educator(user_id=1)
        db = _db_all_returning([])
        svc = LessonPlanService(db=db)
        result = svc.get_all_lesson_resources(current_user=user)
        assert result == []

    def test_returns_only_user_resources(self):
        user = _educator(user_id=1)
        r1 = _make_resource(resource_id=1, user_id=1)
        r2 = _make_resource(resource_id=2, user_id=1)
        db = _db_all_returning([r1, r2])
        svc = LessonPlanService(db=db)
        result = svc.get_all_lesson_resources(current_user=user)
        assert len(result) == 2
        assert result[0].lesson_resources_id == 1
        assert result[1].lesson_resources_id == 2

    def test_resource_fields_mapped_correctly(self):
        user = _educator(user_id=1)
        r = _make_resource(resource_id=7, lesson_plan_id=3, user_id=1)
        r.ai_generated_content = "AI lesson plan text"
        db = _db_all_returning([r])
        svc = LessonPlanService(db=db)
        result = svc.get_all_lesson_resources(current_user=user)
        resp = result[0]
        assert resp.lesson_resources_id == 7
        assert resp.lesson_plan_id == 3
        assert resp.ai_generated_content == "AI lesson plan text"
        assert resp.status == "draft"


# ==========================================================================
# TestGetLessonPlanResources
# ==========================================================================

class TestGetLessonPlanResources:
    """get_lesson_plan_resources — 404 no plan, 403 wrong user, 200, admin bypass."""

    def _db_for_plan_resources(self, plan_obj, resources) -> MagicMock:
        db = MagicMock()
        call_count = [0]

        def query_side(model_arg):
            q = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                # LessonPlan lookup
                q.filter.return_value.first.return_value = plan_obj
            else:
                # LessonResource query
                q.filter.return_value.order_by.return_value.all.return_value = resources
            return q

        db.query.side_effect = query_side
        return db

    def test_plan_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_plan_resources(lesson_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_wrong_user_raises_403(self):
        user = _educator(user_id=2)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        db = self._db_for_plan_resources(lp, [])
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_plan_resources(lesson_id=1, current_user=user)
        assert exc_info.value.status_code == 403

    def test_owner_gets_resources(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        r1 = _make_resource(resource_id=10, lesson_plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [r1])
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=user)
        assert len(result) == 1
        assert result[0].lesson_resources_id == 10

    def test_admin_can_access_any_plan_resources(self):
        admin = _admin(user_id=99)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        r1 = _make_resource(resource_id=10, lesson_plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [r1])
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=admin)
        assert len(result) == 1

    def test_empty_resources_returns_empty_list(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [])
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=user)
        assert result == []


# ==========================================================================
# TestGetLessonResource
# ==========================================================================

class TestGetLessonResource:
    """get_lesson_resource — 404, 403, 200, admin bypass."""

    def test_resource_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_resource(resource_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_wrong_user_returns_404_not_403(self):
        # AWD-M-67: non-admin querying another user's resource gets 404, not 403,
        # so the existence of the resource is not revealed.
        user = _educator(user_id=2)
        db = MagicMock()
        q = MagicMock()
        # Scoped query returns None — resource_id exists but is owned by user 1
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_resource(resource_id=1, current_user=user)
        assert exc_info.value.status_code == 404

    def test_owner_gets_resource(self):
        user = _educator(user_id=1)
        resource = _make_resource(resource_id=1, lesson_plan_id=5, user_id=1)
        resource.ai_generated_content = "Detailed lesson content"
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource(resource_id=1, current_user=user)
        assert result.lesson_resources_id == 1
        assert result.lesson_plan_id == 5
        assert result.ai_generated_content == "Detailed lesson content"

    def test_admin_can_access_any_resource(self):
        admin = _admin(user_id=99)
        resource = _make_resource(resource_id=1, user_id=1)  # owned by user 1
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource(resource_id=1, current_user=admin)
        assert result.lesson_resources_id == 1

    def test_resource_fields_mapped_correctly(self):
        user = _educator(user_id=1)
        resource = _make_resource(resource_id=3, lesson_plan_id=2, user_id=1)
        resource.context_input = "Nigerian classroom context"
        resource.user_edited_content = "Edited by teacher"
        resource.export_format = "pdf"
        resource.status = "complete"
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource(resource_id=3, current_user=user)
        assert result.context_input == "Nigerian classroom context"
        assert result.user_edited_content == "Edited by teacher"
        assert result.export_format == "pdf"
        assert result.status == "complete"
