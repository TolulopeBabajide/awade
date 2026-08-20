"""JWT secret key config and cookie-fallback auth tests (AWD-M-223 split from test_security.py)."""

import asyncio
import os

import jwt as pyjwt
import pytest
from fastapi import Request
from unittest.mock import MagicMock

from apps.backend.dependencies import get_optional_current_user
from apps.backend.models import User, UserRole


def _make_token(user_id: int) -> str:
    """Mint a valid JWT for the given user_id using the test secret."""
    secret = os.getenv("JWT_SECRET_KEY", "test_jwt_secret")
    return pyjwt.encode({"sub": str(user_id)}, secret, algorithm="HS256")


class TestGetJwtSecretKey:
    """AWD-M-142: JWT dev-secret fallback must only be allowed in explicit safe environments."""

    def test_returns_env_var_when_set(self, monkeypatch):
        """When JWT_SECRET_KEY is set it is returned regardless of environment."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.setenv("JWT_SECRET_KEY", "super-strong-secret")
        monkeypatch.setenv("ENVIRONMENT", "production")
        assert get_jwt_secret_key() == "super-strong-secret"

    def test_returns_dev_secret_in_development(self, monkeypatch):
        """Missing key is tolerated in development — falls back to 'dev-secret'."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "development")
        assert get_jwt_secret_key() == "dev-secret"

    def test_returns_dev_secret_in_testing(self, monkeypatch):
        """Missing key is tolerated in testing — falls back to 'dev-secret'."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "testing")
        assert get_jwt_secret_key() == "dev-secret"

    def test_returns_dev_secret_in_test(self, monkeypatch):
        """Missing key is tolerated when ENVIRONMENT='test' — falls back to 'dev-secret'."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "test")
        assert get_jwt_secret_key() == "dev-secret"

    def test_raises_in_production_without_key(self, monkeypatch):
        """Missing JWT_SECRET_KEY in production must raise RuntimeError at call time."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            get_jwt_secret_key()

    def test_raises_when_environment_is_staging(self, monkeypatch):
        """Missing JWT_SECRET_KEY with ENVIRONMENT=staging must raise — staging is not in the safe allowlist (AWD-M-142)."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "staging")
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            get_jwt_secret_key()

    def test_raises_when_environment_is_unrecognised(self, monkeypatch):
        """Any unrecognised ENVIRONMENT value without JWT_SECRET_KEY must raise (AWD-M-142)."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "preview")
        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            get_jwt_secret_key()

    def test_staging_with_key_set_succeeds(self, monkeypatch):
        """Staging environment is fine when JWT_SECRET_KEY is explicitly provided."""
        from apps.backend.dependencies import get_jwt_secret_key
        monkeypatch.setenv("JWT_SECRET_KEY", "staging-strong-secret")
        monkeypatch.setenv("ENVIRONMENT", "staging")
        assert get_jwt_secret_key() == "staging-strong-secret"


class TestGetOptionalCurrentUserCookieFallback:
    """AWD-H-34: get_optional_current_user must fall back to the access_token
    HttpOnly cookie when no Authorization header is present.

    Before this fix the function returned None for any request without an
    Authorization header, silently treating cookie-authenticated browser
    clients as anonymous.
    """

    def test_returns_user_from_authorization_header(self, test_db):
        """Bearer token in Authorization header still resolves the user."""
        user = User(
            full_name="Header User",
            email="header@example.com",
            password_hash="x",
            role=UserRole.EDUCATOR,
            country="NG",
            region="Lagos",
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        token = _make_token(user.user_id)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {token}"}
        mock_request.cookies = {}

        result = asyncio.run(
            get_optional_current_user(request=mock_request, db=test_db)
        )
        assert result is not None
        assert result.user_id == user.user_id

    def test_returns_user_from_cookie(self, test_db):
        """Cookie-only request (no Authorization header) resolves the user."""
        user = User(
            full_name="Cookie User",
            email="cookie@example.com",
            password_hash="x",
            role=UserRole.PARENT,
            country="NG",
            region="Abuja",
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        token = _make_token(user.user_id)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.cookies = {"access_token": token}

        result = asyncio.run(
            get_optional_current_user(request=mock_request, db=test_db)
        )
        assert result is not None
        assert result.user_id == user.user_id

    def test_returns_none_for_unauthenticated_request(self, test_db):
        """No header and no cookie → returns None (not an exception)."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.cookies = {}

        result = asyncio.run(
            get_optional_current_user(request=mock_request, db=test_db)
        )
        assert result is None

    def test_returns_none_for_invalid_cookie_token(self, test_db):
        """A malformed or expired cookie token returns None without raising."""
        mock_request = MagicMock(spec=Request)
        mock_request.headers = {}
        mock_request.cookies = {"access_token": "not.a.valid.jwt"}

        result = asyncio.run(
            get_optional_current_user(request=mock_request, db=test_db)
        )
        assert result is None

    def test_header_takes_precedence_over_cookie(self, test_db):
        """When both Authorization header and cookie are present, header wins."""
        user_a = User(
            full_name="User A",
            email="usera@example.com",
            password_hash="x",
            role=UserRole.EDUCATOR,
            country="NG",
            region="Lagos",
        )
        user_b = User(
            full_name="User B",
            email="userb@example.com",
            password_hash="x",
            role=UserRole.PARENT,
            country="NG",
            region="Lagos",
        )
        test_db.add_all([user_a, user_b])
        test_db.commit()
        test_db.refresh(user_a)
        test_db.refresh(user_b)

        token_a = _make_token(user_a.user_id)
        token_b = _make_token(user_b.user_id)

        mock_request = MagicMock(spec=Request)
        mock_request.headers = {"Authorization": f"Bearer {token_a}"}
        mock_request.cookies = {"access_token": token_b}

        result = asyncio.run(
            get_optional_current_user(request=mock_request, db=test_db)
        )
        assert result is not None
        assert result.user_id == user_a.user_id, "Authorization header should take precedence over cookie"
