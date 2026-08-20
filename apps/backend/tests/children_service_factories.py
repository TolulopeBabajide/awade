"""
Shared test factories for ChildrenService unit-test files.

Imported by:
  test_children_service_role.py
  test_children_service_crud.py
  test_children_service_guides.py
  test_children_service_db_errors.py

AWD-M-182: test_children_service.py split into focused files.
"""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import sys
import os

# Path fixups for sandbox
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, root_dir)

# Sandbox compat shim: datetime.UTC added in Python 3.11
import datetime as _dt
if not hasattr(_dt, "UTC"):
    _dt.UTC = _dt.timezone.utc

from apps.backend.models import (
    ChildProfile, ParentGuide, User, UserRole,
)


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def _now():
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# User factories
# ---------------------------------------------------------------------------

def _make_user(user_id: int, role: UserRole) -> User:
    u = User()
    u.user_id = user_id
    u.email = f"user{user_id}@example.com"
    u.role = role
    u.is_suspended = False
    return u


def _parent(user_id: int = 1) -> User:
    return _make_user(user_id, UserRole.PARENT)


def _educator(user_id: int = 10) -> User:
    return _make_user(user_id, UserRole.EDUCATOR)


# ---------------------------------------------------------------------------
# Model factories
# ---------------------------------------------------------------------------

def _child(child_id: int, parent_id: int) -> ChildProfile:
    c = ChildProfile()
    c.child_id = child_id
    c.parent_id = parent_id
    c.name = f"Child {child_id}"
    c.age = 9
    c.school_name = None
    c.country_id = None
    c.curricula_id = 1
    c.grade_level_id = 1
    c.subjects = None
    c.created_at = _now()
    c.updated_at = _now()
    c.country = None
    c.curriculum = None
    c.grade_level = None
    return c


def _guide(guide_id: int, child_id: int, topic_id: int = 1) -> ParentGuide:
    g = ParentGuide()
    g.guide_id = guide_id
    g.child_id = child_id
    g.topic_id = topic_id
    g.ai_generated_content = None
    g.user_edited_content = None
    g.is_bookmarked = False
    g.created_at = _now()
    g.updated_at = _now()
    t = MagicMock()
    t.topic_title = "Fractions"
    t.curriculum_structure = None
    g.topic = t
    return g


# ---------------------------------------------------------------------------
# Shared AI content fixture
# ---------------------------------------------------------------------------

VALID_AI_CONTENT = {
    "topic_header": {
        "topic": "Fractions",
        "subject": "Mathematics",
        "grade_level": "Grade 5",
        "country": "Nigeria",
        "curriculum": "Nigerian Curriculum",
    },
    "simple_explanation": {
        "what_it_is": "A fraction represents a part of a whole.",
        "why_it_matters": "Fractions are used daily.",
    },
    "home_activity": {
        "title": "Pizza Fraction Fun",
        "description": "Use paper to model fractions.",
        "materials_needed": ["Paper", "Pencil"],
        "steps": ["Fold paper in half", "Label each half"],
        "what_to_look_for": "Child can name each fraction.",
    },
    "conversation_starters": ["What fraction did you eat?"],
    "common_mistakes": [
        {
            "mistake": "Larger denominator = larger fraction",
            "why_it_happens": "Focus on the bigger number.",
            "how_to_help": "Use visual aids.",
        }
    ],
}


# ---------------------------------------------------------------------------
# DB mock helpers (shared across guide-related tests)
# ---------------------------------------------------------------------------

def _db_child_found(parent_user_id: int, child_obj) -> MagicMock:
    """DB mock that returns child_obj for _get_child_or_404 (ownership verified)."""
    db = MagicMock()
    q = MagicMock()
    q.options.return_value.filter.return_value.first.return_value = child_obj
    q.filter.return_value.first.return_value = child_obj
    db.query.return_value = q
    return db


def _db_child_not_found() -> MagicMock:
    """DB mock that returns None for all queries (child not found)."""
    db = MagicMock()
    q = MagicMock()
    q.options.return_value.filter.return_value.first.return_value = None
    q.filter.return_value.first.return_value = None
    db.query.return_value = q
    return db
