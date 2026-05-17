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


class TestApplyUserFieldsNoCopy(TestApplyUserFields):
    """
    Additional tests for AWD-M-168: _apply_user_fields must not mutate the
    caller's dict.  The callers always pass a fresh model_dump() result, but
    silent in-place mutation would be a fragility hazard for future callers.
    """

    def test_caller_dict_not_mutated_subjects(self):
        """Caller's dict is unchanged after _apply_user_fields serialises subjects."""
        service = self._make_service()
        user = self._make_user()
        original_subjects = ["Math", "Science"]
        update_data = {"subjects": original_subjects}
        original_list = list(original_subjects)  # snapshot before call

        service._apply_user_fields(user, update_data)

        # The caller's dict must still hold the original list, not a JSON string
        assert update_data["subjects"] == original_list

    def test_caller_dict_not_mutated_grade_levels(self):
        """Caller's dict is unchanged after _apply_user_fields serialises grade_levels."""
        service = self._make_service()
        user = self._make_user()
        original_grades = ["Grade 1", "Grade 2"]
        update_data = {"grade_levels": original_grades}
        original_list = list(original_grades)

        service._apply_user_fields(user, update_data)

        assert update_data["grade_levels"] == original_list

    def test_caller_dict_not_mutated_when_both_fields_present(self):
        """Caller's dict is unchanged for both JSON fields simultaneously."""
        service = self._make_service()
        user = self._make_user()
        update_data = {
            "subjects": ["English"],
            "grade_levels": ["Grade 3"],
            "full_name": "Test User",
        }
        original_subjects = list(update_data["subjects"])
        original_grades = list(update_data["grade_levels"])
        original_name = update_data["full_name"]

        service._apply_user_fields(user, update_data)

        assert update_data["subjects"] == original_subjects
        assert update_data["grade_levels"] == original_grades
        assert update_data["full_name"] == original_name


class TestParseJsonList:
    """
    Unit tests for UserService._parse_json_list (AWD-M-169).

    These tests exercise the extracted private helper that both
    _create_user_response and _create_user_profile_response delegate to.
    """

    def _make_service(self) -> UserService:
        return UserService(db=MagicMock())

    def test_valid_json_list_returned(self):
        """A valid JSON array string is decoded to a Python list."""
        service = self._make_service()
        result = service._parse_json_list('["Math", "Science"]')
        assert result == ["Math", "Science"]

    def test_none_returns_none(self):
        """None input returns None (no error)."""
        service = self._make_service()
        assert service._parse_json_list(None) is None

    def test_empty_string_returns_none(self):
        """Empty string is treated as falsy — returns None."""
        service = self._make_service()
        assert service._parse_json_list("") is None

    def test_invalid_json_returns_none(self):
        """Malformed JSON string returns None rather than raising."""
        service = self._make_service()
        assert service._parse_json_list("not-json") is None

    def test_non_string_type_returns_none(self):
        """Non-string, non-None input (e.g. int) returns None gracefully."""
        service = self._make_service()
        assert service._parse_json_list(42) is None  # type: ignore[arg-type]

    def test_empty_array_returns_empty_list(self):
        """A JSON empty array string '[]' is decoded to an empty Python list."""
        service = self._make_service()
        result = service._parse_json_list("[]")
        assert result == []


class TestFmtDatetime:
    """AWD-M-174: tests for the extracted _fmt_datetime static helper."""

    def test_none_returns_none(self):
        """None input must return None (no crash)."""
        assert UserService._fmt_datetime(None) is None

    def test_naive_datetime_gets_utc_marker(self):
        """A tz-naive datetime must be tagged as UTC in the output string."""
        from datetime import datetime
        dt = datetime(2026, 5, 17, 10, 0, 0)  # no tzinfo
        result = UserService._fmt_datetime(dt)
        assert result is not None
        assert "+00:00" in result or "Z" in result or "UTC" in result

    def test_aware_datetime_preserved(self):
        """A tz-aware datetime must not have its timezone overwritten."""
        from datetime import datetime, timezone, timedelta
        tz_plus2 = timezone(timedelta(hours=2))
        dt = datetime(2026, 5, 17, 12, 0, 0, tzinfo=tz_plus2)
        result = UserService._fmt_datetime(dt)
        assert result is not None
        # The offset must reflect +02:00, not +00:00
        assert "+02:00" in result

    def test_returns_iso8601_string(self):
        """Output must be a valid ISO-8601 string parseable by fromisoformat."""
        from datetime import datetime, timezone
        dt = datetime(2026, 1, 15, 8, 30, 0, tzinfo=timezone.utc)
        result = UserService._fmt_datetime(dt)
        assert result == "2026-01-15T08:30:00+00:00"


class TestSerializeGuide:
    """AWD-M-174: tests for the extracted _serialize_guide static helper."""

    def _make_guide(self, **kwargs):
        """Return a Mock ParentGuide with sensible defaults."""
        from datetime import datetime, timezone
        g = Mock()
        g.guide_id = kwargs.get("guide_id", 1)
        g.topic_id = kwargs.get("topic_id", 10)
        g.topic = kwargs.get("topic", None)
        g.ai_generated_content = kwargs.get("ai_generated_content", '{"steps":[]}')
        g.user_edited_content = kwargs.get("user_edited_content", None)
        g.is_bookmarked = kwargs.get("is_bookmarked", False)
        g.created_at = kwargs.get("created_at", datetime(2026, 5, 1, tzinfo=timezone.utc))
        g.updated_at = kwargs.get("updated_at", datetime(2026, 5, 2, tzinfo=timezone.utc))
        return g

    def _fmt(self, dt):
        return UserService._fmt_datetime(dt)

    def test_fields_mapped_correctly(self):
        """All expected fields must be present with correct values."""
        topic = Mock()
        topic.topic_title = "Algebra"
        guide = self._make_guide(guide_id=5, topic_id=20, topic=topic, is_bookmarked=True)

        result = UserService._serialize_guide(guide, self._fmt)

        assert result["guide_id"] == 5
        assert result["topic_id"] == 20
        assert result["topic_title"] == "Algebra"
        assert result["is_bookmarked"] is True
        assert result["ai_generated_content"] == '{"steps":[]}'

    def test_topic_none_yields_none_title(self):
        """When guide.topic is None the topic_title key must be None."""
        guide = self._make_guide(topic=None)
        result = UserService._serialize_guide(guide, self._fmt)
        assert result["topic_title"] is None

    def test_is_bookmarked_coerced_to_bool(self):
        """is_bookmarked must be a Python bool even if the model returns a truthy int."""
        guide = self._make_guide(is_bookmarked=1)
        result = UserService._serialize_guide(guide, self._fmt)
        assert result["is_bookmarked"] is True
        assert isinstance(result["is_bookmarked"], bool)

    def test_fmt_fn_called_for_timestamps(self):
        """The supplied fmt_fn must be called for created_at and updated_at."""
        from datetime import datetime, timezone
        calls = []

        def tracking_fmt(dt):
            calls.append(dt)
            return UserService._fmt_datetime(dt)

        guide = self._make_guide(
            created_at=datetime(2026, 3, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        )
        UserService._serialize_guide(guide, tracking_fmt)
        assert len(calls) == 2


class TestSerializeChild:
    """AWD-M-174: tests for the extracted _serialize_child static helper."""

    def _make_child(self, subjects_json=None, guides=None, **kwargs):
        """Return a Mock ChildProfile with sensible defaults."""
        from datetime import datetime, timezone
        c = Mock()
        c.child_id = kwargs.get("child_id", 1)
        c.name = kwargs.get("name", "Test Child")
        c.age = kwargs.get("age", 8)
        c.school_name = kwargs.get("school_name", None)
        c.country_id = kwargs.get("country_id", None)
        c.curricula_id = kwargs.get("curricula_id", None)
        c.grade_level_id = kwargs.get("grade_level_id", None)
        c.subjects = subjects_json
        c.created_at = kwargs.get("created_at", datetime(2026, 5, 1, tzinfo=timezone.utc))
        c.updated_at = kwargs.get("updated_at", datetime(2026, 5, 2, tzinfo=timezone.utc))
        c.parent_guides = guides if guides is not None else []
        return c

    def _make_guide(self, guide_id, topic_title=None):
        from datetime import datetime, timezone
        g = Mock()
        g.guide_id = guide_id
        g.topic_id = guide_id * 10
        g.topic = Mock()
        g.topic.topic_title = topic_title or f"Topic {guide_id}"
        g.ai_generated_content = "{}"
        g.user_edited_content = None
        g.is_bookmarked = False
        g.created_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
        g.updated_at = datetime(2026, 5, 2, tzinfo=timezone.utc)
        return g

    def _fmt(self, dt):
        return UserService._fmt_datetime(dt)

    def test_fields_mapped_correctly(self):
        """Core child fields must be present and correctly mapped."""
        child = self._make_child(child_id=7, name="Alice", age=9)
        result = UserService._serialize_child(child, self._fmt)

        assert result["child_id"] == 7
        assert result["name"] == "Alice"
        assert result["age"] == 9
        assert "guides" in result

    def test_subjects_json_decoded(self):
        """subjects stored as a JSON string must be deserialised in the output."""
        child = self._make_child(subjects_json='["Maths", "English"]')
        result = UserService._serialize_child(child, self._fmt)
        assert result["subjects"] == ["Maths", "English"]

    def test_subjects_none_stays_none(self):
        """subjects=None must produce null in the output, not an error."""
        child = self._make_child(subjects_json=None)
        result = UserService._serialize_child(child, self._fmt)
        assert result["subjects"] is None

    def test_guides_ordered_by_guide_id(self):
        """guides must appear sorted by guide_id ascending."""
        g1 = self._make_guide(guide_id=3)
        g2 = self._make_guide(guide_id=1)
        g3 = self._make_guide(guide_id=2)
        child = self._make_child(guides=[g1, g2, g3])
        result = UserService._serialize_child(child, self._fmt)
        guide_ids = [g["guide_id"] for g in result["guides"]]
        assert guide_ids == [1, 2, 3]

    def test_no_guides_returns_empty_list(self):
        """A child with no guides must produce an empty 'guides' list."""
        child = self._make_child(guides=[])
        result = UserService._serialize_child(child, self._fmt)
        assert result["guides"] == []
