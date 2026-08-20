"""
Shared factories and helpers for lesson-resource test suite.

Split from test_lesson_resource_service.py (AWD-M-259) — imported by:
  test_lesson_resource_read.py, test_lesson_resource_generate.py.

Do NOT import pytest fixtures here — this module is plain Python.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from apps.backend.models import LessonResource, User, UserRole


# ---------------------------------------------------------------------------
# User factories
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Resource factories
# ---------------------------------------------------------------------------

def _make_lesson_plan(plan_id: int = 1, user_id: int = 1) -> MagicMock:
    lp = MagicMock()
    lp.lesson_plan_id = plan_id
    lp.user_id = user_id
    lp.created_at = _now()
    lp.topic_id = 1
    return lp


def _make_resource(
    resource_id: int = 1, lesson_plan_id: int = 1, user_id: int = 1
) -> LessonResource:
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


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _db_all_returning(items) -> MagicMock:
    """DB mock whose all() returns items."""
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = items
    db.query.return_value.filter.return_value.all.return_value = items
    return db
