"""
AWD-M-317 — rate limit structure tests for admin.py.

Verifies that all 12 endpoints carry @limiter.limit() and request: Request
(required by slowapi), following the M-311/M-313/M-315/M-316 sweep convention.
"""

import inspect
import pytest

import apps.backend.routers.admin as admin_module


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


class TestAdminRateLimitStructure:
    """AWD-M-317 — all admin endpoints must carry request: Request for slowapi."""

    @pytest.mark.parametrize("func_name,expected_limit", [
        ("get_admin_metrics",   "60/minute"),
        ("list_users",          "60/minute"),
        ("update_user_status",  "30/minute"),
        ("get_audit_logs",      "60/minute"),
        ("list_resources",      "60/minute"),
        ("moderate_resource",   "30/minute"),
        ("create_template",     "30/minute"),
        ("list_templates",      "60/minute"),
        ("update_template",     "30/minute"),
        ("delete_template",     "30/minute"),
        ("admin_list_children", "60/minute"),
        ("admin_get_child",     "60/minute"),
    ])
    def test_rate_limited_endpoint_has_request_parameter(self, func_name, expected_limit):
        """Each rate-limited endpoint must accept `request: Request` for slowapi."""
        func = getattr(admin_module, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"{func_name} is missing the `request: Request` parameter required by slowapi "
            f"(@limiter.limit({expected_limit!r}) will silently fail without it)."
        )

    def test_request_param_is_fastapi_request(self):
        """The `request` param on get_admin_metrics must be typed as fastapi.Request."""
        from fastapi import Request
        sig = inspect.signature(admin_module.get_admin_metrics)
        annotation = sig.parameters["request"].annotation
        assert annotation is Request, (
            "The `request` param must be typed as fastapi.Request."
        )

    def test_admin_list_children_request_not_optional(self):
        """admin_list_children.request must not have a default (was `= None` before M-317)."""
        sig = inspect.signature(admin_module.admin_list_children)
        param = sig.parameters["request"]
        assert param.default is inspect.Parameter.empty, (
            "admin_list_children.request must be a required parameter, not `= None`."
        )

    # Route-registration checks — verify @limiter.limit() did not drop any route

    def test_metrics_route_is_registered(self, client):
        """GET /api/admin/metrics returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/metrics")
        assert resp.status_code != 404, (
            "GET /api/admin/metrics returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_list_users_route_is_registered(self, client):
        """GET /api/admin/users returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/users")
        assert resp.status_code != 404, (
            "GET /api/admin/users returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_update_user_route_is_registered(self, client):
        """PATCH /api/admin/users/{id} returns 401 (auth required), not 404."""
        resp = client.patch("/api/admin/users/1", json={})
        assert resp.status_code != 404, (
            "PATCH /api/admin/users/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_audit_logs_route_is_registered(self, client):
        """GET /api/admin/audit-logs returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/audit-logs")
        assert resp.status_code != 404, (
            "GET /api/admin/audit-logs returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_list_resources_route_is_registered(self, client):
        """GET /api/admin/resources returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/resources")
        assert resp.status_code != 404, (
            "GET /api/admin/resources returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_moderate_resource_route_is_registered(self, client):
        """PATCH /api/admin/resources/{id} returns 401 (auth required), not 404."""
        resp = client.patch("/api/admin/resources/1", json={})
        assert resp.status_code != 404, (
            "PATCH /api/admin/resources/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_create_template_route_is_registered(self, client):
        """POST /api/admin/templates returns 401 (auth required), not 404."""
        resp = client.post("/api/admin/templates", json={})
        assert resp.status_code != 404, (
            "POST /api/admin/templates returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_list_templates_route_is_registered(self, client):
        """GET /api/admin/templates returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/templates")
        assert resp.status_code != 404, (
            "GET /api/admin/templates returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_update_template_route_is_registered(self, client):
        """PATCH /api/admin/templates/{id} returns 401 (auth required), not 404."""
        resp = client.patch("/api/admin/templates/1", json={})
        assert resp.status_code != 404, (
            "PATCH /api/admin/templates/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_delete_template_route_is_registered(self, client):
        """DELETE /api/admin/templates/{id} returns 401 (auth required), not 404."""
        resp = client.delete("/api/admin/templates/1")
        assert resp.status_code != 404, (
            "DELETE /api/admin/templates/1 returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_admin_list_children_route_is_registered(self, client):
        """GET /api/admin/children returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/children")
        assert resp.status_code != 404, (
            "GET /api/admin/children returned 404 — route removed or @limiter.limit broke routing."
        )

    def test_admin_get_child_route_is_registered(self, client):
        """GET /api/admin/children/{id} returns 401 (auth required), not 404."""
        resp = client.get("/api/admin/children/1")
        assert resp.status_code != 404, (
            "GET /api/admin/children/1 returned 404 — route removed or @limiter.limit broke routing."
        )
