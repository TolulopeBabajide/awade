"""
Tests for configurable password max-length behaviour (AWD-M-129 split).

Covers:
- M-91: UserLogin.validate_password_bytes must respect PASSWORD_MAX_LENGTH env var
- H-70: get_password_max_length() must clamp to 72 even when env var is higher (AWD-M-95)
"""

import apps.backend.schemas.users as schemas_module


# ---------------------------------------------------------------------------
# M-91: UserLogin.validate_password_bytes must use get_password_max_length()
# ---------------------------------------------------------------------------

class TestUserLoginPasswordMaxLengthConfigurable:
    """Verify that UserLogin.validate_password_bytes respects the configured
    PASSWORD_MAX_LENGTH env var rather than hardcoding 72 (AWD-M-91).

    If PASSWORD_MAX_LENGTH is set to a value lower than 72 (e.g. 64), login
    must reject passwords exceeding that lower limit with HTTP 422, not accept
    them up to the old hardcoded 72."""

    def test_login_validator_respects_custom_lower_max_length(self, client, monkeypatch):
        """A password within the default 72-byte limit but exceeding a stricter
        configured limit (64 bytes) must be rejected with HTTP 422."""
        monkeypatch.setenv("PASSWORD_MAX_LENGTH", "64")
        # Reload the env-reading function so the patched env takes effect
        monkeypatch.setattr(schemas_module, "get_password_max_length", lambda: 64)

        # 65 ASCII bytes: over the patched limit of 64, under the default 72
        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "A" * 65},
        )
        assert response.status_code == 422, (
            f"Login with 65-byte password must yield 422 when PASSWORD_MAX_LENGTH=64, "
            f"got {response.status_code}: {response.text} (AWD-M-91)"
        )

    def test_login_validator_accepts_password_at_custom_boundary(self, client, monkeypatch):
        """A password exactly at the custom configured limit must pass schema
        validation (64-byte password when PASSWORD_MAX_LENGTH=64)."""
        monkeypatch.setattr(schemas_module, "get_password_max_length", lambda: 64)

        # 64 ASCII bytes: exactly at the patched limit — must not be rejected by schema
        response = client.post(
            "/api/auth/login",
            json={"email": "nonexistent@example.com", "password": "A" * 64},
        )
        # Schema passes → auth layer runs → 401 (wrong user); never 422 (schema reject) or 500
        assert response.status_code == 401, (
            f"Expected 401 (schema passes, auth rejects unknown user), "
            f"got {response.status_code}: {response.text} (AWD-M-93)"
        )


# ---------------------------------------------------------------------------
# H-70: get_password_max_length() must clamp to 72 even if env var is higher
# ---------------------------------------------------------------------------

class TestPasswordMaxLengthUpperBoundCap:
    """Verify that PASSWORD_MAX_LENGTH values above 72 are silently clamped to 72.

    AWD-M-72 fixed the default from 128 → 72.  AWD-H-70 adds a hard upper-bound
    cap so that misconfiguring PASSWORD_MAX_LENGTH=200 (or any value > 72) cannot
    re-enable the bcrypt ValueError / HTTP 500 crash path.
    """

    def test_get_password_max_length_clamps_to_72_when_env_exceeds_limit(self, monkeypatch):
        """get_password_max_length() must return 72 even when env var is set above 72."""
        monkeypatch.setenv("PASSWORD_MAX_LENGTH", "200")
        # Re-read the function with the patched env — reload is not needed because
        # get_password_max_length() calls os.getenv() at call time.
        result = schemas_module.get_password_max_length()
        assert result == 72, (
            f"get_password_max_length() must clamp to 72, got {result} when "
            f"PASSWORD_MAX_LENGTH=200 (AWD-H-70)"
        )

    def test_login_with_73_byte_password_yields_422_not_500_when_env_set_to_200(
        self, client, monkeypatch
    ):
        """A 73-byte login password must yield HTTP 422 even if PASSWORD_MAX_LENGTH=200.

        With PASSWORD_MAX_LENGTH=200 set, the real get_password_max_length() must
        return min(200, 72) = 72 (AWD-H-70 cap), so the validator still rejects 73
        bytes with HTTP 422 rather than letting bcrypt raise ValueError → HTTP 500.
        This test exercises the full stack without mocking the cap function (AWD-M-95).
        """
        monkeypatch.setenv("PASSWORD_MAX_LENGTH", "200")

        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "A" * 73},
        )
        assert response.status_code == 422, (
            f"73-byte login password must yield 422 even when PASSWORD_MAX_LENGTH=200; "
            f"got {response.status_code}: {response.text} (AWD-H-70, AWD-M-95)"
        )

    def test_register_with_73_byte_password_yields_422_when_env_set_to_200(
        self, client, monkeypatch
    ):
        """A 73-byte registration password must yield HTTP 422 even if PASSWORD_MAX_LENGTH=200.

        With PASSWORD_MAX_LENGTH=200 set, the real get_password_max_length() must
        return min(200, 72) = 72 (AWD-H-70 cap), so the validator still rejects 73
        bytes with HTTP 422. Tests the full stack without mocking the cap (AWD-M-95).
        """
        monkeypatch.setenv("PASSWORD_MAX_LENGTH", "200")

        response = client.post(
            "/api/auth/signup",
            json={
                "email": "newuser_h70@example.com",
                "password": "A" * 73,
                "full_name": "Test User",
                "role": "EDUCATOR",
                "country": "NG",
            },
        )
        assert response.status_code == 422, (
            f"73-byte registration password must yield 422 even when PASSWORD_MAX_LENGTH=200; "
            f"got {response.status_code}: {response.text} (AWD-H-70, AWD-M-95)"
        )
