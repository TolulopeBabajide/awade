"""
Tests for ContextService.

Split from test_services.py (AWD-M-110).
Covers: initialization, context creation, and retrieval by lesson plan.
AWD-L-47: added tests for get_contexts_for_user().

Author: Tolulope Babajide
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from services.context_service import ContextService
from schemas.contexts import ContextCreate
from apps.backend.models import User, LessonPlan, Context


class TestContextService:
    """Test context service."""

    def test_context_service_initialization(self, test_db):
        """Test ContextService initialization."""
        service = ContextService(test_db)
        assert service.db == test_db

    def test_create_context(self, test_db, sample_lesson_plan):
        """Test context creation."""
        service = ContextService(test_db)

        context_data = ContextCreate(
            lesson_plan_id=sample_lesson_plan.lesson_plan_id,
            context_text="Test context for lesson plan",
            context_type="cultural"
        )

        result = service.create_context(context_data)
        assert result is not None
        assert result.context_text == "Test context for lesson plan"

    def test_get_contexts_by_lesson_plan(self, test_db, sample_lesson_plan):
        """Test get contexts by lesson plan."""
        service = ContextService(test_db)

        # Create a context first
        context_data = ContextCreate(
            lesson_plan_id=sample_lesson_plan.lesson_plan_id,
            context_text="Test context",
            context_type="cultural"
        )
        service.create_context(context_data)

        # Get contexts
        result = service.get_contexts_by_lesson_plan(sample_lesson_plan.lesson_plan_id)
        assert result.total >= 1


@pytest.mark.database
class TestGetContextsForUser:
    """Tests for ContextService.get_contexts_for_user() (AWD-L-47)."""

    def test_get_contexts_for_user_happy_path(self, test_db, sample_lesson_plan, sample_user):
        """Happy path: returns only contexts belonging to the requesting user's lesson plans."""
        service = ContextService(test_db)

        # Create a second user with their own lesson plan and context
        other_user = User(
            full_name="Other User",
            email="other@example.com",
            password_hash="hashed_other",
            role="EDUCATOR",
            country="Nigeria",
            region="Lagos",
        )
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)

        other_lesson_plan = LessonPlan(
            topic_id=sample_lesson_plan.topic_id,
            user_id=other_user.user_id,
        )
        test_db.add(other_lesson_plan)
        test_db.commit()
        test_db.refresh(other_lesson_plan)

        # Add one context for sample_user's plan and one for other_user's plan
        ctx_user = Context(
            lesson_plan_id=sample_lesson_plan.lesson_plan_id,
            context_text="User context",
            context_type="cultural",
        )
        ctx_other = Context(
            lesson_plan_id=other_lesson_plan.lesson_plan_id,
            context_text="Other context",
            context_type="cultural",
        )
        test_db.add_all([ctx_user, ctx_other])
        test_db.commit()

        result = service.get_contexts_for_user(sample_user.user_id)

        context_texts = [r.context_text for r in result]
        assert "User context" in context_texts
        assert "Other context" not in context_texts

    def test_get_contexts_for_user_empty_when_no_lesson_plans(self, test_db):
        """Empty result: user with no lesson plans gets an empty list."""
        # Create a user that has no lesson plans at all
        lonely_user = User(
            full_name="Lonely User",
            email="lonely@example.com",
            password_hash="hashed_lonely",
            role="EDUCATOR",
            country="Nigeria",
            region="Lagos",
        )
        test_db.add(lonely_user)
        test_db.commit()
        test_db.refresh(lonely_user)

        service = ContextService(test_db)
        result = service.get_contexts_for_user(lonely_user.user_id)

        assert result == []

    def test_get_contexts_for_user_raises_500_on_db_exception(self, test_db):
        """DB exception path: query raises Exception → HTTPException 500 with logging."""
        service = ContextService(test_db)

        with patch.object(test_db, "query", side_effect=Exception("DB connection lost")):
            with pytest.raises(HTTPException) as exc_info:
                service.get_contexts_for_user(user_id=1)

        assert exc_info.value.status_code == 500
        assert "error" in exc_info.value.detail.lower()
