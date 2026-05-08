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
from apps.backend.services.lesson_plan_service import (
    LessonPlanService,
    _to_lesson_resource_response,
)


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


def _super_admin(user_id: int = 100) -> User:
    return _make_user(user_id, UserRole.SUPER_ADMIN)


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
    # Attribute chains read by create_lesson_plan_response and generate_lesson_resource
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

    def test_super_admin_can_list_resources(self):
        """AWD-H-62: SUPER_ADMIN must bypass ownership check in get_lesson_plan_resources."""
        super_admin = _super_admin(user_id=100)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        r1 = _make_resource(resource_id=10, lesson_plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [r1])
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=super_admin)
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

    def test_super_admin_can_access_any_resource(self):
        """AWD-H-61: SUPER_ADMIN must bypass ownership scoping like ADMIN."""
        super_admin = _super_admin(user_id=100)
        resource = _make_resource(resource_id=1, user_id=1)  # owned by user 1
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource(resource_id=1, current_user=super_admin)
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


# ==========================================================================
# TestGetLessonResourceOrm — AWD-M-70
# ==========================================================================


class TestGetLessonResourceOrm:
    """get_lesson_resource_orm — single source of truth for export access control.

    AWD-M-70 extracted the ADMIN/SUPER_ADMIN/owner-scoped query into one helper
    so the export router can delegate. These tests cover the same behaviours as
    TestGetLessonResource but against the ORM-returning entry point used by
    routers/lesson_plans.py::export_lesson_resource.
    """

    def test_resource_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_resource_orm(resource_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_wrong_user_returns_404_not_403(self):
        # AWD-M-67: non-admin querying another user's resource gets 404, not 403.
        # The scoped query returns None for the foreign user_id.
        user = _educator(user_id=2)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_resource_orm(resource_id=1, current_user=user)
        assert exc_info.value.status_code == 404

    def test_owner_gets_orm_object(self):
        user = _educator(user_id=1)
        resource = _make_resource(resource_id=1, lesson_plan_id=5, user_id=1)
        resource.ai_generated_content = "Detailed lesson content"
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource_orm(resource_id=1, current_user=user)
        # Returns the raw ORM object, not a response schema (export needs ORM)
        assert result is resource
        assert isinstance(result, LessonResource)

    def test_admin_can_access_any_resource(self):
        admin = _admin(user_id=99)
        resource = _make_resource(resource_id=1, user_id=1)  # owned by user 1
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource_orm(resource_id=1, current_user=admin)
        assert result is resource

    def test_super_admin_can_access_any_resource(self):
        """AWD-H-61: SUPER_ADMIN must bypass ownership scoping like ADMIN."""
        super_admin = _super_admin(user_id=100)
        resource = _make_resource(resource_id=1, user_id=1)  # owned by user 1
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)
        result = svc.get_lesson_resource_orm(resource_id=1, current_user=super_admin)
        assert result is resource


# ==========================================================================
# TestToLessonResourceResponse — AWD-M-118
# ==========================================================================


class TestToLessonResourceResponse:
    """_to_lesson_resource_response — single source of truth for ORM → DTO mapping.

    AWD-M-118 extracted the duplicated 9-kwarg ``LessonResourceResponse(...)``
    constructor into one private helper. These tests pin the field-by-field
    mapping so any future change to ``LessonResource`` or the response schema
    is caught here rather than at four divergent call sites.
    """

    def test_all_fields_mapped(self):
        resource = _make_resource(resource_id=42, lesson_plan_id=7, user_id=3)
        resource.context_input = "rural primary classroom"
        resource.ai_generated_content = "AI body"
        resource.user_edited_content = "teacher edits"
        resource.export_format = "pdf"
        resource.status = "complete"

        result = _to_lesson_resource_response(resource)

        assert isinstance(result, LessonResourceResponse)
        assert result.lesson_resources_id == 42
        assert result.lesson_plan_id == 7
        assert result.user_id == 3
        assert result.context_input == "rural primary classroom"
        assert result.ai_generated_content == "AI body"
        assert result.user_edited_content == "teacher edits"
        assert result.export_format == "pdf"
        assert result.status == "complete"
        assert result.created_at == resource.created_at

    def test_optional_fields_pass_through_as_none(self):
        """``user_edited_content`` and ``export_format`` are nullable on the ORM
        and the response — verify ``None`` round-trips cleanly."""
        resource = _make_resource(resource_id=1, lesson_plan_id=1, user_id=1)
        resource.user_edited_content = None
        resource.export_format = None
        resource.context_input = None
        resource.ai_generated_content = None

        result = _to_lesson_resource_response(resource)

        assert result.user_edited_content is None
        assert result.export_format is None
        assert result.context_input is None
        assert result.ai_generated_content is None
        assert result.status == "draft"

    def test_helper_used_by_get_lesson_resource(self):
        """End-to-end: get_lesson_resource must produce the same response the
        helper would. This is the safety-net that keeps the four converted
        call sites tied to ``_to_lesson_resource_response``."""
        user = _educator(user_id=1)
        resource = _make_resource(resource_id=5, lesson_plan_id=2, user_id=1)
        resource.context_input = "urban context"
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonPlanService(db=db)

        from_service = svc.get_lesson_resource(resource_id=5, current_user=user)
        from_helper = _to_lesson_resource_response(resource)

        assert from_service.model_dump() == from_helper.model_dump()


# ==========================================================================
# TestGenerateLessonResource
# ==========================================================================

class TestGenerateLessonResource:
    """generate_lesson_resource — 403 wrong user, SUPER_ADMIN bypass."""

    def _db_for_generate(self, plan_obj) -> MagicMock:
        """DB mock that drives the full generate_lesson_resource query sequence.

        Query order inside generate_lesson_resource:
          1. LessonPlan  .filter().first()
          2. Topic       .filter().first()
          3. CurriculumStructure .filter().first()
          4. Subject     .filter().first()
          5. GradeLevel  .filter().first()
          6. Context     .filter().all()
        Then: db.add / db.commit / db.refresh
        """
        db = MagicMock()
        call_count = [0]

        topic = MagicMock()
        topic.topic_id = 1
        topic.curriculum_structure_id = 1
        topic.learning_objectives = []
        topic.topic_contents = []

        cs = MagicMock()
        cs.subject_id = 1
        cs.grade_level_id = 1

        subject = MagicMock()
        subject.name = "Mathematics"

        grade_level = MagicMock()
        grade_level.name = "Grade 5"

        def query_side(_model):
            q = MagicMock()
            call_count[0] += 1
            n = call_count[0]
            if n == 1:
                q.filter.return_value.first.return_value = plan_obj
            elif n == 2:
                q.filter.return_value.first.return_value = topic
            elif n == 3:
                q.filter.return_value.first.return_value = cs
            elif n == 4:
                q.filter.return_value.first.return_value = subject
            elif n == 5:
                q.filter.return_value.first.return_value = grade_level
            else:
                q.filter.return_value.all.return_value = []
            return q

        db.query.side_effect = query_side

        def _refresh(obj):
            obj.lesson_resources_id = 99

        db.refresh.side_effect = _refresh
        return db

    def test_wrong_user_raises_403(self):
        import asyncio
        user = _educator(user_id=2)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        lp.topic_id = 1
        db = self._db_for_generate(lp)
        svc = LessonPlanService(db=db)
        from apps.backend.schemas.lesson_plans import LessonResourceCreate
        data = LessonResourceCreate(lesson_plan_id=1)
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(svc.generate_lesson_resource(lesson_id=1, data=data, current_user=user))
        assert exc_info.value.status_code == 403

    def test_super_admin_can_generate_resource(self):
        """AWD-H-62: SUPER_ADMIN must bypass ownership check in generate_lesson_resource."""
        import asyncio
        super_admin = _super_admin(user_id=100)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1, not super_admin
        lp.topic_id = 1
        db = self._db_for_generate(lp)
        svc = LessonPlanService(db=db)
        from apps.backend.schemas.lesson_plans import LessonResourceCreate
        data = LessonResourceCreate(lesson_plan_id=1)
        result = asyncio.run(svc.generate_lesson_resource(lesson_id=1, data=data, current_user=super_admin))
        assert result.status == "processing"


# ---------------------------------------------------------------------------
# Basic smoke tests migrated from test_services.py (AWD-M-110 split)
# These cover the top-level generate + list paths not already tested above.
# ---------------------------------------------------------------------------

class TestLessonPlanServiceSmoke:
    """Smoke tests for LessonPlanService initialization, plan generation, and retrieval.

    Migrated from test_services.py as part of AWD-M-110 (split monolith test file).
    The detailed unit tests for individual methods live in the classes above.
    """

    def test_lesson_plan_service_initialization(self, test_db):
        """Test LessonPlanService initialization."""
        from apps.backend.services.lesson_plan_service import LessonPlanService
        service = LessonPlanService(test_db)
        assert service.db == test_db

    def test_generate_lesson_plan(self, test_db, sample_user, sample_topic):
        """Test lesson plan generation via mocked topic query."""
        from apps.backend.services.lesson_plan_service import LessonPlanService
        from apps.backend.schemas.lesson_plans import LessonPlanCreate
        from unittest.mock import patch

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
        from apps.backend.services.lesson_plan_service import LessonPlanService

        service = LessonPlanService(test_db)

        lesson_plans = service.get_lesson_plans(sample_user)
        assert len(lesson_plans) >= 1
