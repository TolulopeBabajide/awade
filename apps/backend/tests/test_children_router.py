"""
Tests for AWD-H-11: children router auth gating, ownership enforcement,
and guide idempotency.

Covers:
- Unauthenticated requests → 401 on every children endpoint
- EDUCATOR role → 403 on every children endpoint (parent-only)
- Ownership: parent A cannot access parent B's child → 404
- Happy path: create, list, get, update, delete child profile
- Happy path: list guides, get guide
- Guide idempotency: second generate call for same child+topic returns
  existing guide without re-calling AI (covered at router layer)
- Malformed AI JSON → 502 (router layer — delegates to service)
"""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_active_user
from apps.backend.models import User, UserRole, ChildProfile, ParentGuide

# ---------------------------------------------------------------------------
# Helpers / factories
# ---------------------------------------------------------------------------

def _make_user(user_id: int, role: UserRole, email: str = None) -> User:
    u = User()
    u.user_id = user_id
    u.email = email or f"user{user_id}@example.com"
    u.role = role
    u.is_suspended = False
    return u


def _make_parent(user_id: int = 1, email: str = "parent@example.com") -> User:
    return _make_user(user_id, UserRole.PARENT, email)


def _make_educator(user_id: int = 10, email: str = "educator@example.com") -> User:
    return _make_user(user_id, UserRole.EDUCATOR, email)


def _auth_override(user: User):
    """Return a dependency function that injects the given user."""
    def _dep():
        return user
    return _dep


def _now():
    return datetime.now(timezone.utc)


def _make_child_profile(child_id: int, parent_id: int) -> ChildProfile:
    c = ChildProfile()
    c.child_id = child_id
    c.parent_id = parent_id
    c.name = f"Child {child_id}"
    c.age = 8
    c.school_name = None
    c.country_id = None
    c.curricula_id = None
    c.grade_level_id = None
    c.subjects = None
    c.created_at = _now()
    c.updated_at = _now()
    # Lazy relationships — set to None so _to_response handles gracefully
    c.country = None
    c.curriculum = None
    c.grade_level = None
    return c


def _make_guide(guide_id: int, child_id: int, topic_id: int = 1) -> ParentGuide:
    g = ParentGuide()
    g.guide_id = guide_id
    g.child_id = child_id
    g.topic_id = topic_id
    g.ai_generated_content = None
    g.user_edited_content = None
    g.is_bookmarked = False
    g.created_at = _now()
    g.updated_at = _now()
    mock_topic = MagicMock()
    mock_topic.topic_title = "Fractions"
    mock_topic.curriculum_structure = None
    g.topic = mock_topic
    return g


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


def _client_as(user: User) -> TestClient:
    """Return a TestClient with the given user injected as the current user."""
    app.dependency_overrides[get_current_active_user] = _auth_override(user)
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# 401 — unauthenticated requests
# ---------------------------------------------------------------------------

CHILDREN_ENDPOINTS = [
    ("POST",   "/api/children",         {"name": "Alice"}),
    ("GET",    "/api/children",         None),
    ("GET",    "/api/children/1",       None),
    ("PUT",    "/api/children/1",       {"name": "Alice"}),
    ("DELETE", "/api/children/1",       None),
    ("GET",    "/api/children/1/topics", None),
    ("GET",    "/api/children/1/guides", None),
    ("POST",   "/api/children/1/guides/generate?topic_id=1", None),
    ("GET",    "/api/guides/1",         None),
    ("POST",   "/api/guides/1/bookmark", None),
]


class TestUnauthenticated:
    """Every children endpoint must return 401 when no token is provided.

    AWD-H-25 changed HTTPBearer to auto_error=False; get_current_user now
    manually raises HTTP 401 when no token is present (header or cookie absent).
    The dependency chain is:
    HTTPBearer(auto_error=False) → get_current_user → raises 401.
    """

    @pytest.mark.parametrize("method,path,body", CHILDREN_ENDPOINTS)
    def test_returns_401(self, client, method, path, body):
        resp = client.request(method, path, json=body)
        assert resp.status_code == 401, (
            f"{method} {path} returned {resp.status_code}, expected 401 (no auth)"
        )


# ---------------------------------------------------------------------------
# 403 — EDUCATOR role is forbidden from children endpoints
# ---------------------------------------------------------------------------

class TestEducatorForbidden:
    """EDUCATOR accounts must receive 403 on all children/guides endpoints."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    @pytest.mark.parametrize("method,path,body", CHILDREN_ENDPOINTS)
    def test_educator_receives_403(self, method, path, body):
        educator = _make_educator()
        c = _client_as(educator)
        resp = c.request(method, path, json=body)
        assert resp.status_code == 403, (
            f"EDUCATOR on {method} {path} returned {resp.status_code}, expected 403"
        )


# ---------------------------------------------------------------------------
# Ownership enforcement — parent A cannot access parent B's child
# ---------------------------------------------------------------------------

class TestOwnershipEnforcement:
    """
    parent_a (user_id=1) must get 404 when requesting a child that belongs
    to parent_b (user_id=2).  The 404 masks existence rather than leaking 403.
    """

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _mock_db_child_belongs_to(self, owner_id: int):
        """
        Return a mock DB where child_id=99 belongs to owner_id, not to
        the requesting parent.
        """
        child = _make_child_profile(child_id=99, parent_id=owner_id)

        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            if model is ChildProfile:
                # Simulate chained: .options(...).filter(...).first()
                filtered = MagicMock()
                filtered.first.return_value = None  # wrong owner → not found
                q.options.return_value.filter.return_value = filtered
                q.filter.return_value.first.return_value = None
            else:
                q.options.return_value.filter.return_value.first.return_value = None
                q.filter.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def _set_db(self, mock_db):
        app.dependency_overrides[get_db] = lambda: mock_db

    def test_get_child_returns_404_for_wrong_parent(self):
        parent_a = _make_parent(user_id=1)
        mock_db = self._mock_db_child_belongs_to(owner_id=2)
        self._set_db(mock_db)
        c = _client_as(parent_a)
        resp = c.get("/api/children/99")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_update_child_returns_404_for_wrong_parent(self):
        parent_a = _make_parent(user_id=1)
        mock_db = self._mock_db_child_belongs_to(owner_id=2)
        self._set_db(mock_db)
        c = _client_as(parent_a)
        resp = c.put("/api/children/99", json={"name": "Hijacked"})
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_delete_child_returns_404_for_wrong_parent(self):
        parent_a = _make_parent(user_id=1)
        mock_db = self._mock_db_child_belongs_to(owner_id=2)
        self._set_db(mock_db)
        c = _client_as(parent_a)
        resp = c.delete("/api/children/99")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_get_topics_returns_404_for_wrong_parent(self):
        parent_a = _make_parent(user_id=1)
        mock_db = self._mock_db_child_belongs_to(owner_id=2)
        self._set_db(mock_db)
        c = _client_as(parent_a)
        resp = c.get("/api/children/99/topics")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_list_guides_returns_404_for_wrong_parent(self):
        parent_a = _make_parent(user_id=1)
        mock_db = self._mock_db_child_belongs_to(owner_id=2)
        self._set_db(mock_db)
        c = _client_as(parent_a)
        resp = c.get("/api/children/99/guides")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"

    def test_generate_guide_returns_404_for_wrong_parent(self):
        parent_a = _make_parent(user_id=1)
        mock_db = self._mock_db_child_belongs_to(owner_id=2)
        self._set_db(mock_db)
        c = _client_as(parent_a)
        resp = c.post("/api/children/99/guides/generate?topic_id=1")
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"


# ---------------------------------------------------------------------------
# Happy path — CRUD via dependency-overridden DB
# ---------------------------------------------------------------------------

class TestChildCRUDHappyPath:
    """Smoke tests for the full CRUD lifecycle via mocked DB."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _build_db_for_create(self, child: ChildProfile):
        """Mock DB that handles create_child: FK checks + add/commit/refresh."""
        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            # FK validation queries return truthy objects so validation passes
            q.filter.return_value.first.return_value = MagicMock()
            # For the reload after commit, return the child
            q.options.return_value.filter.return_value.first.return_value = child
            return q

        mock_db.query.side_effect = query_side
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        def refresh_side(obj):
            obj.child_id = child.child_id

        mock_db.refresh.side_effect = refresh_side
        return mock_db

    def _build_db_for_list(self, children):
        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            q.options.return_value.filter.return_value.order_by.return_value.all.return_value = children
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def _build_db_for_get(self, child: ChildProfile):
        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            q.options.return_value.filter.return_value.first.return_value = child
            return q

        mock_db.query.side_effect = query_side
        return mock_db

    def test_list_children_returns_200(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=5, parent_id=1)
        mock_db = self._build_db_for_list([child])
        app.dependency_overrides[get_db] = lambda: mock_db
        c = _client_as(parent)
        resp = c.get("/api/children")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["children"][0]["child_id"] == 5

    def test_get_child_returns_200_for_owner(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=7, parent_id=1)
        mock_db = self._build_db_for_get(child)
        app.dependency_overrides[get_db] = lambda: mock_db
        c = _client_as(parent)
        resp = c.get("/api/children/7")
        assert resp.status_code == 200
        assert resp.json()["child_id"] == 7

    def test_create_child_returns_201(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=3, parent_id=1)
        mock_db = self._build_db_for_create(child)
        app.dependency_overrides[get_db] = lambda: mock_db
        c = _client_as(parent)
        resp = c.post("/api/children", json={"name": "Alice"})
        assert resp.status_code == 201
        assert resp.json()["name"] == child.name

    def test_delete_child_returns_200(self):
        parent = _make_parent(user_id=1)
        child = _make_child_profile(child_id=9, parent_id=1)
        mock_db = self._build_db_for_get(child)
        mock_db.delete = MagicMock()
        mock_db.commit = MagicMock()
        app.dependency_overrides[get_db] = lambda: mock_db
        c = _client_as(parent)
        resp = c.delete("/api/children/9")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Child profile deleted successfully"


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
                # Return existing guide — service should short-circuit
                # Service uses a single .filter(cond1, cond2) call, not two chained filters
                q.options.return_value.filter.return_value.first.return_value = existing_guide
                q.filter.return_value.first.return_value = existing_guide
            else:
                q.options.return_value.filter.return_value.first.return_value = None
            return q

        mock_db.query.side_effect = query_side
        app.dependency_overrides[get_db] = lambda: mock_db

        c = _client_as(parent)
        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
            resp = c.post("/api/children/5/guides/generate?topic_id=7")
            # AI constructor must never be called
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

        call_count = [0]
        mock_db = MagicMock()

        def query_side(model):
            call_count[0] += 1
            q = MagicMock()
            if model is ChildProfile:
                q.options.return_value.filter.return_value.first.return_value = child
                q.filter.return_value.first.return_value = child
            elif model is ParentGuide:
                # First call: existence check → None; subsequent calls: n/a
                # Service uses a single .filter(cond1, cond2) call, not two chained filters
                q.options.return_value.filter.return_value.first.return_value = None
                q.filter.return_value.first.return_value = None
            else:
                # Topic query
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
        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
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

        # Valid JSON but missing required top-level 'home_activity' field
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
        with patch("packages.ai.gpt_service.AwadeGPTService") as MockAI:
            instance = MockAI.return_value
            instance.generate_parent_guide.return_value = (bad_content, False)
            resp = c.post("/api/children/5/guides/generate?topic_id=1")

        assert resp.status_code == 502


# ---------------------------------------------------------------------------
# AWD-M-21: GET /api/guides/{guide_id}/export  — PDF export
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
