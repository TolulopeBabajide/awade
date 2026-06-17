"""
Tests for LessonResourceService read paths — AWD-M-259 split.

Split from test_lesson_resource_service.py (575 lines) into focused modules.
Covers:
- _assert_lesson_plan_ownership (shared 403 guard — AWD-M-193)
- get_all_lesson_resources (empty, populated, field mapping)
- get_lesson_plan_resources (404 no plan, 403 wrong user, 200, admin/super_admin bypass)
- get_lesson_resource (404, 404 cross-user, 200, admin/super_admin bypass, field mapping)
- get_lesson_resource_orm (same access-control guarantees, raw ORM return)
- _to_lesson_resource_response (all fields mapped, optional fields as None, end-to-end)
"""

import pytest
import sys
import os
from unittest.mock import MagicMock
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

from apps.backend.models import LessonResource
from apps.backend.schemas.lesson_plans import LessonResourceResponse
from apps.backend.services.lesson_resource_service import (
    LessonResourceService,
    _to_lesson_resource_response,
)
from lesson_resource_factories import (
    _educator, _admin, _super_admin,
    _make_lesson_plan, _make_resource,
    _db_all_returning,
)

# ==========================================================================
# TestAssertLessonPlanOwnership — AWD-M-193
# ==========================================================================

class TestAssertLessonPlanOwnership:
    """_assert_lesson_plan_ownership — shared 403 guard for lesson-plan access.

    AWD-M-193: extracted from the inline guards that were duplicated in
    generate_lesson_resource and get_lesson_plan_resources.
    """

    def _svc(self) -> LessonResourceService:
        return LessonResourceService(db=MagicMock())

    def test_owner_passes(self):
        svc = self._svc()
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        user = _educator(user_id=1)
        svc._assert_lesson_plan_ownership(lp, user)  # must not raise

    def test_wrong_user_raises_403(self):
        svc = self._svc()
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        other = _educator(user_id=2)
        with pytest.raises(HTTPException) as exc_info:
            svc._assert_lesson_plan_ownership(lp, other)
        assert exc_info.value.status_code == 403

    def test_admin_passes_even_for_other_user_plan(self):
        svc = self._svc()
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        admin = _admin(user_id=99)
        svc._assert_lesson_plan_ownership(lp, admin)  # must not raise

    def test_super_admin_passes_even_for_other_user_plan(self):
        svc = self._svc()
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        super_admin = _super_admin(user_id=100)
        svc._assert_lesson_plan_ownership(lp, super_admin)  # must not raise


# ==========================================================================
# TestGetAllLessonResources
# ==========================================================================

class TestGetAllLessonResources:
    """get_all_lesson_resources — returns user's resources ordered by created_at."""

    def test_empty_returns_empty_list(self):
        user = _educator(user_id=1)
        db = _db_all_returning([])
        svc = LessonResourceService(db=db)
        result = svc.get_all_lesson_resources(current_user=user)
        assert result == []

    def test_returns_only_user_resources(self):
        user = _educator(user_id=1)
        r1 = _make_resource(resource_id=1, user_id=1)
        r2 = _make_resource(resource_id=2, user_id=1)
        db = _db_all_returning([r1, r2])
        svc = LessonResourceService(db=db)
        result = svc.get_all_lesson_resources(current_user=user)
        assert len(result) == 2
        assert result[0].lesson_resources_id == 1
        assert result[1].lesson_resources_id == 2

    def test_resource_fields_mapped_correctly(self):
        user = _educator(user_id=1)
        r = _make_resource(resource_id=7, lesson_plan_id=3, user_id=1)
        r.ai_generated_content = "AI lesson plan text"
        db = _db_all_returning([r])
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_plan_resources(lesson_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_wrong_user_raises_403(self):
        user = _educator(user_id=2)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        db = self._db_for_plan_resources(lp, [])
        svc = LessonResourceService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_plan_resources(lesson_id=1, current_user=user)
        assert exc_info.value.status_code == 403

    def test_owner_gets_resources(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        r1 = _make_resource(resource_id=10, lesson_plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [r1])
        svc = LessonResourceService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=user)
        assert len(result) == 1
        assert result[0].lesson_resources_id == 10

    def test_admin_can_access_any_plan_resources(self):
        admin = _admin(user_id=99)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        r1 = _make_resource(resource_id=10, lesson_plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [r1])
        svc = LessonResourceService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=admin)
        assert len(result) == 1

    def test_super_admin_can_list_resources(self):
        """AWD-H-62: SUPER_ADMIN must bypass ownership check in get_lesson_plan_resources."""
        super_admin = _super_admin(user_id=100)
        lp = _make_lesson_plan(plan_id=1, user_id=1)  # owned by user 1
        r1 = _make_resource(resource_id=10, lesson_plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [r1])
        svc = LessonResourceService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=super_admin)
        assert len(result) == 1

    def test_empty_resources_returns_empty_list(self):
        user = _educator(user_id=1)
        lp = _make_lesson_plan(plan_id=1, user_id=1)
        db = self._db_for_plan_resources(lp, [])
        svc = LessonResourceService(db=db)
        result = svc.get_lesson_plan_resources(lesson_id=1, current_user=user)
        assert result == []


# ==========================================================================
# TestGetLessonResource
# ==========================================================================

class TestGetLessonResource:
    """get_lesson_resource — 404, 404 cross-user, 200, admin/super_admin bypass."""

    def test_resource_not_found_raises_404(self):
        user = _educator(user_id=1)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_lesson_resource_orm(resource_id=99, current_user=user)
        assert exc_info.value.status_code == 404

    def test_wrong_user_returns_404_not_403(self):
        # AWD-M-67: non-admin querying another user's resource gets 404, not 403.
        user = _educator(user_id=2)
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = None
        db.query.return_value = q
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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
        svc = LessonResourceService(db=db)
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

    Moved to this module as part of AWD-M-117 (LessonResourceService extraction).
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
        helper would. This is the safety-net that keeps the converted call sites
        tied to ``_to_lesson_resource_response``."""
        user = _educator(user_id=1)
        resource = _make_resource(resource_id=5, lesson_plan_id=2, user_id=1)
        resource.context_input = "urban context"
        db = MagicMock()
        q = MagicMock()
        q.filter.return_value.first.return_value = resource
        db.query.return_value = q
        svc = LessonResourceService(db=db)

        from_service = svc.get_lesson_resource(resource_id=5, current_user=user)
        from_helper = _to_lesson_resource_response(resource)

        assert from_service.model_dump() == from_helper.model_dump()
