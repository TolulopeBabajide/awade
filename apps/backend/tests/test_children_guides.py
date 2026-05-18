"""
Guide happy-path, idempotency, and AI-error tests for the children router.

Split from test_children_router.py (AWD-M-116).

Covers:
- Happy path: list guides, get guide
- Guide idempotency: second generate call for same child+topic returns
  existing guide without re-calling AI (router layer)
- Malformed AI JSON → 502
- Missing required AI fields → 502
"""

import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.models import ChildProfile, ParentGuide
from children_factories import (
    _make_parent,
    _make_child_profile,
    _make_guide,
    _client_as,
)


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
# Guide happy path
# ---------------------------------------------------------------------------

class TestGuideHappyPath:
    """Smoke tests for guide list + get endpoints."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _build_db_for_guide_list(self, child: ChildProfile, guides):
        mock_db = MagicMock()
        call_count = [0]

        def query_side(model):
            call_count[0] += 1
            q = MagicMock()
            if model is ChildProfile:
                q.options.return_value.filter.return_value.first.return_value = child
                q.filter.return_value.first.return_value = child
            elif model is ParentGuide:
                q.options.return_value.filter.return_value.filter.return_value.order_by.return_value.all.return_value = guides
                q.options.return_value.filter.return_value.order_by.return_value.all.return_value = guides
            else:
                q.options.return_value.filter.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def test_list_guides_returns_200(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=5, parent_id=1)
        guide = _make_guide(guide_id=11, child_id=5)
        mock_db = self._build_db_for_guide_list(child, [guide])
        app.dependency_overrides[get_db] = lambda: mock_db
        c = _client_as(parent)
        resp = c.get("/api/children/5/guides")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["guides"][0]["guide_id"] == 11


# ---------------------------------------------------------------------------
# Generate guide — idempotency at router layer
# ---------------------------------------------------------------------------

class TestGenerateGuideIdempotency:
    """
    When a guide already exists for child+topic, the endpoint returns it
    without making an AI call.  Tested at the router level by mocking the
    DB to return an existing guide on the first ParentGuide query.
    """

    def teardown_method(self):
        app.dependency_overrides.clear()

    def test_existing_guide_returned_no_ai_call(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=5, parent_id=1)
        existing_guide = _make_guide(guide_id=20, child_id=5, topic_id=7)

        call_count = [0]
        mock_db = MagicMock()

        def query_side(model):
            call_count[0] += 1
            q = MagicMock()
            if model is ChildProfile:
                q.options.return_value.filter.return_value.first.return_value = child
                q.filter.return_value.first.return_value = child
            elif model is ParentGuide:
                q.options.return_value.filter.return_value.first.return_value = existing_guide
                q.filter.return_value.first.return_value = existing_guide
            else:
                q.options.return_value.filter.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = query_side
        app.dependency_overrides[get_db] = lambda: mock_db

        c = _client_as(parent)
        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
            resp = c.post("/api/children/5/guides/generate?topic_id=7")
            MockAI.assert_not_called()

        assert resp.status_code == 200
        assert resp.json()["guide_id"] == 20


# ---------------------------------------------------------------------------
# Generate guide — malformed AI JSON → 502
# ---------------------------------------------------------------------------

class TestGenerateGuideMalformedAI:
    """When AI returns bad JSON the endpoint must respond 502, not 500."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _build_db_no_existing_guide(self, child: ChildProfile):
        """Mock DB: no existing guide, topic exists with full relationships."""
        mock_topic = MagicMock()
        mock_topic.topic_id = 1
        mock_topic.topic_title = "Fractions"
        cs = MagicMock()
        cs.subject.name = "Mathematics"
        cs.grade_level.name = "Grade 5"
        cs.curriculum.curricula_title = "Nigerian Curriculum"
        mock_topic.curriculum_structure = cs
        mock_topic.learning_objectives = []
        mock_topic.topic_contents = []

        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            if model is ChildProfile:
                q.options.return_value.filter.return_value.first.return_value = child
                q.filter.return_value.first.return_value = child
            elif model is ParentGuide:
                q.options.return_value.filter.return_value.first.return_value = None
                q.filter.return_value.first.return_value = None
            else:
                q.options.return_value.filter.return_value.first.return_value = mock_topic
            return q

        mock_db.query.side_effect = query_side
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock()
        return mock_db

    def test_malformed_ai_json_returns_502(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=5, parent_id=1)
        child.country = MagicMock()
        child.country.country_name = "Nigeria"
        child.curricula_id = 1
        child.grade_level_id = 1
        mock_db = self._build_db_no_existing_guide(child)
        app.dependency_overrides[get_db] = lambda: mock_db

        c = _client_as(parent)
        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = ("not valid json {{{", True)
            resp = c.post("/api/children/5/guides/generate?topic_id=1")

        assert resp.status_code == 502

    def test_missing_required_ai_fields_returns_502(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=5, parent_id=1)
        child.country = MagicMock()
        child.country.country_name = "Nigeria"
        child.curricula_id = 1
        child.grade_level_id = 1
        mock_db = self._build_db_no_existing_guide(child)
        app.dependency_overrides[get_db] = lambda: mock_db

        bad_content = json.dumps({
            "topic_header": {
                "topic": "Fractions", "subject": "Math",
                "grade_level": "5", "country": "Nigeria", "curriculum": "NC"
            },
            "simple_explanation": {
                "what_it_is": "A part of a whole",
                "why_it_matters": "Used daily"
            },
            "conversation_starters": ["How many?"],
            "common_mistakes": [{
                "mistake": "Wrong denominator",
                "why_it_happens": "Big number bias",
                "how_to_help": "Use visuals"
            }],
            # 'home_activity' is absent — schema validation must reject this
        })

        c = _client_as(parent)
        with patch("apps.backend.services.children_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = (bad_content, False)
            resp = c.post("/api/children/5/guides/generate?topic_id=1")

        assert resp.status_code == 502
