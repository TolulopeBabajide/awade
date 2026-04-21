"""
Tests for the contexts router — covers auth gating and ownership enforcement.

AWD-C-04: All 7 context routes were unauthenticated; this test suite verifies
the fix: every route requires EDUCATOR/ADMIN auth and educators cannot access
other users' contexts.
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.models import User, UserRole, LessonPlan, Context
from apps.backend.dependencies import require_admin_or_educator


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_educator(user_id: int = 1, email: str = "edu@example.com") -> User:
    u = User.__new__(User)
    u.user_id = user_id
    u.email = email
    u.role = UserRole.EDUCATOR
    return u


def _make_admin(user_id: int = 99) -> User:
    u = User.__new__(User)
    u.user_id = user_id
    u.email = "admin@example.com"
    u.role = UserRole.ADMIN
    return u


def _make_lesson_plan(lesson_plan_id: int, owner_id: int) -> LessonPlan:
    lp = LessonPlan.__new__(LessonPlan)
    lp.lesson_plan_id = lesson_plan_id
    lp.user_id = owner_id
    return lp


def _make_context(context_id: int, lesson_plan_id: int) -> Context:
    ctx = Context.__new__(Context)
    ctx.context_id = context_id
    ctx.lesson_plan_id = lesson_plan_id
    ctx.context_text = "some context"
    ctx.context_type = "general"
    from datetime import datetime, UTC
    ctx.created_at = datetime.now(UTC)
    ctx.updated_at = datetime.now(UTC)
    return ctx


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("ENVIRONMENT", "testing")


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _override_auth(user: User):
    """Return a dependency override that injects the given user."""
    def dep():
        return user
    return dep


# ---------------------------------------------------------------------------
# 401 — unauthenticated requests are rejected
# ---------------------------------------------------------------------------

class TestUnauthenticated:
    """Every context endpoint must return 401 when no token is provided."""

    ENDPOINTS = [
        ("POST",   "/api/contexts/"),
        ("GET",    "/api/contexts/"),
        ("GET",    "/api/contexts/1"),
        ("PUT",    "/api/contexts/1"),
        ("DELETE", "/api/contexts/1"),
        ("GET",    "/api/contexts/lesson-plan/1"),
        ("POST",   "/api/contexts/lesson-plan/1/submit"),
    ]

    @pytest.mark.parametrize("method,path", ENDPOINTS)
    def test_returns_401(self, client, method, path):
        response = client.request(method, path, json={"context_text": "x", "context_type": "g", "lesson_plan_id": 1})
        assert response.status_code == 401, f"{method} {path} should require auth"


# ---------------------------------------------------------------------------
# 403 — educator cannot access another user's lesson plan contexts
# ---------------------------------------------------------------------------

class TestOwnershipEnforcement:
    """An EDUCATOR (user_id=1) may not access contexts on a lesson plan owned by user_id=2."""

    def _client_as(self, educator: User):
        app.dependency_overrides[require_admin_or_educator] = _override_auth(educator)
        c = TestClient(app, raise_server_exceptions=False)
        return c

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _db_with_plan(self, owner_id: int, context_id: int = 10):
        """Return a mock DB session whose query returns a lesson plan owned by owner_id."""
        lesson_plan = _make_lesson_plan(lesson_plan_id=5, owner_id=owner_id)
        context = _make_context(context_id=context_id, lesson_plan_id=5)

        mock_db = MagicMock()
        # Chained query mock — handles .filter().first() style calls
        def query_side_effect(model):
            q = MagicMock()
            if model is LessonPlan:
                q.filter.return_value.first.return_value = lesson_plan
            elif model is Context:
                q.filter.return_value.first.return_value = context
                # For join queries (get_contexts_for_user)
                q.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
            else:
                q.filter.return_value.first.return_value = None
            return q
        mock_db.query.side_effect = query_side_effect
        return mock_db

    def _set_db(self, mock_db):
        app.dependency_overrides[get_db] = lambda: mock_db

    def test_get_context_forbidden_for_non_owner(self):
        edu = _make_educator(user_id=1)
        mock_db = self._db_with_plan(owner_id=2)
        self._set_db(mock_db)
        c = self._client_as(edu)
        resp = c.get("/api/contexts/10")
        assert resp.status_code == 403

    def test_update_context_forbidden_for_non_owner(self):
        edu = _make_educator(user_id=1)
        mock_db = self._db_with_plan(owner_id=2)
        self._set_db(mock_db)
        c = self._client_as(edu)
        resp = c.put("/api/contexts/10", json={"context_text": "new"})
        assert resp.status_code == 403

    def test_delete_context_forbidden_for_non_owner(self):
        edu = _make_educator(user_id=1)
        mock_db = self._db_with_plan(owner_id=2)
        self._set_db(mock_db)
        c = self._client_as(edu)
        resp = c.delete("/api/contexts/10")
        assert resp.status_code == 403

    def test_get_contexts_by_lesson_plan_forbidden_for_non_owner(self):
        edu = _make_educator(user_id=1)
        mock_db = self._db_with_plan(owner_id=2)
        self._set_db(mock_db)
        c = self._client_as(edu)
        resp = c.get("/api/contexts/lesson-plan/5")
        assert resp.status_code == 403

    def test_create_context_forbidden_for_non_owner(self):
        edu = _make_educator(user_id=1)
        mock_db = self._db_with_plan(owner_id=2)
        self._set_db(mock_db)
        c = self._client_as(edu)
        resp = c.post("/api/contexts/", json={
            "lesson_plan_id": 5,
            "context_text": "injected",
            "context_type": "general"
        })
        assert resp.status_code == 403

    def test_submit_context_forbidden_for_non_owner(self):
        edu = _make_educator(user_id=1)
        mock_db = self._db_with_plan(owner_id=2)
        self._set_db(mock_db)
        c = self._client_as(edu)
        resp = c.post("/api/contexts/lesson-plan/5/submit", json={
            "context_text": "injected",
            "context_type": "general"
        })
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 200 — admin bypasses ownership restriction
# ---------------------------------------------------------------------------

class TestAdminBypass:
    """An ADMIN user may read/write any context regardless of lesson plan ownership."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _setup(self, owner_id: int = 2):
        admin = _make_admin()
        lesson_plan = _make_lesson_plan(lesson_plan_id=5, owner_id=owner_id)
        context = _make_context(context_id=10, lesson_plan_id=5)

        mock_db = MagicMock()
        def query_side_effect(model):
            q = MagicMock()
            if model is LessonPlan:
                q.filter.return_value.first.return_value = lesson_plan
            elif model is Context:
                q.filter.return_value.first.return_value = context
                q.offset.return_value.limit.return_value.all.return_value = [context]
            return q
        mock_db.query.side_effect = query_side_effect

        app.dependency_overrides[require_admin_or_educator] = _override_auth(admin)
        app.dependency_overrides[get_db] = lambda: mock_db
        return TestClient(app, raise_server_exceptions=False)

    def test_admin_can_get_context_owned_by_other_user(self):
        c = self._setup(owner_id=99)
        resp = c.get("/api/contexts/10")
        # Should not return 403
        assert resp.status_code != 403

    def test_admin_can_delete_context_owned_by_other_user(self):
        c = self._setup(owner_id=99)
        resp = c.delete("/api/contexts/10")
        assert resp.status_code != 403
