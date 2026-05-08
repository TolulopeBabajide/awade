"""
Tests for UserService.

Split from test_services.py (AWD-M-110).
Covers: initialization, paginated retrieval, get-by-ID, and 404 handling.

Author: Tolulope Babajide
"""

import pytest
from unittest.mock import Mock
from fastapi import HTTPException

from services.user_service import UserService


class TestUserService:
    """Test user service."""

    def test_user_service_initialization(self, test_db):
        """Test UserService initialization."""
        service = UserService(test_db)
        assert service.db == test_db

    def test_get_users_pagination(self, test_db, sample_user):
        """Test user retrieval with pagination."""
        service = UserService(test_db)

        users = service.get_users(skip=0, limit=10)
        assert len(users) >= 1
        assert any(user.email == "test@example.com" for user in users)

    def test_get_user_by_id(self, test_db, sample_user):
        """Test get user by ID."""
        service = UserService(test_db)

        # Pass owner as current_user — owner may read their own record
        user = service.get_user(sample_user.user_id, current_user=sample_user)
        assert user is not None
        assert user.email == "test@example.com"

    def test_get_user_not_found(self, test_db):
        """Test get user when not found."""
        service = UserService(test_db)

        # Use caller.user_id == requested id — ownership check short-circuits,
        # service proceeds to DB lookup and raises 404 for the missing record
        caller = Mock()
        caller.user_id = 99999
        with pytest.raises(HTTPException) as exc_info:
            service.get_user(99999, current_user=caller)
        assert exc_info.value.status_code == 404
