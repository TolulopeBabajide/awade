"""
Tests for UserService.

Split from test_services.py (AWD-M-110).
Covers: initialization, paginated retrieval, get-by-ID, and 404 handling.
AWD-M-162: added TestApplyUserFields covering the extracted _apply_user_fields
helper and the update_user / update_user_profile delegation paths.

Author: Tolulope Babajide
"""

import json
import pytest
from unittest.mock import Mock, MagicMock
from fastapi import HTTPException

from apps.backend.models import UserRole
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


class TestApplyUserFields:
    """
    Unit tests for UserService._apply_user_fields (AWD-M-162).

    These tests exercise the extracted helper directly with a mock User object
    so they stay fast and database-free.  Integration behaviour (DB round-trip,
    response shape) is covered by TestUpdateUser and TestUpdateUserProfile.
    """

    def _make_service(self) -> UserService:
        """Return a UserService wired to a no-op mock DB."""
        return UserService(db=MagicMock())

    def _make_user(self) -> Mock:
        """Return a minimal mock User with writable attributes."""
        user = Mock()
        user.subjects = None
        user.grade_levels = None
        user.full_name = "Original Name"
        user.bio = None
        return user

    # --- JSON serialization ---

    def test_subjects_list_serialised_to_json(self):
        """subjects list is JSON-encoded and written to user.subjects."""
        service = self._make_service()
        user = self._make_user()
        update_data = {"subjects": ["Math", "Science"]}

        service._apply_user_fields(user, update_data)

        assert user.subjects == json.dumps(["Math", "Science"])

    def test_grade_levels_list_serialised_to_json(self):
        """grade_levels list is JSON-encoded and written to user.grade_levels."""
        service = self._make_service()
        user = self._make_user()
        update_data = {"grade_levels": ["Grade 1", "Grade 2"]}

        service._apply_user_fields(user, update_data)

        assert user.grade_levels == json.dumps(["Grade 1", "Grade 2"])

    def test_subjects_none_not_serialised(self):
        """Explicit None for subjects is stored as-is, not json.dumps(None)."""
        service = self._make_service()
        user = self._make_user()
        update_data = {"subjects": None}

        service._apply_user_fields(user, update_data)

        # setattr is still called, value remains None
        assert user.subjects is None

    def test_grade_levels_none_not_serialised(self):
        """Explicit None for grade_levels is stored as-is."""
        service = self._make_service()
        user = self._make_user()
        update_data = {"grade_levels": None}

        service._apply_user_fields(user, update_data)

        assert user.grade_levels is None

    # --- Plain-field setattr ---

    def test_plain_field_applied_via_setattr(self):
        """Non-JSON fields (e.g. full_name) are applied with setattr."""
        service = self._make_service()
        user = self._make_user()
        update_data = {"full_name": "New Name"}

        service._apply_user_fields(user, update_data)

        assert user.full_name == "New Name"

    def test_multiple_fields_all_applied(self):
        """All fields in update_data are applied in a single call."""
        service = self._make_service()
        user = self._make_user()
        update_data = {
            "full_name": "Jane Doe",
            "bio": "Hello world",
            "subjects": ["English"],
            "grade_levels": ["Grade 3"],
        }

        service._apply_user_fields(user, update_data)

        assert user.full_name == "Jane Doe"
        assert user.bio == "Hello world"
        assert user.subjects == json.dumps(["English"])
        assert user.grade_levels == json.dumps(["Grade 3"])

    def test_empty_update_data_no_op(self):
        """Empty dict leaves user attributes unchanged."""
        service = self._make_service()
        user = self._make_user()
        original_name = user.full_name

        service._apply_user_fields(user, {})

        assert user.full_name == original_name

    # --- Integration: update_user delegates to _apply_user_fields ---

    @pytest.mark.database
    def test_update_user_persists_json_fields(self, test_db, sample_user):
        """update_user round-trips subjects/grade_levels through JSON correctly."""
        from apps.backend.schemas.users import UserUpdate

        service = UserService(test_db)
        payload = UserUpdate(subjects=["Physics"], grade_levels=["Grade 5"])

        result = service.update_user(
            user_id=sample_user.user_id,
            user_data=payload,
            current_user=sample_user,
        )

        assert result.subjects == ["Physics"]
        assert result.grade_levels == ["Grade 5"]

    # --- Integration: update_user_profile delegates to _apply_user_fields ---

    @pytest.mark.database
    def test_update_user_profile_persists_json_fields(self, test_db, sample_user):
        """update_user_profile round-trips subjects/grade_levels through JSON correctly."""
        from apps.backend.schemas.users import UserUpdate

        service = UserService(test_db)
        payload = UserUpdate(subjects=["History"], grade_levels=["Grade 4"])

        result = service.update_user_profile(
            user_id=sample_user.user_id,
            profile_data=payload,
            current_user=sample_user,
        )

        assert result.subjects == ["History"]
        assert result.grade_levels == ["Grade 4"]
