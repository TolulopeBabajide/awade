"""Rate limiting tests for auth and guide-generation endpoints (AWD-M-223 split from test_security.py)."""

import asyncio

import pytest


@pytest.mark.skip(
    reason="AWD-M-44 TestClient shares slowapi limiter state across test files — "
           "needs rate_limiter_reset autouse fixture (approach from AWD-H-29) before "
           "a meaningful 429 assertion can be made without flake risk."
)
@pytest.mark.asyncio
async def test_rate_limiting():
    """
    Test rate limiting on auth endpoints.

    Skipped: the module-level TestClient shares the in-process slowapi limiter
    with every other test file.  Earlier tests can exhaust the 10/minute login
    bucket, causing this test to receive 429 when it expects 200, or vice-versa.
    A proper implementation requires the `rate_limiter_reset` autouse fixture
    described in AWD-H-29 — add it to conftest.py, then replace the body below
    with real 429-assertion logic.
    """
    pass


class TestGenerateGuideRateLimit:
    """
    H-07 — Parent guide generation endpoint must be rate-limited.

    The POST /api/children/{child_id}/guides/generate endpoint calls OpenAI on
    every cache miss. Without a rate limit any authenticated user can trigger
    unlimited API calls, creating a cost-abuse vector.

    These tests verify the structural requirements for slowapi rate limiting:
    - The route accepts a `request: Request` parameter (required by slowapi).
    - The route is registered in the application and returns 403 when
      unauthenticated (not 404 — confirming the route exists and the
      decorator stack is intact).
    """

    def test_generate_guide_route_is_registered(self, client):
        """Unauthenticated POST returns 401, not 404 — route exists in the app."""
        response = client.post("/api/children/1/guides/generate?topic_id=1")
        assert response.status_code == 401, (
            f"Expected 401 (auth required), got {response.status_code}. "
            "If 404, the route may have been removed or the rate-limit decorator broke routing."
        )

    def test_generate_guide_has_request_parameter(self):
        """generate_guide must accept `request: Request` — required by slowapi."""
        import inspect
        from apps.backend.routers.children import generate_guide

        sig = inspect.signature(generate_guide)
        assert "request" in sig.parameters, (
            "generate_guide is missing the `request: Request` parameter. "
            "slowapi @limiter.limit requires it to extract the client IP."
        )


class TestAuthEndpointRateLimitStructure:
    """
    H-13 — Auth endpoints must be rate-limited.

    `/auth/google`, `/auth/refresh`, `/auth/forgot-password`, and `/auth/reset-password`
    were previously unprotected, enabling email-bombing, user enumeration, and cheap DoS.

    These structural tests verify:
    - Each newly rate-limited endpoint accepts a `request: Request` parameter
      (required by slowapi to extract the client IP).
    - Each endpoint is registered in the app (returns auth-required status, not 404).
    """

    @pytest.mark.parametrize("func_name,module_path", [
        ("google_auth", "apps.backend.routers.auth"),
        ("refresh_token", "apps.backend.routers.auth"),
        ("forgot_password", "apps.backend.routers.auth"),
        ("reset_password", "apps.backend.routers.auth"),
    ])
    def test_rate_limited_endpoint_has_request_parameter(self, func_name, module_path):
        """Each rate-limited endpoint must accept `request: Request` for slowapi."""
        import inspect
        import importlib
        module = importlib.import_module(module_path)
        func = getattr(module, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"{func_name} is missing the `request: Request` parameter required by slowapi."
        )

    def test_google_auth_route_is_registered(self, client):
        """POST /api/auth/google returns 422 (validation), not 404 — route exists."""
        response = client.post("/api/auth/google", json={})
        assert response.status_code != 404, (
            "POST /api/auth/google returned 404 — route missing or decorator broke routing."
        )

    def test_forgot_password_route_is_registered(self, client):
        """POST /api/auth/forgot-password returns 422 (validation), not 404 — route exists."""
        response = client.post("/api/auth/forgot-password", json={})
        assert response.status_code != 404, (
            "POST /api/auth/forgot-password returned 404 — route missing or decorator broke routing."
        )

    def test_reset_password_route_is_registered(self, client):
        """POST /api/auth/reset-password returns 422 (validation), not 404 — route exists."""
        response = client.post("/api/auth/reset-password", json={})
        assert response.status_code != 404, (
            "POST /api/auth/reset-password returned 404 — route missing or decorator broke routing."
        )

    def test_refresh_route_is_registered(self, client):
        """POST /api/auth/refresh returns 401 (no cookie), not 404 — route exists."""
        response = client.post("/api/auth/refresh")
        assert response.status_code != 404, (
            "POST /api/auth/refresh returned 404 — route missing or decorator broke routing."
        )
