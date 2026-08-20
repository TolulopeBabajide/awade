"""
Unit tests for require_role / require_roles 403 detail — AWD-L-84.

Verifies that role-based guards return a generic "Access denied." detail
and do NOT reveal internal role names to unauthorized callers.
"""

import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

import sys, os
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(backend_dir))
sys.path.insert(0, backend_dir)
sys.path.insert(0, root_dir)

from apps.backend.dependencies import require_role, require_roles
from apps.backend.models import UserRole


def _user(role: UserRole) -> MagicMock:
    u = MagicMock()
    u.role = role
    u.is_suspended = False
    return u


class TestRequireRole:
    """require_role() factory — the returned function is callable directly (bypassing DI)."""

    def test_matching_role_returns_user(self):
        check = require_role(UserRole.EDUCATOR)
        user = _user(UserRole.EDUCATOR)
        assert check(user) == user

    def test_wrong_role_raises_403(self):
        check = require_role(UserRole.EDUCATOR)
        user = _user(UserRole.PARENT)
        with pytest.raises(HTTPException) as exc_info:
            check(user)
        assert exc_info.value.status_code == 403

    def test_403_detail_is_generic(self):
        check = require_role(UserRole.EDUCATOR)
        user = _user(UserRole.PARENT)
        with pytest.raises(HTTPException) as exc_info:
            check(user)
        assert exc_info.value.detail == "Access denied."

    def test_403_detail_does_not_reveal_role_name(self):
        check = require_role(UserRole.SUPER_ADMIN)
        user = _user(UserRole.PARENT)
        with pytest.raises(HTTPException) as exc_info:
            check(user)
        detail = exc_info.value.detail
        assert "SUPER_ADMIN" not in detail
        assert "super_admin" not in detail.lower()
        assert "Required role" not in detail


class TestRequireRoles:
    """require_roles() factory — the returned function is callable directly (bypassing DI)."""

    def test_matching_role_returns_user(self):
        check = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        user = _user(UserRole.ADMIN)
        assert check(user) == user

    def test_wrong_role_raises_403(self):
        check = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        user = _user(UserRole.EDUCATOR)
        with pytest.raises(HTTPException) as exc_info:
            check(user)
        assert exc_info.value.status_code == 403

    def test_403_detail_is_generic(self):
        check = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        user = _user(UserRole.EDUCATOR)
        with pytest.raises(HTTPException) as exc_info:
            check(user)
        assert exc_info.value.detail == "Access denied."

    def test_403_detail_does_not_reveal_role_list(self):
        check = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
        user = _user(UserRole.PARENT)
        with pytest.raises(HTTPException) as exc_info:
            check(user)
        detail = exc_info.value.detail
        assert "ADMIN" not in detail
        assert "Required roles" not in detail
