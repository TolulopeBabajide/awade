"""
Tests verifying that internal exception strings never appear in HTTP responses (AWD-M-129 split).

Covers H-08: str(e) must not leak in HTTPException detail fields.
"""

from unittest.mock import patch


# ---------------------------------------------------------------------------
# H-08: str(e) must not leak in HTTPException detail fields
# ---------------------------------------------------------------------------

class TestExceptionDetailSanitization:
    """Verify that unexpected internal errors never expose str(e) in HTTP responses."""

    def test_login_db_error_does_not_leak_exception(self, client):
        """A DB failure during login must return a generic 500, not the exception string."""
        # Simulate a DB query raising an unexpected exception
        boom = RuntimeError("INTERNAL: connection pool exhausted — secret detail")
        with patch(
            "apps.backend.services.auth_service.AuthService.authenticate_user",
            side_effect=boom,
        ):
            response = client.post("/api/auth/login", json={
                "email": "test@example.com",
                "password": "password123",
            })

        assert response.status_code == 500
        body = response.json()
        # The raw exception message must NOT appear in the response detail
        assert "secret detail" not in body.get("detail", ""), (
            "Exception string leaked into HTTPException detail — H-08"
        )
        assert "connection pool" not in body.get("detail", ""), (
            "Exception string leaked into HTTPException detail — H-08"
        )

    def test_registration_db_error_does_not_leak_exception(self, client):
        """A DB failure during registration must return a generic 500, not the exception string."""
        boom = RuntimeError("INTERNAL: unique constraint violated on secret_column")
        with patch(
            "apps.backend.services.auth_service.AuthService.register_user",
            side_effect=boom,
        ):
            response = client.post("/api/auth/signup", json={
                "email": "new@example.com",
                "password": "password123",
                "full_name": "New User",
                "role": "PARENT",
                "country": "NG",
            })

        assert response.status_code == 500
        body = response.json()
        assert "secret_column" not in body.get("detail", ""), (
            "Exception string leaked into HTTPException detail — H-08"
        )

    def test_google_auth_error_does_not_leak_exception(self, client):
        """A failure in Google auth must return a generic 500, not the exception string."""
        boom = RuntimeError("INTERNAL: oauth key file path /etc/secrets/key.pem missing")
        with patch(
            "apps.backend.services.auth_service.AuthService.authenticate_google_user",
            side_effect=boom,
        ):
            response = client.post("/api/auth/google", json={
                "credential": "dummy-token",
            })

        assert response.status_code == 500
        body = response.json()
        assert "/etc/secrets" not in body.get("detail", ""), (
            "Exception string leaked into HTTPException detail — H-08"
        )
