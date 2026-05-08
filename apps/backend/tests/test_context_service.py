"""
Tests for ContextService.

Split from test_services.py (AWD-M-110).
Covers: initialization, context creation, and retrieval by lesson plan.

Author: Tolulope Babajide
"""

from services.context_service import ContextService


class TestContextService:
    """Test context service."""

    def test_context_service_initialization(self, test_db):
        """Test ContextService initialization."""
        service = ContextService(test_db)
        assert service.db == test_db

    def test_create_context(self, test_db, sample_lesson_plan):
        """Test context creation."""
        service = ContextService(test_db)

        from schemas.contexts import ContextCreate

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
        from schemas.contexts import ContextCreate
        context_data = ContextCreate(
            lesson_plan_id=sample_lesson_plan.lesson_plan_id,
            context_text="Test context",
            context_type="cultural"
        )
        service.create_context(context_data)

        # Get contexts
        result = service.get_contexts_by_lesson_plan(sample_lesson_plan.lesson_plan_id)
        assert result.total >= 1
