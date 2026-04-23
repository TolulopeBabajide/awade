
import pytest
import bcrypt
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

def test_login_sets_httponly_cookies(client, sample_user, test_db):
    """Test that login sets both access_token and refresh_token as HttpOnly cookies."""
    password = "testpassword123"
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    sample_user.password_hash = pw_hash
    test_db.commit()

    response = client.post("/api/auth/login", json={"email": sample_user.email, "password": password})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
    assert response.status_code == 200

    # Both tokens must be present as cookies
    cookies = response.cookies
    assert "access_token" in cookies, "access_token cookie missing from login response"
    assert "refresh_token" in cookies, "refresh_token cookie missing from login response"

    # Verify HttpOnly + SameSite on Set-Cookie headers
    set_cookie_headers = response.headers.get_list("set-cookie") if hasattr(response.headers, "get_list") else [response.headers.get("set-cookie", "")]
    combined = " ".join(set_cookie_headers).lower()
    assert "httponly" in combined
    assert "lax" in combined

    # access_token must NOT appear in the JSON body
    body = response.json()
    assert "access_token" not in body, "access_token must not be returned in the response body"
    assert "user" in body, "user payload missing from login response"


def test_refresh_token_flow(client, sample_user, test_db):
    """Refresh rotates both cookies; response body contains user but no raw token."""
    password = "testpassword123"
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    sample_user.password_hash = pw_hash
    test_db.commit()

    # 1. Login to establish cookies
    login_response = client.post("/api/auth/login", json={"email": sample_user.email, "password": password})
    assert login_response.status_code == 200

    # 2. Call refresh — cookies are forwarded automatically by TestClient
    refresh_response = client.post("/api/auth/refresh")
    if refresh_response.status_code != 200:
        print(f"Refresh failed: {refresh_response.json()}")
    assert refresh_response.status_code == 200

    data = refresh_response.json()
    # Body must contain user + token_type but NOT the raw access_token
    assert "user" in data
    assert data["token_type"] == "bearer"
    assert "access_token" not in data, "access_token must not be returned in refresh response body"

    # Rotated access_token cookie must be present
    assert "access_token" in refresh_response.cookies, "rotated access_token cookie missing"


def test_logout_clears_cookies(client, sample_user, test_db):
    """Logout clears both access_token and refresh_token cookies."""
    password = "testpassword123"
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    sample_user.password_hash = pw_hash
    test_db.commit()

    client.post("/api/auth/login", json={"email": sample_user.email, "password": password})

    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    # Both cookies must be cleared (empty value or Max-Age=0)
    set_cookie = response.headers.get("set-cookie", "")
    assert (
        'access_token=""' in set_cookie
        or "Max-Age=0" in set_cookie
        or "Expires=" in set_cookie
    ), f"Cookies not cleared — Set-Cookie: {set_cookie}"


# ---------------------------------------------------------------------------
# H-05: Account enumeration protection
# ---------------------------------------------------------------------------

class TestAccountEnumerationProtection:
    """Verify login endpoint does not leak whether an email address is registered."""

    def test_unknown_email_returns_generic_error(self, client):
        """Attempting login with a non-existent email must return 401 with generic message."""
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePassword1!"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_wrong_password_returns_generic_error(self, client, sample_user, test_db):
        """Attempting login with wrong password returns 401 with same generic message."""
        import bcrypt as _bcrypt
        salt = _bcrypt.gensalt()
        sample_user.password_hash = _bcrypt.hashpw(b"CorrectPass1!", salt).decode("utf-8")
        test_db.commit()

        response = client.post("/api/auth/login", json={
            "email": sample_user.email,
            "password": "WrongPass999!"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_google_oauth_account_returns_generic_error(self, client, test_db):
        """Attempting password login on a Google-OAuth-only account must return the SAME
        generic message as an unknown email — prevents enumeration via auth-method disclosure."""
        import datetime, pytz
        from apps.backend.models import User, UserRole

        oauth_user = User(
            email="google_only@example.com",
            password_hash="google-oauth",
            full_name="Google User",
            role=UserRole.PARENT,
            country="NG",
            created_at=datetime.datetime.now(pytz.UTC),
        )
        test_db.add(oauth_user)
        test_db.commit()

        response = client.post("/api/auth/login", json={
            "email": "google_only@example.com",
            "password": "AnyPassword1!"
        })
        assert response.status_code == 401
        # Must be IDENTICAL to the message returned for unknown emails
        assert response.json()["detail"] == "Invalid email or password", (
            "Google OAuth account must not reveal its existence via a distinct error message"
        )


# ---------------------------------------------------------------------------
# H-08: str(e) must not leak in HTTPException detail fields
# ---------------------------------------------------------------------------

class TestExceptionDetailSanitization:
    """Verify that unexpected internal errors never expose str(e) in HTTP responses."""

    def test_login_db_error_does_not_leak_exception(self, client):
        """A DB failure during login must return a generic 500, not the exception string."""
        from unittest.mock import patch, MagicMock

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
        from unittest.mock import patch

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
        from unittest.mock import patch

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


# ---------------------------------------------------------------------------
# H-24: Suspended users must be blocked by get_current_active_user
# ---------------------------------------------------------------------------

class TestSuspendedUserAuthBypass:
    """Verify that a suspended user cannot access protected endpoints."""

    def _make_token(self, user_id: int) -> str:
        """Mint a valid JWT for the given user_id using the test secret."""
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        return pyjwt.encode(payload, "test_jwt_secret", algorithm="HS256")

    def test_active_user_can_access_protected_endpoint(self, client, sample_user):
        """Baseline: a non-suspended user with a valid token gets through."""
        token = self._make_token(sample_user.user_id)
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        # 200 means the dependency chain passed; any other 4xx would indicate
        # the endpoint itself requires something extra — we only care it isn't 403.
        assert response.status_code != 403, (
            "Active user should not receive 403 from get_current_active_user"
        )

    def test_suspended_user_receives_403(self, client, sample_user, test_db):
        """A user with is_suspended=1 must receive 403 on every protected endpoint."""
        sample_user.is_suspended = 1
        test_db.commit()

        token = self._make_token(sample_user.user_id)
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Account suspended"

    def test_suspended_user_unblocked_after_unsuspend(self, client, sample_user, test_db):
        """After clearing is_suspended the user can authenticate again."""
        # Suspend then re-activate
        sample_user.is_suspended = 1
        test_db.commit()
        sample_user.is_suspended = 0
        test_db.commit()

        token = self._make_token(sample_user.user_id)
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code != 403, (
            "Re-activated user must not receive 403 from get_current_active_user"
        )
