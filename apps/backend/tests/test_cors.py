"""CORS, trusted host, and allowed-hosts configuration tests (AWD-M-223 split from test_security.py)."""

import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app

client = TestClient(app)


def test_cors_headers():
    """Test CORS configuration."""
    # Test with allowed origin (simulated by default config)
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    # Note: In test environment, CORS might behave differently depending on middleware setup
    # But we check if the middleware is active
    assert response.status_code == 200


def test_cors_allowed_methods_and_headers():
    """AWD-M-36: CORS middleware must not use wildcard allow_methods / allow_headers.

    Verify the CORS middleware is configured with an explicit method list and header
    list rather than '*', so that cross-origin requests are not over-permissioned.
    """
    from apps.backend.main import app as _app
    from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware

    cors_middleware = None
    for middleware in _app.user_middleware:
        if middleware.cls is StarletteCORSMiddleware:
            cors_middleware = middleware
            break

    assert cors_middleware is not None, "CORSMiddleware not found in app middleware stack"

    allowed_methods = cors_middleware.kwargs.get("allow_methods", [])
    allowed_headers = cors_middleware.kwargs.get("allow_headers", [])

    # Must not use wildcard
    assert "*" not in allowed_methods, "allow_methods must not contain wildcard '*'"
    assert "*" not in allowed_headers, "allow_headers must not contain wildcard '*'"

    # Must include the methods the frontend actually uses
    for method in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]:
        assert method in allowed_methods, f"allow_methods is missing '{method}'"

    # Must include the headers the frontend actually sends
    for header in ["Authorization", "Content-Type"]:
        assert header in allowed_headers, f"allow_headers is missing '{header}'"


def test_trusted_host_middleware_registered():
    """AWD-L-04: TrustedHostMiddleware must be present in the middleware stack."""
    from apps.backend.main import app as _app
    from fastapi.middleware.trustedhost import TrustedHostMiddleware

    middleware_classes = [m.cls for m in _app.user_middleware]
    assert TrustedHostMiddleware in middleware_classes, (
        "TrustedHostMiddleware not found in app middleware stack — AWD-L-04."
    )


def test_trusted_host_allows_requests_with_default_config():
    """AWD-L-04: Default config (ALLOWED_HOSTS=*) must allow any Host header."""
    # Module-level TestClient uses the default dev config (ALLOWED_HOSTS not set → "*").
    # A request with an arbitrary Host header must still reach the route handler.
    response = client.get("/", headers={"Host": "example.com"})
    assert response.status_code == 200, (
        f"TrustedHostMiddleware with ALLOWED_HOSTS='*' returned {response.status_code} "
        "for Host: example.com — wildcard config must allow any host."
    )


class TestGetAllowedHosts:
    """AWD-L-54: _get_allowed_hosts() must mirror JWT_SECRET_KEY guard pattern."""

    def test_returns_wildcard_in_development(self, monkeypatch):
        """ALLOWED_HOSTS unset in development environment returns ['*']."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        assert _get_allowed_hosts() == ["*"]

    def test_returns_wildcard_in_testing(self, monkeypatch):
        """ALLOWED_HOSTS unset in testing environment returns ['*']."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "testing")
        assert _get_allowed_hosts() == ["*"]

    def test_returns_wildcard_in_test(self, monkeypatch):
        """ALLOWED_HOSTS unset when ENVIRONMENT='test' returns ['*']."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "test")
        assert _get_allowed_hosts() == ["*"]

    def test_raises_in_production_without_allowed_hosts(self, monkeypatch):
        """ALLOWED_HOSTS unset in production must raise RuntimeError."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _get_allowed_hosts()

    def test_raises_in_staging_without_allowed_hosts(self, monkeypatch):
        """ALLOWED_HOSTS unset in staging must raise RuntimeError."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.delenv("ALLOWED_HOSTS", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "staging")
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _get_allowed_hosts()

    def test_returns_parsed_list_when_set(self, monkeypatch):
        """Explicit ALLOWED_HOSTS value is parsed and returned in any environment."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.setenv("ALLOWED_HOSTS", "awade.app,www.awade.app")
        monkeypatch.setenv("ENVIRONMENT", "production")
        assert _get_allowed_hosts() == ["awade.app", "www.awade.app"]

    def test_wildcard_env_var_raises_in_production(self, monkeypatch):
        """ALLOWED_HOSTS='*' explicit wildcard in production still raises RuntimeError."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.setenv("ALLOWED_HOSTS", "*")
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _get_allowed_hosts()

    def test_whitespace_only_raises_in_production(self, monkeypatch):
        """AWD-H-112: ALLOWED_HOSTS='  ' (whitespace-only) must raise RuntimeError, not silently return ['*']."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.setenv("ALLOWED_HOSTS", "  ")
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _get_allowed_hosts()

    def test_comma_only_raises_in_production(self, monkeypatch):
        """AWD-H-113: ALLOWED_HOSTS=',' must raise RuntimeError in production, not silently return ['*']."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.setenv("ALLOWED_HOSTS", ",")
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _get_allowed_hosts()

    def test_all_whitespace_segments_raises_in_production(self, monkeypatch):
        """AWD-H-113: ALLOWED_HOSTS=', , ,' (all-blank segments) must raise RuntimeError in production."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.setenv("ALLOWED_HOSTS", ", , ,")
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _get_allowed_hosts()

    def test_comma_only_returns_wildcard_in_development(self, monkeypatch):
        """AWD-H-113: ALLOWED_HOSTS=',' in development should fall back to ['*'] safely."""
        from apps.backend.main import _get_allowed_hosts
        monkeypatch.setenv("ALLOWED_HOSTS", ",")
        monkeypatch.setenv("ENVIRONMENT", "development")
        assert _get_allowed_hosts() == ["*"]


class TestRequireExplicitHosts:
    """AWD-M-241: _require_explicit_hosts() extracted helper — unit tests."""

    def test_raises_for_production(self):
        """Non-safe environment raises RuntimeError."""
        from apps.backend.main import _require_explicit_hosts
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _require_explicit_hosts("production")

    def test_raises_for_staging(self):
        """Non-safe environment raises RuntimeError."""
        from apps.backend.main import _require_explicit_hosts
        with pytest.raises(RuntimeError, match="ALLOWED_HOSTS"):
            _require_explicit_hosts("staging")

    def test_does_not_raise_for_development(self):
        """Safe environment returns without raising."""
        from apps.backend.main import _require_explicit_hosts
        _require_explicit_hosts("development")

    def test_does_not_raise_for_test(self):
        """Safe environment returns without raising."""
        from apps.backend.main import _require_explicit_hosts
        _require_explicit_hosts("test")

    def test_does_not_raise_for_testing(self):
        """Safe environment returns without raising."""
        from apps.backend.main import _require_explicit_hosts
        _require_explicit_hosts("testing")

    def test_error_message_includes_environment(self):
        """Error message includes the offending environment value."""
        from apps.backend.main import _require_explicit_hosts
        with pytest.raises(RuntimeError, match="ENVIRONMENT='production'"):
            _require_explicit_hosts("production")
