"""
Auth-gating tests for the children router.

Split from test_children_router.py (AWD-M-116).

Covers:
- Unauthenticated requests → 401 on every children endpoint
- EDUCATOR role → 403 on every children endpoint (parent-only)
"""

import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app
from children_factories import (
    CHILDREN_ENDPOINTS,
    _make_educator,
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
# 401 — unauthenticated requests
# ---------------------------------------------------------------------------

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
