"""
Tests for password byte-length validation at login and registration (AWD-M-129 split).

Covers:
- M-71: UserLogin must reject passwords > 72 bytes before reaching bcrypt
- M-72: UserCreate and PasswordReset must reject passwords > 72 UTF-8 bytes
- M-92: Module-level validation helpers (unit tests)
- M-127: _validate_full_password orchestrator (unit tests)
"""

import pytest
import bcrypt

from apps.backend.schemas.users import (
    _validate_full_password,
    _validate_password_byte_length,
    _validate_weak_password,
    _WEAK_PASSWORDS,
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
        response = client.post("/api/auth/signup", json=payload)
        assert response.status_code == 422, (
            f"Expected 422 for overlong ASCII password at /signup, "
            f"got {response.status_code}: {response.text}"
        )
        assert response.status_code != 500, (
            "HTTP 500 from bcrypt ValueError must not occur (AWD-M-72)"
        )

    def test_register_with_password_over_72_utf8_bytes_returns_422(self, client):
        """Registration with a multi-byte password whose UTF-8 encoding exceeds
        72 bytes must be rejected at schema validation (HTTP 422)."""
        payload = {**self._BASE_PAYLOAD, "password": self._OVERLONG_UNICODE}
        response = client.post("/api/auth/signup", json=payload)
        assert response.status_code == 422, (
            f"Expected 422 for overlong unicode password at /signup, "
            f"got {response.status_code}: {response.text}"
        )

    def test_register_with_exactly_72_byte_password_passes_schema_validation(self, client):
        """A password of exactly 72 ASCII bytes is within bcrypt's limit and must
        pass schema validation — response should be 200 or 409 (duplicate email),
        never 422 or 500."""
        payload = {**self._BASE_PAYLOAD, "password": self._BOUNDARY_ASCII}
        response = client.post("/api/auth/signup", json=payload)
        assert response.status_code not in (422, 500), (
            f"72-byte password must not be rejected by schema or crash bcrypt "
            f"(AWD-M-72), got {response.status_code}: {response.text}"
        )

    def test_register_overlong_password_returns_422_not_500(self, client):
        """Regression guard: a password > 72 bytes must yield 422, not 500."""
        payload = {**self._BASE_PAYLOAD, "password": "X" * 100}
        response = client.post("/api/auth/signup", json=payload)
        assert response.status_code == 422, (
            f"Overlong password must yield 422, not {response.status_code} (AWD-M-72 regression guard)"
        )
        assert response.status_code != 500, (
            "HTTP 500 from bcrypt ValueError must not reach the client (AWD-M-72)"
        )


# ---------------------------------------------------------------------------
# M-92: Module-level validation helpers (unit tests)
# ---------------------------------------------------------------------------

class TestPasswordValidationHelpers:
    """Unit tests for the module-level helpers extracted in AWD-M-92.

    These tests exercise the helpers directly, ensuring the single source of
    truth for byte-length enforcement and the weak-password denylist is correct.
    The HTTP-layer behaviour is already covered by TestUserLoginPasswordBytesValidator
    and TestUserCreatePasswordBytesValidator above.
    """

    def test_byte_length_helper_raises_for_overlong_ascii(self):
        """Helper raises ValueError when ASCII password exceeds max_bytes."""
        with pytest.raises(ValueError, match="too long"):
            _validate_password_byte_length("A" * 73, 72)

    def test_byte_length_helper_raises_for_overlong_multibyte(self):
        """Helper raises ValueError when multi-byte chars push encoding over the limit."""
        # "é" encodes to 2 UTF-8 bytes; 37 copies → 74 bytes > 72
        with pytest.raises(ValueError, match="too long"):
            _validate_password_byte_length("é" * 37, 72)

    def test_byte_length_helper_passes_at_exact_limit(self):
        """Helper does not raise when byte length equals max_bytes exactly."""
        _validate_password_byte_length("A" * 72, 72)  # must not raise

    def test_byte_length_helper_passes_below_limit(self):
        """Helper does not raise for a short password."""
        _validate_password_byte_length("SecurePass1!", 72)  # must not raise

    def test_weak_password_helper_raises_for_denylist_entry(self):
        """Helper raises ValueError for each password on the denylist."""
        for pw in _WEAK_PASSWORDS:
            with pytest.raises(ValueError, match="too common"):
                _validate_weak_password(pw)

    def test_weak_password_helper_raises_case_insensitive(self):
        """Denylist check is case-insensitive."""
        with pytest.raises(ValueError, match="too common"):
            _validate_weak_password("PASSWORD")
        with pytest.raises(ValueError, match="too common"):
            _validate_weak_password("Admin")

    def test_weak_password_helper_passes_for_strong_password(self):
        """Helper does not raise for a strong, non-denylist password."""
        _validate_weak_password("Tr0ub4dor&3")  # must not raise

    def test_weak_passwords_constant_contains_expected_entries(self):
        """_WEAK_PASSWORDS frozenset contains all originally hardcoded values."""
        expected = {"password", "123456", "qwerty", "admin", "letmein"}
        assert expected <= _WEAK_PASSWORDS, (
            f"Missing entries from _WEAK_PASSWORDS: {expected - _WEAK_PASSWORDS}"
        )


# ---------------------------------------------------------------------------
# M-127: _validate_full_password orchestrator (unit tests)
# ---------------------------------------------------------------------------

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
