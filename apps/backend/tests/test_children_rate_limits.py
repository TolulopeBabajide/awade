"""
Rate-limit structural tests for the children router.

Split from test_children_router.py (AWD-M-116).

Covers AWD-M-111:
- create_child, toggle_bookmark, and export_guide_pdf must carry the
  `request: Request` parameter required by slowapi.
- The routes must still be registered after decorator application.
"""

import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app


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
# Rate-limit structural checks
# ---------------------------------------------------------------------------

class TestChildrenRateLimitStructure:
    """
    M-111 — create_child, toggle_bookmark, and export_guide_pdf must be
    rate-limited via @limiter.limit() to prevent profile-spam and CPU-abuse.

    These tests verify structural requirements (request parameter present,
    routes still registered) — not live 429 behaviour (which requires
    resetting slowapi state per-request, covered by the autouse fixture).
    """

    @pytest.mark.parametrize("func_name,expected_limit", [
        ("create_child",    "20/minute"),
        ("toggle_bookmark", "30/minute"),
        ("export_guide_pdf", "5/minute"),
    ])
    def test_rate_limited_endpoint_has_request_parameter(self, func_name, expected_limit):
        """Each rate-limited endpoint must accept `request: Request` for slowapi."""
        import inspect
        from apps.backend.routers import children as children_module
        func = getattr(children_module, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"{func_name} is missing the `request: Request` parameter required by slowapi "
            f"(@limiter.limit({expected_limit!r}) will silently fail without it)."
        )

    def test_create_child_route_is_registered(self, client):
        """POST /api/children returns 401 (auth required), not 404."""
        resp = client.post("/api/children", json={"name": "Test"})
        assert resp.status_code != 404, (
            "POST /api/children returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_toggle_bookmark_route_is_registered(self, client):
        """POST /api/guides/{id}/bookmark returns 401 (auth required), not 404."""
        resp = client.post("/api/guides/1/bookmark")
        assert resp.status_code != 404, (
            "POST /api/guides/1/bookmark returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_export_guide_pdf_route_is_registered(self, client):
        """GET /api/guides/{id}/export returns 401 (auth required), not 404."""
        resp = client.get("/api/guides/1/export")
        assert resp.status_code != 404, (
            "GET /api/guides/1/export returned 404 — route removed or @limiter.limit broke routing."
        )
