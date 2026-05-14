"""
Shared factories and helpers for children-router test suite.

Split from test_children_router.py (AWD-M-116) — imported by:
  test_children_auth.py, test_children_crud.py, test_children_guides.py,
  test_children_export.py, test_children_rate_limits.py.

Do NOT import pytest fixtures here — this module is plain Python.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.dependencies import get_current_active_user
from apps.backend.models import User, UserRole, ChildProfile, ParentGuide

# ---------------------------------------------------------------------------
# Endpoint catalogue (used by parametrized auth/role tests)
# ---------------------------------------------------------------------------

CHILDREN_ENDPOINTS = [
    ("POST",   "/api/children",         {"name": "Alice"}),
    ("GET",    "/api/children",         None),
    ("GET",    "/api/children/1",       None),
    ("PUT",    "/api/children/1",       {"name": "Alice"}),
    ("DELETE", "/api/children/1",       None),
    ("GET",    "/api/children/1/topics", None),
    ("GET",    "/api/children/1/guides", None),
    ("POST",   "/api/children/1/guides/generate?topic_id=1", None),
    ("GET",    "/api/guides/1",         None),
    ("POST",   "/api/guides/1/bookmark", None),
]

# ---------------------------------------------------------------------------
# User factories
# ---------------------------------------------------------------------------


def _make_user(user_id: int, role: UserRole, email: str = None) -> User:
    u = User()
    u.user_id = user_id
    u.email = email or f"user{user_id}@example.com"
    u.role = role
    u.is_suspended = False
    return u


def _make_parent(user_id: int = 1, email: str = "parent@example.com") -> User:
    return _make_user(user_id, UserRole.PARENT, email)


def _make_educator(user_id: int = 10, email: str = "educator@example.com") -> User:
    return _make_user(user_id, UserRole.EDUCATOR, email)


def _auth_override(user: User):
    """Return a dependency function that injects *user* as the current user."""
    def _dep():
        return user
    return _dep


def _now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Domain object factories
# ---------------------------------------------------------------------------


def _make_child_profile(child_id: int, parent_id: int) -> ChildProfile:
    c = ChildProfile()
    c.child_id = child_id
    c.parent_id = parent_id
    c.name = f"Child {child_id}"
    c.age = 8
    c.school_name = None
    c.country_id = None
    c.curricula_id = None
    c.grade_level_id = None
    c.subjects = None
    c.created_at = _now()
    c.updated_at = _now()
    # Lazy relationships — set to None so _to_response handles gracefully
    c.country = None
    c.curriculum = None
    c.grade_level = None
    return c


def _make_guide(guide_id: int, child_id: int, topic_id: int = 1) -> ParentGuide:
    g = ParentGuide()
    g.guide_id = guide_id
    g.child_id = child_id
    g.topic_id = topic_id
    g.ai_generated_content = None
    g.user_edited_content = None
    g.is_bookmarked = False
    g.created_at = _now()
    g.updated_at = _now()
    mock_topic = MagicMock()
    mock_topic.topic_title = "Fractions"
    mock_topic.curriculum_structure = None
    g.topic = mock_topic
    return g


# ---------------------------------------------------------------------------
# Client helper
# ---------------------------------------------------------------------------


def _client_as(user: User) -> TestClient:
    """Return a TestClient with *user* injected as the authenticated user."""
    app.dependency_overrides[get_current_active_user] = _auth_override(user)
    return TestClient(app, raise_server_exceptions=False)
