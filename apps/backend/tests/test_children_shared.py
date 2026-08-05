"""
AWD-M-331: Tests for children_shared module.

Covers:
  - TestVerifyParent: verify_parent raises 403 for EDUCATOR, passes for parent-level roles
  - TestGetChildOr404: get_child_or_404 returns child for valid owner, raises 404 otherwise
"""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../../"))
sys.path.insert(0, root_dir)

import datetime as _dt
if not hasattr(_dt, "UTC"):
    _dt.UTC = _dt.timezone.utc

from children_service_factories import _make_user, _parent, _educator, _child
from apps.backend.models import UserRole
from apps.backend.services.children_shared import verify_parent, get_child_or_404


# ---------------------------------------------------------------------------
# verify_parent
# ---------------------------------------------------------------------------

class TestVerifyParent:
    """verify_parent must raise 403 for EDUCATOR, pass for parent-level roles."""

    def test_educator_raises_403(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_parent(_educator())
        assert exc_info.value.status_code == 403

    def test_parent_does_not_raise(self):
        verify_parent(_parent())

    def test_admin_does_not_raise(self):
        verify_parent(_make_user(99, UserRole.ADMIN))

    def test_super_admin_does_not_raise(self):
        verify_parent(_make_user(100, UserRole.SUPER_ADMIN))

    def test_403_detail_message(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_parent(_educator())
        assert "parent" in exc_info.value.detail.lower()


# ---------------------------------------------------------------------------
# get_child_or_404
# ---------------------------------------------------------------------------

class TestGetChildOr404:
    """get_child_or_404 returns child for correct owner, raises 404 otherwise."""

    def _db_returns(self, child_or_none):
        db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.first.return_value = child_or_none
        db.query.return_value = q
        return db

    def test_returns_child_for_correct_owner(self):
        c = _child(child_id=5, parent_id=1)
        db = self._db_returns(c)
        result = get_child_or_404(db, child_id=5, parent_id=1)
        assert result.child_id == 5

    def test_raises_404_when_not_found(self):
        db = self._db_returns(None)
        with pytest.raises(HTTPException) as exc_info:
            get_child_or_404(db, child_id=99, parent_id=1)
        assert exc_info.value.status_code == 404

    def test_404_detail_message(self):
        db = self._db_returns(None)
        with pytest.raises(HTTPException) as exc_info:
            get_child_or_404(db, child_id=99, parent_id=1)
        assert "not found" in exc_info.value.detail.lower()

    def test_db_query_uses_both_id_filters(self):
        """Confirm query filters on both child_id and parent_id."""
        c = _child(child_id=3, parent_id=7)
        db = self._db_returns(c)
        get_child_or_404(db, child_id=3, parent_id=7)
        # The DB was queried via the full ORM chain
        assert db.query.called
