
import pytest
import bcrypt
import jwt as pyjwt
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from apps.backend.schemas.users import _validate_full_password

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
        from apps.backend.models import User
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


# ---------------------------------------------------------------------------
# M-71: UserLogin must reject passwords > 72 bytes before reaching bcrypt
# ---------------------------------------------------------------------------

class TestUserLoginPasswordBytesValidator:
    """Verify that UserLogin.validate_password_bytes rejects passwords exceeding
    bcrypt's 72-byte input limit with HTTP 422, not HTTP 500 (AWD-M-71)."""

    # 73 ASCII chars = 73 UTF-8 bytes — just over the limit
    _OVERLONG_ASCII = "A" * 73

    # 37 two-byte UTF-8 chars = 74 bytes — multi-byte edge case
    _OVERLONG_UNICODE = "é" * 37  # é = 2 bytes each → 74 bytes total

    # 72 ASCII chars = exactly 72 bytes — boundary must be accepted
    _BOUNDARY_ASCII = "A" * 72

    def test_login_with_password_over_72_ascii_bytes_returns_422(self, client):
        """A password that is 73 ASCII bytes must be rejected at schema validation
        (HTTP 422) before the request reaches authenticate_user / bcrypt."""
        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": self._OVERLONG_ASCII},
        )
        assert response.status_code == 422, (
            f"Expected 422 for overlong ASCII password, got {response.status_code}: {response.text}"
        )
        body = response.json()
        assert "detail" in body, "422 response must include a 'detail' field"

    def test_login_with_password_over_72_utf8_bytes_returns_422(self, client):
        """A password whose UTF-8 encoding exceeds 72 bytes (multi-byte chars) must
        also be rejected with HTTP 422."""
        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": self._OVERLONG_UNICODE},
        )
        assert response.status_code == 422, (
            f"Expected 422 for overlong unicode password, got {response.status_code}: {response.text}"
        )

    def test_login_with_exactly_72_byte_password_passes_schema_validation(self, client, sample_user, test_db):
        """A password of exactly 72 ASCII bytes is within bcrypt's limit and must
        pass schema validation (the response should be 200 or 401, not 422/500)."""
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(self._BOUNDARY_ASCII.encode("utf-8"), salt).decode("utf-8")
        sample_user.password_hash = pw_hash
        test_db.commit()

        response = client.post(
            "/api/auth/login",
            json={"email": sample_user.email, "password": self._BOUNDARY_ASCII},
        )
        # Schema validation passes — should reach the auth layer (200 on success)
        assert response.status_code != 422, (
            "72-byte password must not be rejected by schema validation (AWD-M-71)"
        )
        assert response.status_code != 500, (
            "72-byte password must not trigger a bcrypt ValueError (HTTP 500)"
        )
        assert response.status_code == 200, (
            f"Expected 200 for valid 72-byte password, got {response.status_code}: {response.text}"
        )

    def test_login_overlong_password_returns_422_not_500(self, client):
        """Regression guard: the response for an overlong password must be 422, not
        500 — confirming bcrypt.checkpw is never reached with an invalid input."""
        response = client.post(
            "/api/auth/login",
            json={"email": "any@example.com", "password": "X" * 100},
        )
        assert response.status_code == 422, (
            f"Overlong password must yield 422, not {response.status_code} (AWD-M-71 regression guard)"
        )
        assert response.status_code != 500, "HTTP 500 from bcrypt ValueError must not occur (AWD-M-71)"


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
        import apps.backend.schemas.users as schemas_module
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
        import apps.backend.schemas.users as schemas_module
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
        import apps.backend.schemas.users as schemas_module
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
            "/api/auth/register",
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


# ---------------------------------------------------------------------------
# M-72: UserCreate and PasswordReset must reject passwords > 72 UTF-8 bytes
# ---------------------------------------------------------------------------

class TestUserCreatePasswordBytesValidator:
    """Verify that UserCreate.validate_password rejects passwords exceeding
    bcrypt's 72-byte input limit with HTTP 422 during registration (AWD-M-72).

    UserCreate previously checked character count against PASSWORD_MAX_LENGTH
    (default 128).  With a default of 72 bytes now enforced, a password of 73
    ASCII chars would pass character-length validation (73 <= 128) yet crash
    bcrypt.hashpw() with ValueError → HTTP 500.  The fix lowers the default
    to 72 and switches to byte-length comparison.
    """

    _OVERLONG_ASCII = "A" * 73           # 73 bytes — just over limit
    _OVERLONG_UNICODE = "é" * 37         # 74 bytes (é = 2 bytes) — multi-byte edge case
    _BOUNDARY_ASCII = "A" * 72           # exactly 72 bytes — must be accepted by schema
    _SHORT = "ValidPwd1"                 # 9 chars / 9 bytes — always passes

    _BASE_PAYLOAD = {
        "email": "newuser@example.com",
        "full_name": "Test User",
        "role": "EDUCATOR",
        "country": "NG",
    }

    def test_register_with_password_over_72_ascii_bytes_returns_422(self, client):
        """Registration with a 73-ASCII-byte password must return 422 (schema
        rejection) rather than reaching bcrypt and returning 500."""
        payload = {**self._BASE_PAYLOAD, "password": self._OVERLONG_ASCII}
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422, (
            f"Expected 422 for overlong ASCII password at /register, "
            f"got {response.status_code}: {response.text}"
        )
        assert response.status_code != 500, (
            "HTTP 500 from bcrypt ValueError must not occur (AWD-M-72)"
        )

    def test_register_with_password_over_72_utf8_bytes_returns_422(self, client):
        """Registration with a multi-byte password whose UTF-8 encoding exceeds
        72 bytes must be rejected at schema validation (HTTP 422)."""
        payload = {**self._BASE_PAYLOAD, "password": self._OVERLONG_UNICODE}
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422, (
            f"Expected 422 for overlong unicode password at /register, "
            f"got {response.status_code}: {response.text}"
        )

    def test_register_with_exactly_72_byte_password_passes_schema_validation(self, client):
        """A password of exactly 72 ASCII bytes is within bcrypt's limit and must
        pass schema validation — response should be 200 or 409 (duplicate email),
        never 422 or 500."""
        payload = {**self._BASE_PAYLOAD, "password": self._BOUNDARY_ASCII}
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code not in (422, 500), (
            f"72-byte password must not be rejected by schema or crash bcrypt "
            f"(AWD-M-72), got {response.status_code}: {response.text}"
        )

    def test_register_overlong_password_returns_422_not_500(self, client):
        """Regression guard: a password > 72 bytes must yield 422, not 500."""
        payload = {**self._BASE_PAYLOAD, "password": "X" * 100}
        response = client.post("/api/auth/register", json=payload)
        assert response.status_code == 422, (
            f"Overlong password must yield 422, not {response.status_code} (AWD-M-72 regression guard)"
        )
        assert response.status_code != 500, (
            "HTTP 500 from bcrypt ValueError must not reach the client (AWD-M-72)"
        )


class TestPasswordValidationHelpers:
    """Unit tests for the module-level helpers extracted in AWD-M-92.

    These tests exercise the helpers directly, ensuring the single source of
    truth for byte-length enforcement and the weak-password denylist is correct.
    The HTTP-layer behaviour is already covered by TestUserLoginPasswordBytesValidator
    and TestUserCreatePasswordBytesValidator above.
    """

    def test_byte_length_helper_raises_for_overlong_ascii(self):
        """Helper raises ValueError when ASCII password exceeds max_bytes."""
        from apps.backend.schemas.users import _validate_password_byte_length
        import pytest as _pytest
        with _pytest.raises(ValueError, match="too long"):
            _validate_password_byte_length("A" * 73, 72)

    def test_byte_length_helper_raises_for_overlong_multibyte(self):
        """Helper raises ValueError when multi-byte chars push encoding over the limit."""
        from apps.backend.schemas.users import _validate_password_byte_length
        import pytest as _pytest
        # "é" encodes to 2 UTF-8 bytes; 37 copies → 74 bytes > 72
        with _pytest.raises(ValueError, match="too long"):
            _validate_password_byte_length("é" * 37, 72)

    def test_byte_length_helper_passes_at_exact_limit(self):
        """Helper does not raise when byte length equals max_bytes exactly."""
        from apps.backend.schemas.users import _validate_password_byte_length
        _validate_password_byte_length("A" * 72, 72)  # must not raise

    def test_byte_length_helper_passes_below_limit(self):
        """Helper does not raise for a short password."""
        from apps.backend.schemas.users import _validate_password_byte_length
        _validate_password_byte_length("SecurePass1!", 72)  # must not raise

    def test_weak_password_helper_raises_for_denylist_entry(self):
        """Helper raises ValueError for each password on the denylist."""
        from apps.backend.schemas.users import _WEAK_PASSWORDS, _validate_weak_password
        import pytest as _pytest
        for pw in _WEAK_PASSWORDS:
            with _pytest.raises(ValueError, match="too common"):
                _validate_weak_password(pw)

    def test_weak_password_helper_raises_case_insensitive(self):
        """Denylist check is case-insensitive."""
        from apps.backend.schemas.users import _validate_weak_password
        import pytest as _pytest
        with _pytest.raises(ValueError, match="too common"):
            _validate_weak_password("PASSWORD")
        with _pytest.raises(ValueError, match="too common"):
            _validate_weak_password("Admin")

    def test_weak_password_helper_passes_for_strong_password(self):
        """Helper does not raise for a strong, non-denylist password."""
        from apps.backend.schemas.users import _validate_weak_password
        _validate_weak_password("Tr0ub4dor&3")  # must not raise

    def test_weak_passwords_constant_contains_expected_entries(self):
        """_WEAK_PASSWORDS frozenset contains all originally hardcoded values."""
        from apps.backend.schemas.users import _WEAK_PASSWORDS
        expected = {"password", "123456", "qwerty", "admin", "letmein"}
        assert expected <= _WEAK_PASSWORDS, (
            f"Missing entries from _WEAK_PASSWORDS: {expected - _WEAK_PASSWORDS}"
        )


class TestValidateFullPasswordHelper:
    """Unit tests for _validate_full_password — the unified orchestrator (AWD-M-127).

    Verifies that the helper enforces all three checks (min-length, byte-ceiling,
    denylist) and returns the original string on success.  HTTP-layer coverage
    for UserCreate and PasswordReset is already present in
    TestUserCreatePasswordBytesValidator; these tests target the helper directly.
    """

    def test_raises_for_password_below_min_length(self, monkeypatch):
        """Helper raises ValueError when password is shorter than PASSWORD_MIN_LENGTH."""
        monkeypatch.setenv("PASSWORD_MIN_LENGTH", "8")
        with pytest.raises(ValueError, match="at least 8 characters"):
            _validate_full_password("short")

    def test_raises_for_password_exceeding_byte_ceiling(self, monkeypatch):
        """Helper raises ValueError when UTF-8 byte length exceeds the configured cap."""
        monkeypatch.setenv("PASSWORD_MIN_LENGTH", "8")
        monkeypatch.setenv("PASSWORD_MAX_LENGTH", "72")
        # "é" = 2 UTF-8 bytes; 37 copies → 74 bytes > 72
        with pytest.raises(ValueError, match="too long"):
            _validate_full_password("é" * 37)

    def test_raises_for_weak_password(self, monkeypatch):
        """Helper raises ValueError for a denylist entry."""
        monkeypatch.setenv("PASSWORD_MIN_LENGTH", "8")
        with pytest.raises(ValueError, match="too common"):
            _validate_full_password("password")

    def test_returns_value_for_strong_password(self, monkeypatch):
        """Helper returns the original string unchanged for a valid password."""
        monkeypatch.setenv("PASSWORD_MIN_LENGTH", "8")
        result = _validate_full_password("Tr0ub4dor&3")
        assert result == "Tr0ub4dor&3"
