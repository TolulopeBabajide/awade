"""
AWD-M-182: ChildrenService tests — role gating and ownership.

Covers:
  - TestRoleGating: _verify_parent must raise 403 for EDUCATOR role
  - TestOwnership: _get_child_or_404 returns child when owner matches, 404 otherwise
"""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from children_service_factories import (
    _make_user, _parent, _educator, _child,
)

from apps.backend.models import UserRole
from apps.backend.services.children_service import ChildrenService
from apps.backend.services.parent_guide_service import ParentGuideService
from apps.backend.schemas.children import ChildProfileCreate, ChildProfileUpdate


# ---------------------------------------------------------------------------
# Role gating — _verify_parent
# ---------------------------------------------------------------------------

class TestRoleGating:
    """_verify_parent must raise 403 for EDUCATOR role."""

    def _service(self):
        return ChildrenService(db=MagicMock())

    def test_educator_create_child_raises_403(self):
        svc = self._service()
        with pytest.raises(HTTPException) as exc_info:
            svc._verify_parent(_educator())
        assert exc_info.value.status_code == 403

    def test_parent_does_not_raise(self):
        svc = self._service()
        # Must not raise for PARENT
        svc._verify_parent(_parent())

    def test_admin_does_not_raise(self):
        svc = self._service()
        admin = _make_user(99, UserRole.ADMIN)
        svc._verify_parent(admin)

    def test_super_admin_does_not_raise(self):
        svc = self._service()
        super_admin = _make_user(100, UserRole.SUPER_ADMIN)
        svc._verify_parent(super_admin)

    def test_create_child_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.create_child(_educator(), ChildProfileCreate(name="Alice"))
        assert exc_info.value.status_code == 403

    def test_list_children_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.list_children(_educator())
        assert exc_info.value.status_code == 403

    def test_get_child_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.get_child(_educator(), child_id=1)
        assert exc_info.value.status_code == 403

    def test_delete_child_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ChildrenService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete_child(_educator(), child_id=1)
        assert exc_info.value.status_code == 403

    def test_generate_guide_raises_403_for_educator(self):
        mock_db = MagicMock()
        svc = ParentGuideService(db=mock_db)
        with pytest.raises(HTTPException) as exc_info:
            svc.generate_guide(_educator(), child_id=1, topic_id=1)
        assert exc_info.value.status_code == 403


# ---------------------------------------------------------------------------
# Ownership — _get_child_or_404
# ---------------------------------------------------------------------------

class TestOwnership:
    """_get_child_or_404 returns child when owner matches, 404 otherwise."""

    def _db_returns(self, child_or_none):
        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.filter.return_value.first.return_value = child_or_none
        mock_db.query.return_value = q
        return mock_db

    def test_returns_child_for_correct_owner(self):
        c = _child(child_id=5, parent_id=1)
        svc = ChildrenService(db=self._db_returns(c))
        result = svc._get_child_or_404(child_id=5, parent_id=1)
        assert result.child_id == 5

    def test_raises_404_when_child_not_found(self):
        svc = ChildrenService(db=self._db_returns(None))
        with pytest.raises(HTTPException) as exc_info:
            svc._get_child_or_404(child_id=99, parent_id=1)
        assert exc_info.value.status_code == 404

    def test_get_child_returns_404_for_wrong_parent(self):
        """get_child uses parent_id from user — wrong user → 404."""
        svc = ChildrenService(db=self._db_returns(None))
        parent_a = _parent(user_id=1)
        # DB returns None because parent_id filter doesn't match parent_a
        with pytest.raises(HTTPException) as exc_info:
            svc.get_child(parent_a, child_id=5)
        assert exc_info.value.status_code == 404

    def test_update_child_returns_404_for_wrong_parent(self):
        svc = ChildrenService(db=self._db_returns(None))
        parent_a = _parent(user_id=1)
        with pytest.raises(HTTPException) as exc_info:
            svc.update_child(parent_a, child_id=5, data=ChildProfileUpdate(name="X"))
        assert exc_info.value.status_code == 404

    def test_delete_child_returns_404_for_wrong_parent(self):
        svc = ChildrenService(db=self._db_returns(None))
        parent_a = _parent(user_id=1)
        with pytest.raises(HTTPException) as exc_info:
            svc.delete_child(parent_a, child_id=5)
        assert exc_info.value.status_code == 404
