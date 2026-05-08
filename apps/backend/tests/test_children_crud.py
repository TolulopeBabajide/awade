"""
Ownership enforcement and CRUD happy-path tests for the children router.

Split from test_children_router.py (AWD-M-116).

Covers:
- Ownership: parent A cannot access parent B's child → 404
- Happy path: create, list, get, delete child profile
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.models import ChildProfile
from children_factories import (
    _make_parent,
    _make_child_profile,
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
        mock_db = MagicMock()

        def query_side(model):
            q = MagicMock()
            if model is ChildProfile:
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
            q.filter.return_value.first.return_value = MagicMock()
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
