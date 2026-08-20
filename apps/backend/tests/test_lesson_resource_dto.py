"""
Tests for LessonResourceService DTO-mapping helper — AWD-M-261 split.

Split from test_lesson_resource_read.py (440 lines) into a focused module.
Covers _to_lesson_resource_response: all fields mapped, optional fields as None,
end-to-end consistency with get_lesson_resource.
"""

import sys
import os
from unittest.mock import MagicMock

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

from apps.backend.schemas.lesson_plans import LessonResourceResponse
from apps.backend.services.lesson_resource_service import (
    LessonResourceService,
    _to_lesson_resource_response,
)
from lesson_resource_factories import _educator, _make_resource


# ==========================================================================
# TestToLessonResourceResponse — AWD-M-118
# ==========================================================================

class TestToLessonResourceResponse:
    """_to_lesson_resource_response — single source of truth for ORM → DTO mapping.

    AWD-M-118 extracted the duplicated 9-kwarg ``LessonResourceResponse(...)``
    constructor into one private helper. These tests pin the field-by-field
    mapping so any future change to ``LessonResource`` or the response schema
    is caught here rather than at four divergent call sites.

    Extracted to this module as part of AWD-M-261 (test_lesson_resource_read.py
    size split).
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
