"""
Tests for AWD-H-68: real password-reset token storage and validation.

These tests exercise the full HTTP layer (via TestClient) to ensure:
  - request_password_reset() stores a SHA-256 token hash + 1-hour expiry on the user.
  - reset_password() accepts the correct raw token and updates the password.
  - Expired tokens are rejected with HTTP 400.
  - Invalid (unknown) tokens are rejected with HTTP 400.
  - Enumeration guard: forgot-password always returns the same response regardless
    of whether the email exists.
  - Token is cleared after a successful reset (replay prevention).
"""

import hashlib
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.models import Base, User, UserRole
from apps.backend.services.auth_service import AuthService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Enable FK enforcement so cascades are exercised.
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def _make_user(session, email: str = "user@example.com", password_hash: str = "hashed") -> User:
    user = User(
        full_name="Test User",
        email=email,
        password_hash=password_hash,
        role=UserRole.EDUCATOR,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def db_session():
    engine = _make_engine()
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def http_client(db_session):
    """TestClient wired to the in-memory SQLite DB."""
    def _override_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Unit-level tests (AuthService directly, no HTTP)
# ---------------------------------------------------------------------------

class TestRequestPasswordResetUnit:
    """AuthService.request_password_reset() stores token hash + expiry."""

    def test_stores_token_hash_on_valid_email(self, db_session):
        user = _make_user(db_session)
        service = AuthService(db_session)

        result = service.request_password_reset(user.email)

        assert result == {"message": "If the email exists, a password reset link has been sent"}
        db_session.refresh(user)
        assert user.password_reset_token is not None, "Token hash must be stored"
        assert len(user.password_reset_token) == 64, "SHA-256 hex digest is 64 chars"
        assert user.password_reset_expires is not None, "Expiry must be set"
        # Expiry should be ~1 hour in the future (allow 5 s clock drift).
        now = datetime.now(timezone.utc)
        assert user.password_reset_expires.replace(tzinfo=timezone.utc) > now + timedelta(minutes=59)

    def test_enumeration_guard_on_unknown_email(self, db_session):
        service = AuthService(db_session)
        result = service.request_password_reset("nobody@example.com")
        # Same message — caller cannot distinguish existing from non-existing.
        assert result == {"message": "If the email exists, a password reset link has been sent"}

    def test_does_not_store_raw_token(self, db_session):
        """The stored value must be a SHA-256 hex digest, not the raw URL-safe token."""
        import re
        user = _make_user(db_session)
        service = AuthService(db_session)
        service.request_password_reset(user.email)
        db_session.refresh(user)
        stored = user.password_reset_token
        # A raw token_urlsafe(32) is ~43 chars (base64url); a SHA-256 hex is 64 hex chars.
        assert re.fullmatch(r"[0-9a-f]{64}", stored), (
            f"Stored token must be a 64-char hex SHA-256 digest, got: {stored!r}"
        )


class TestResetPasswordUnit:
    """AuthService.reset_password() validates token and updates password."""

    def _generate_token_for(self, service: AuthService, db_session, user: User):
        """Helper: store a valid reset token on the user and return the raw token."""
        import secrets
        raw = secrets.token_urlsafe(32)
        user.password_reset_token = AuthService._hash_reset_token(raw)
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db_session.commit()
        return raw

    def test_valid_token_resets_password(self, db_session):
        import bcrypt
        user = _make_user(db_session)
        service = AuthService(db_session)
        raw = self._generate_token_for(service, db_session, user)

        result = service.reset_password(raw, "NewPassword123!")

        assert result == {"message": "Password reset successfully"}
        db_session.refresh(user)
        # Password hash must have been updated.
        assert bcrypt.checkpw(b"NewPassword123!", user.password_hash.encode())

    def test_valid_token_is_cleared_after_reset(self, db_session):
        """Replay protection: token columns must be NULL after a successful reset."""
        user = _make_user(db_session)
        service = AuthService(db_session)
        raw = self._generate_token_for(service, db_session, user)

        service.reset_password(raw, "NewPassword123!")

        db_session.refresh(user)
        assert user.password_reset_token is None
        assert user.password_reset_expires is None

    def test_expired_token_rejected(self, db_session):
        """Token past its expiry window returns HTTP 400."""
        from fastapi import HTTPException
        user = _make_user(db_session)
        service = AuthService(db_session)

        import secrets
        raw = secrets.token_urlsafe(32)
        user.password_reset_token = AuthService._hash_reset_token(raw)
        # Set expiry in the past.
        user.password_reset_expires = datetime.now(timezone.utc) - timedelta(minutes=1)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            service.reset_password(raw, "NewPassword123!")
        assert exc_info.value.status_code == 400
        assert "expired" in exc_info.value.detail.lower() or "invalid" in exc_info.value.detail.lower()

    def test_invalid_token_rejected(self, db_session):
        """An unrecognised token string returns HTTP 400."""
        from fastapi import HTTPException
        _make_user(db_session)
        service = AuthService(db_session)

        with pytest.raises(HTTPException) as exc_info:
            service.reset_password("completelyWrongToken", "NewPassword123!")
        assert exc_info.value.status_code == 400

    def test_replay_rejected_after_successful_reset(self, db_session):
        """Re-using the same raw token after a successful reset must fail."""
        from fastapi import HTTPException
        user = _make_user(db_session)
        service = AuthService(db_session)
        raw = self._generate_token_for(service, db_session, user)

        service.reset_password(raw, "NewPassword123!")

        with pytest.raises(HTTPException) as exc_info:
            service.reset_password(raw, "AnotherPassword456!")
        assert exc_info.value.status_code == 400


# ---------------------------------------------------------------------------
# HTTP-layer tests
# ---------------------------------------------------------------------------

class TestForgotPasswordHTTP:
    def test_returns_200_for_existing_email(self, http_client, db_session):
        _make_user(db_session, email="known@example.com")
        resp = http_client.post("/api/auth/forgot-password", json={"email": "known@example.com"})
        assert resp.status_code == 200
        assert "password reset" in resp.json()["message"].lower()

    def test_returns_200_for_unknown_email(self, http_client):
        """Enumeration guard: same 200 for a non-existent email."""
        resp = http_client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
        assert resp.status_code == 200

    def test_returns_422_for_invalid_email(self, http_client):
        resp = http_client.post("/api/auth/forgot-password", json={"email": "not-an-email"})
        assert resp.status_code == 422

    def test_returns_422_for_missing_email(self, http_client):
        resp = http_client.post("/api/auth/forgot-password", json={})
        assert resp.status_code == 422


class TestResetPasswordHTTP:
    def _plant_token(self, db_session, email: str = "user@example.com"):
        """Create a user with a live reset token; return (user, raw_token)."""
        import secrets
        user = _make_user(db_session, email=email)
        raw = secrets.token_urlsafe(32)
        user.password_reset_token = AuthService._hash_reset_token(raw)
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        db_session.commit()
        return user, raw

    def test_valid_token_returns_200(self, http_client, db_session):
        _user, raw = self._plant_token(db_session)
        resp = http_client.post(
            "/api/auth/reset-password",
            json={"token": raw, "new_password": "ValidPass123!"},
        )
        assert resp.status_code == 200
        assert resp.json() == {"message": "Password reset successfully"}

    def test_invalid_token_returns_400(self, http_client, db_session):
        _make_user(db_session)
        resp = http_client.post(
            "/api/auth/reset-password",
            json={"token": "bad-token", "new_password": "ValidPass123!"},
        )
        assert resp.status_code == 400

    def test_short_password_returns_422(self, http_client, db_session):
        _user, raw = self._plant_token(db_session, email="u2@example.com")
        resp = http_client.post(
            "/api/auth/reset-password",
            json={"token": raw, "new_password": "short"},
        )
        assert resp.status_code == 422

    def test_returns_422_for_missing_fields(self, http_client):
        resp = http_client.post("/api/auth/reset-password", json={})
        assert resp.status_code == 422
