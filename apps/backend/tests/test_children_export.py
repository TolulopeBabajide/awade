"""
PDF export tests for the children router (GET /api/guides/{id}/export).

Split from test_children_router.py (AWD-M-116).

Covers AWD-M-21:
- 401 when unauthenticated
- 404 when guide is absent / not owned
- 422 when guide has no AI content
- 422 when guide has malformed AI content
- 503 when WeasyPrint is unavailable
- 200 application/pdf happy path
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from children_factories import (
    _make_parent,
    _make_guide,
    _client_as,
)


# ---------------------------------------------------------------------------
# Shared guide content fixture (valid JSON that passes schema validation)
# ---------------------------------------------------------------------------

_VALID_GUIDE_CONTENT = json.dumps({
    "topic_header": {
        "topic": "Fractions",
        "subject": "Mathematics",
        "grade_level": "Grade 5",
        "country": "Nigeria",
        "curriculum": "Nigerian National Curriculum",
    },
    "simple_explanation": {
        "what_it_is": "A fraction represents a part of a whole.",
        "why_it_matters": "Fractions appear in everyday life.",
    },
    "home_activity": {
        "title": "Pizza Fractions",
        "description": "Use a pizza or paper circle to explore fractions.",
        "materials_needed": ["paper", "scissors"],
        "steps": ["Fold the paper in half.", "Label each half 1/2."],
        "what_to_look_for": "Child identifies numerator and denominator.",
    },
    "conversation_starters": [
        "If we share this apple equally, what fraction does each person get?"
    ],
    "common_mistakes": [
        {
            "mistake": "Adding denominators when adding fractions",
            "why_it_happens": "Treats numerator and denominator independently.",
            "how_to_help": "Use visual aids to show why denominators stay the same.",
        }
    ],
    "curriculum_context": {
        "what_came_before": "Whole numbers",
        "what_comes_next": "Decimals",
        "how_long_in_school": "3 weeks",
    },
    "encouragement_tips": ["Praise effort, not just correct answers."],
})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("ENVIRONMENT", "testing")


@pytest.fixture()
def client():
    """Plain client — no auth override."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# PDF export tests
# ---------------------------------------------------------------------------

class TestExportGuidePdf:
    """AWD-M-21: PDF export endpoint."""

    def _guide_db(self, guide):
        """Build a minimal mock DB that returns the guide for ownership query."""
        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = guide
        q.filter.return_value.first.return_value = guide
        mock_db.query.return_value = q
        return mock_db

    def test_unauthenticated_returns_401(self):
        c = TestClient(app, raise_server_exceptions=False)
        resp = c.get("/api/guides/1/export")
        assert resp.status_code == 401

    def test_guide_not_found_returns_404(self):
        """Ownership check via ChildrenService → 404 when guide is absent."""
        parent = _make_parent(user_id=1)
        mock_db = MagicMock()
        q = MagicMock()
        q.options.return_value.join.return_value.filter.return_value.first.return_value = None
        q.filter.return_value.first.return_value = None
        mock_db.query.return_value = q
        app.dependency_overrides[get_db] = lambda: mock_db

        c = _client_as(parent)
        resp = c.get("/api/guides/99/export")

        assert resp.status_code == 404
        app.dependency_overrides.clear()

    def test_guide_with_no_content_returns_422(self):
        parent = _make_parent(user_id=1)
        guide = _make_guide(guide_id=7, child_id=2)
        guide.ai_generated_content = None
        mock_topic = MagicMock()
        mock_topic.topic_title = "Fractions"
        mock_topic.curriculum_structure = None
        guide.topic = mock_topic
        app.dependency_overrides[get_db] = lambda: self._guide_db(guide)

        c = _client_as(parent)
        resp = c.get("/api/guides/7/export")

        assert resp.status_code == 422
        app.dependency_overrides.clear()

    def test_guide_with_malformed_content_returns_422(self):
        parent = _make_parent(user_id=1)
        guide = _make_guide(guide_id=8, child_id=2)
        guide.ai_generated_content = "not valid json {{{"
        mock_topic = MagicMock()
        mock_topic.topic_title = "Fractions"
        mock_topic.curriculum_structure = None
        guide.topic = mock_topic
        app.dependency_overrides[get_db] = lambda: self._guide_db(guide)

        c = _client_as(parent)
        resp = c.get("/api/guides/8/export")

        assert resp.status_code == 422
        app.dependency_overrides.clear()

    def test_weasyprint_unavailable_returns_503(self):
        parent = _make_parent(user_id=1)
        guide = _make_guide(guide_id=9, child_id=2)
        guide.ai_generated_content = _VALID_GUIDE_CONTENT
        mock_topic = MagicMock()
        mock_topic.topic_title = "Fractions"
        mock_topic.curriculum_structure = None
        guide.topic = mock_topic
        app.dependency_overrides[get_db] = lambda: self._guide_db(guide)

        c = _client_as(parent)
        with patch(
            "apps.backend.services.pdf_service.WEASYPRINT_AVAILABLE", False
        ):
            resp = c.get("/api/guides/9/export")

        assert resp.status_code == 503
        app.dependency_overrides.clear()

    def test_happy_path_returns_pdf(self):
        """With WeasyPrint mocked, endpoint returns 200 application/pdf."""
        parent = _make_parent(user_id=1)
        guide = _make_guide(guide_id=10, child_id=2)
        guide.ai_generated_content = _VALID_GUIDE_CONTENT
        mock_topic = MagicMock()
        mock_topic.topic_title = "Fractions"
        mock_topic.curriculum_structure = None
        guide.topic = mock_topic
        app.dependency_overrides[get_db] = lambda: self._guide_db(guide)

        fake_pdf = b"%PDF-1.4 fake"
        c = _client_as(parent)
        with patch(
            "apps.backend.services.pdf_service.PDFService.generate_guide_pdf",
            return_value=fake_pdf,
        ):
            resp = c.get("/api/guides/10/export")

        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        assert "attachment" in resp.headers.get("content-disposition", "")
        assert resp.content == fake_pdf
        app.dependency_overrides.clear()
