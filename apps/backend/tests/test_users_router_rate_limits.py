"""
AWD-M-316 — rate limit structure tests for users.py.

Verifies that the 6 previously unprotected endpoints carry `request: Request`
(required by slowapi) and that the 2 already-limited endpoints are unchanged.
"""

import inspect
import pytest

import apps.backend.routers.users as users_module


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("ENVIRONMENT", "testing")


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient
    from apps.backend.main import app
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


class TestUsersRateLimitStructure:
    """AWD-M-316 — all users endpoints must carry request: Request for slowapi."""

    @pytest.mark.parametrize("func_name,expected_limit", [
        # Newly rate-limited (this fix)
        ("get_users",            "60/minute"),
        ("get_user",             "60/minute"),
        ("get_user_profile",     "60/minute"),
        ("update_user",          "30/minute"),
        ("delete_user",          "30/minute"),
        ("update_user_profile",  "30/minute"),
        # Pre-existing (regression guard)
        ("export_my_data",       "5/minute"),
        ("delete_my_account",    "3/minute"),
    ])
    def test_rate_limited_endpoint_has_request_parameter(self, func_name, expected_limit):
        """Each rate-limited endpoint must accept `request: Request` for slowapi."""
        func = getattr(users_module, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"{func_name} is missing the `request: Request` parameter required by slowapi "
            f"(@limiter.limit({expected_limit!r}) will silently fail without it)."
        )

    def test_request_param_is_fastapi_request(self):
        """The `request` param on get_users must be typed as fastapi.Request."""
        from fastapi import Request
        sig = inspect.signature(users_module.get_users)
        annotation = sig.parameters["request"].annotation
        assert annotation is Request, (
            "The `request` param must be typed as fastapi.Request."
        )

    # Route-registration checks — verify decorator application did not drop the route

    def test_get_users_route_is_registered(self, client):
        """GET /api/users returns 401 (auth required), not 404."""
        resp = client.get("/api/users")
        assert resp.status_code != 404, (
            "GET /api/users returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_get_user_route_is_registered(self, client):
        """GET /api/users/{id} returns 401 (auth required), not 404."""
        resp = client.get("/api/users/1")
        assert resp.status_code != 404, (
            "GET /api/users/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_update_user_route_is_registered(self, client):
        """PUT /api/users/{id} returns 401 (auth required), not 404."""
        resp = client.put("/api/users/1", json={})
        assert resp.status_code != 404, (
            "PUT /api/users/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_delete_user_route_is_registered(self, client):
        """DELETE /api/users/{id} returns 401 (auth required), not 404."""
        resp = client.delete("/api/users/1")
        assert resp.status_code != 404, (
            "DELETE /api/users/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_get_user_profile_route_is_registered(self, client):
        """GET /api/users/{id}/profile returns 401 (auth required), not 404."""
        resp = client.get("/api/users/1/profile")
        assert resp.status_code != 404, (
            "GET /api/users/1/profile returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_update_user_profile_route_is_registered(self, client):
        """PUT /api/users/{id}/profile returns 401 (auth required), not 404."""
        resp = client.put("/api/users/1/profile", json={})
        assert resp.status_code != 404, (
            "PUT /api/users/1/profile returned 404 — route removed or @limiter.limit broke routing."
        )
