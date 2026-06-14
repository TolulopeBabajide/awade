"""
AWD-H-110 regression: _generate_html_content must accept db: Session explicitly
rather than mining it from ORM internals (_sa_instance_state.session).
"""
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime

import pytest

from apps.backend.services.pdf_service import PDFService


class TestGenerateHtmlContentDbParam:
    """_generate_html_content receives db via parameter, not via ORM private attribute."""

    def _make_lesson_resource(self):
        lr = MagicMock()
        lr.lesson_plan_id = 1
        lr.lesson_resources_id = 42
        lr.ai_generated_content = "AI content"
        lr.user_edited_content = None
        lr.context_input = None
        lr.status = "draft"
        lr.created_at = datetime(2026, 6, 14)
        return lr

    def _make_topic(self):
        topic = MagicMock()
        topic.topic_id = 10
        topic.topic_title = "Fractions"
        topic.learning_objectives = []
        topic.topic_contents = []
        return topic

    def _make_db(self):
        return MagicMock()

    def test_generate_html_content_accepts_db_param(self):
        """_generate_html_content must accept a db: Session keyword argument."""
        service = PDFService()
        lr = self._make_lesson_resource()
        topic = self._make_topic()
        subject = MagicMock(name="Math")
        grade_level = MagicMock(name="JSS1")
        curriculum = MagicMock(curricula_title="NERDC")
        db = self._make_db()

        with patch.object(service, "format_curriculum_alignment", return_value="alignment") as mock_align:
            html = service._generate_html_content(
                lesson_resource=lr,
                topic=topic,
                subject=subject,
                grade_level=grade_level,
                curriculum=curriculum,
                db=db,
            )

        # db must be forwarded to format_curriculum_alignment, never via ORM internals
        mock_align.assert_called_once_with(topic, db)
        assert "Fractions" in html

    def test_generate_html_content_does_not_access_sa_instance_state(self):
        """Calling _generate_html_content must not touch _sa_instance_state on lesson_resource."""
        service = PDFService()
        lr = self._make_lesson_resource()
        topic = self._make_topic()
        db = self._make_db()

        # If the code ever accesses _sa_instance_state, MagicMock records the call.
        # We assert it was NOT called after _generate_html_content runs.
        with patch.object(service, "format_curriculum_alignment", return_value=""):
            service._generate_html_content(
                lesson_resource=lr,
                topic=topic,
                subject=MagicMock(),
                grade_level=MagicMock(),
                curriculum=MagicMock(),
                db=db,
            )

        # lesson_resource._sa_instance_state should never have been accessed
        sa_state_calls = [
            call for call in lr.mock_calls
            if "_sa_instance_state" in str(call)
        ]
        assert sa_state_calls == [], (
            f"_sa_instance_state was accessed: {sa_state_calls}"
        )

    def test_generate_lesson_resource_pdf_passes_db_to_html_content(self):
        """generate_lesson_resource_pdf must forward db to _generate_html_content."""
        service = PDFService()

        lr = self._make_lesson_resource()
        db = self._make_db()

        # Stub out all DB queries
        mock_lesson_plan = MagicMock(topic_id=10)
        mock_topic = self._make_topic()
        mock_subject = MagicMock(name="Math")
        mock_grade_level = MagicMock(name="JSS1")
        mock_curriculum = MagicMock(curricula_title="NERDC")

        db.query.return_value.filter.return_value.first.side_effect = [
            mock_lesson_plan,
            mock_topic,
            MagicMock(subject_id=1, grade_level_id=1, curricula_id=1),  # curriculum_structure
            mock_subject,
            mock_grade_level,
            mock_curriculum,
        ]

        mock_HTML = MagicMock()
        mock_HTML.return_value.write_pdf.return_value = b"%PDF"
        with patch.object(service, "_generate_html_content", return_value="<html/>") as mock_html, \
             patch("apps.backend.services.pdf_service.WEASYPRINT_AVAILABLE", True), \
             patch("apps.backend.services.pdf_service.HTML", mock_HTML, create=True), \
             patch("apps.backend.services.pdf_service.CSS", MagicMock(), create=True):
            service.generate_lesson_resource_pdf(lr, db)

        # Verify _generate_html_content received the db session
        _, kwargs = mock_html.call_args
        assert kwargs.get("db") is db, (
            "_generate_html_content was not called with the db parameter"
        )
