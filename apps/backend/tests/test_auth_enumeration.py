"""
Tests for account enumeration protection on auth endpoints (AWD-M-129 split).

Covers:
- H-05: Login must not reveal whether an email is registered
- H-133: Registration must not reveal whether an email is already registered
- M-47: Refresh token must not reveal whether a user still exists
"""

import datetime

import bcrypt

from apps.backend.models import User, UserRole


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
        salt = bcrypt.gensalt()
        sample_user.password_hash = bcrypt.hashpw(b"CorrectPass1!", salt).decode("utf-8")
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
        oauth_user = User(
            email="google_only@example.com",
            password_hash="google-oauth",
            full_name="Google User",
            role=UserRole.PARENT,
            country="NG",
            created_at=datetime.datetime.now(datetime.timezone.utc),
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
# H-133: Registration must not reveal whether an email is already registered
# ---------------------------------------------------------------------------

class TestRegistrationEnumerationProtection:
    """Verify signup endpoint does not leak whether an email address is taken (AWD-H-133)."""

    _VALID_PAYLOAD = {
        "email": "existing@example.com",
        "password": "ValidPass1!",
        "full_name": "Test User",
        "role": "PARENT",
        "country": "NG",
    }

    def test_duplicate_email_returns_generic_error(self, client):
        """Registering an already-used email must NOT return 'Email already registered'."""
        # First registration succeeds
        client.post("/api/auth/signup", json=self._VALID_PAYLOAD)

        # Second attempt with same email
        response = client.post("/api/auth/signup", json=self._VALID_PAYLOAD)
        assert response.status_code == 400
        detail = response.json().get("detail", "")
        assert "already registered" not in detail.lower(), (
            "Registration endpoint must not reveal whether the email is taken (AWD-H-133)"
        )
        assert "registration failed" in detail.lower(), (
            f"Expected generic registration failure message, got: {detail!r}"
        )

    def test_unknown_email_registration_succeeds(self, client):
        """A fresh email not in the DB should register successfully (sanity check)."""
        payload = {**self._VALID_PAYLOAD, "email": "brand_new@example.com"}
        response = client.post("/api/auth/signup", json=payload)
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# M-47: Token refresh must not leak "User not found" (account enumeration)
# ---------------------------------------------------------------------------

class TestRefreshTokenEnumeration:
    """Verify that the refresh endpoint returns a generic error when the user
    associated with a valid refresh token no longer exists.  AWD-M-47."""

    def test_deleted_user_refresh_returns_generic_error(self, client, sample_user, test_db):
        """A valid refresh token whose user has been deleted must return 401 with
        a generic 'Invalid token' message — not 'User not found'."""
        # 1. Give sample_user a known password and log in to get a real refresh token.
        password = "TestPassword1!"
        salt = bcrypt.gensalt()
        sample_user.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
        test_db.commit()

        login_resp = client.post(
            "/api/auth/login",
            json={"email": sample_user.email, "password": password},
        )
        assert login_resp.status_code == 200, (
            f"Login failed unexpectedly: {login_resp.text}"
        )
        assert "refresh_token" in login_resp.cookies, "refresh_token cookie missing after login"

        # 2. Delete the user from the database so the next refresh hits the
        #    "user not found" branch in refresh_access_token().
        test_db.query(User).filter(User.user_id == sample_user.user_id).delete()
        test_db.commit()

        # 3. Call refresh — cookie is forwarded automatically by TestClient.
        refresh_resp = client.post("/api/auth/refresh")

        assert refresh_resp.status_code == 401
        detail = refresh_resp.json().get("detail", "")
        assert detail != "User not found", (
            "Refresh endpoint must not reveal whether a user ID existed (AWD-M-47)"
        )
        assert "Invalid token" in detail or "invalid" in detail.lower() or "authentication" in detail.lower(), (
            f"Expected a generic auth error, got: {detail!r}"
        )
