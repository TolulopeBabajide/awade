"""
Unit tests for UserService._assert_user_access (AWD-M-173).

Tests the extracted helper directly — no HTTP layer needed.
Covers: owner access, cross-user 403, ADMIN bypass, SUPER_ADMIN bypass.
"""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from apps.backend.models import User, UserRole


class TestAssertUserAccessM173:
    """
    Unit tests for UserService._assert_user_access (AWD-M-173).

    Tests the extracted helper directly — no HTTP layer needed.
    Covers: owner access, cross-user 403, ADMIN bypass, SUPER_ADMIN bypass.
    """

    def _make_service(self, test_db):
        from apps.backend.services.user_service import UserService
        return UserService(test_db)

    def _make_user(self, user_id: int, role: UserRole) -> MagicMock:
        """Build a User stub with the given id and role (MagicMock avoids SA init)."""
        u = MagicMock(spec=User)
        u.user_id = user_id
        u.role = role
        return u

    def test_owner_can_access_own_resource(self, test_db):
        """Caller whose user_id matches target should not raise."""
        svc = self._make_service(test_db)
        caller = self._make_user(42, UserRole.EDUCATOR)
        # Should not raise
        svc._assert_user_access(caller, 42)

    def test_non_owner_educator_raises_403(self, test_db):
        """EDUCATOR accessing a different user's resource must get 403."""
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.EDUCATOR)
        with pytest.raises(HTTPException) as exc_info:
            svc._assert_user_access(caller, 999)
        assert exc_info.value.status_code == 403

    def test_non_owner_parent_raises_403(self, test_db):
        """PARENT accessing a different user's resource must get 403."""
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.PARENT)
        with pytest.raises(HTTPException) as exc_info:
            svc._assert_user_access(caller, 999)
        assert exc_info.value.status_code == 403

    def test_admin_bypasses_ownership_check(self, test_db):
        """ADMIN can access any user_id without raising."""
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.ADMIN)
        # Should not raise for a different user_id
        svc._assert_user_access(caller, 999)

    def test_super_admin_bypasses_ownership_check(self, test_db):
        """SUPER_ADMIN can access any user_id without raising."""
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.SUPER_ADMIN)
        # Should not raise for a different user_id
        svc._assert_user_access(caller, 999)
