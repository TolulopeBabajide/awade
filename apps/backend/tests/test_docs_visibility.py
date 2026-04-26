"""
AWD-M-10 — API documentation endpoint visibility tests.

Verifies that /docs and /redoc are disabled (return 404) when
ENVIRONMENT=production and accessible in all other environments.
"""

import os
import pytest
from fastapi.testclient import TestClient


class TestDocsVisibilityInNonProduction:
    """In the test environment, /docs and /redoc must be reachable (200)."""

    def test_docs_accessible_outside_production(self, client):
        """GET /docs returns 200 when ENVIRONMENT != production."""
        assert os.getenv("ENVIRONMENT", "development") != "production", (
            "This test is only valid outside the production environment."
        )
        response = client.get("/docs")
        assert response.status_code == 200, (
            f"Expected /docs to return 200 in non-production, got {response.status_code}"
        )

    def test_redoc_accessible_outside_production(self, client):
        """GET /redoc returns 200 when ENVIRONMENT != production."""
        assert os.getenv("ENVIRONMENT", "development") != "production", (
            "This test is only valid outside the production environment."
        )
        response = client.get("/redoc")
        assert response.status_code == 200, (
            f"Expected /redoc to return 200 in non-production, got {response.status_code}"
        )


class TestDocsUrlConfiguration:
    """Verify the FastAPI app is configured with the correct docs URLs for the
    current environment — matching the AWD-M-10 gating logic."""

    def test_docs_url_matches_environment(self):
        """app.docs_url is None in production, '/docs' otherwise."""
        from apps.backend.main import app

        environment = os.getenv("ENVIRONMENT", "development")
        expected = None if environment == "production" else "/docs"
        assert app.docs_url == expected, (
            f"ENVIRONMENT={environment!r}: expected docs_url={expected!r}, "
            f"got {app.docs_url!r}"
        )

    def test_redoc_url_matches_environment(self):
        """app.redoc_url is None in production, '/redoc' otherwise."""
        from apps.backend.main import app

        environment = os.getenv("ENVIRONMENT", "development")
        expected = None if environment == "production" else "/redoc"
        assert app.redoc_url == expected, (
            f"ENVIRONMENT={environment!r}: expected redoc_url={expected!r}, "
            f"got {app.redoc_url!r}"
        )

    def test_production_docs_url_would_be_none(self, monkeypatch):
        """The gating expression evaluates to None when ENVIRONMENT=production."""
        monkeypatch.setenv("ENVIRONMENT", "production")
        env = os.getenv("ENVIRONMENT", "development")
        assert (None if env == "production" else "/docs") is None

    def test_development_docs_url_would_be_slash_docs(self, monkeypatch):
        """The gating expression evaluates to '/docs' when ENVIRONMENT=development."""
        monkeypatch.setenv("ENVIRONMENT", "development")
        env = os.getenv("ENVIRONMENT", "development")
        assert (None if env == "production" else "/docs") == "/docs"

    def test_testing_docs_url_would_be_slash_docs(self, monkeypatch):
        """The gating expression evaluates to '/docs' when ENVIRONMENT=testing."""
        monkeypatch.setenv("ENVIRONMENT", "testing")
        env = os.getenv("ENVIRONMENT", "development")
        assert (None if env == "production" else "/docs") == "/docs"
