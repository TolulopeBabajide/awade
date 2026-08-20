"""
AWD-H-110 regression: _generate_html_content must accept db: Session explicitly
rather than mining it from ORM internals (_sa_instance_state.session).

AWD-M-232 regression: all database-sourced values interpolated into the HTML
must be escaped via _h() to prevent HTML injection from field values like
"Science & Technology" (ampersand) or attacker-controlled topic titles.
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
        subject = MagicMock()
        subject.name = "Math"
        grade_level = MagicMock()
        grade_level.name = "JSS1"
        curriculum = MagicMock(curriculum_title="NERDC")
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
        assert "Math" in html
        assert "JSS1" in html

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
        mock_subject = MagicMock()
        mock_subject.name = "Math"
        mock_grade_level = MagicMock()
        mock_grade_level.name = "JSS1"
        mock_curriculum = MagicMock(curriculum_title="NERDC")

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


class TestGenerateHtmlContentEscaping:
    """AWD-M-232: _generate_html_content must HTML-escape all database-sourced values."""

    def _make_lesson_resource(self, **overrides):
        lr = MagicMock()
        lr.lesson_plan_id = 1
        lr.lesson_resources_id = 99
        lr.ai_generated_content = "AI content"
        lr.user_edited_content = None
        lr.context_input = None
        lr.status = "draft"
        lr.created_at = datetime(2026, 6, 14)
        for k, v in overrides.items():
            setattr(lr, k, v)
        return lr

    def _make_topic(self, title="Fractions"):
        topic = MagicMock()
        topic.topic_id = 10
        topic.topic_title = title
        topic.learning_objectives = []
        topic.topic_contents = []
        return topic

    def _render(self, topic_title="Fractions", subject_name="Mathematics",
                grade_name="Grade 3", curriculum_title="NERDC",
                alignment="obj1\nobj2", content="para1\npara2"):
        service = PDFService()
        lr = self._make_lesson_resource()
        topic = self._make_topic(title=topic_title)
        subject = MagicMock()
        subject.name = subject_name
        grade_level = MagicMock()
        grade_level.name = grade_name
        curriculum = MagicMock()
        curriculum.curriculum_title = curriculum_title
        db = MagicMock()
        with patch.object(service, "format_curriculum_alignment", return_value=alignment), \
             patch.object(service, "include_ai_and_user_content", return_value=content):
            return service._generate_html_content(
                lesson_resource=lr,
                topic=topic,
                subject=subject,
                grade_level=grade_level,
                curriculum=curriculum,
                db=db,
            )

    def test_ampersand_in_topic_title_is_escaped(self):
        html = self._render(topic_title="Science & Technology")
        assert "Science & Technology" not in html
        assert "Science &amp; Technology" in html

    def test_ampersand_in_subject_name_is_escaped(self):
        html = self._render(subject_name="Arts & Crafts")
        assert "Arts & Crafts" not in html
        assert "Arts &amp; Crafts" in html

    def test_ampersand_in_curriculum_title_is_escaped(self):
        html = self._render(curriculum_title="Lagos & FCT Curriculum")
        assert "Lagos & FCT Curriculum" not in html
        assert "Lagos &amp; FCT Curriculum" in html

    def test_lt_gt_in_grade_name_is_escaped(self):
        html = self._render(grade_name="<JSS1>")
        assert "<JSS1>" not in html
        assert "&lt;JSS1&gt;" in html

    def test_newlines_in_alignment_become_br_tags(self):
        html = self._render(alignment="line1\nline2")
        assert "<br>" in html
        assert "line1" in html
        assert "line2" in html

    def test_ampersand_in_alignment_is_escaped_before_br_substitution(self):
        html = self._render(alignment="Obj A & B\nObj C")
        assert "Obj A & B" not in html
        assert "Obj A &amp; B" in html
        assert "<br>" in html

    def test_newlines_in_combined_content_become_br_tags(self):
        html = self._render(content="Para 1\nPara 2")
        assert "<br>" in html
        assert "Para 1" in html
        assert "Para 2" in html

    def test_ampersand_in_combined_content_is_escaped_before_br_substitution(self):
        html = self._render(content="R & D notes\nMore text")
        assert "R & D notes" not in html
        assert "R &amp; D notes" in html
        assert "<br>" in html


class TestGetContentSourceInfoEscaping:
    """AWD-M-234: _get_content_source_info must HTML-escape the status field."""

    def test_html_chars_in_status_are_escaped(self):
        # .title() runs first ("Complete" with caps), then _h() escapes angle brackets
        service = PDFService()
        lr = MagicMock()
        lr.user_edited_content = None
        lr.ai_generated_content = None
        lr.context_input = None
        lr.status = "<script>xss</script>"
        result = service._get_content_source_info(lr)
        assert "<script>" not in result
        assert "<Script>" not in result
        assert "&lt;" in result

    def test_ampersand_in_status_is_escaped(self):
        # .title() runs first ("Draft & Pending"), then _h() escapes the ampersand
        service = PDFService()
        lr = MagicMock()
        lr.user_edited_content = None
        lr.ai_generated_content = None
        lr.context_input = None
        lr.status = "draft & pending"
        result = service._get_content_source_info(lr)
        assert "draft & pending" not in result
        assert "Draft &amp; Pending" in result
