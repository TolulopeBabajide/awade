"""
Tests for AuthService and TokenService.

Split from test_services.py (AWD-M-110) — was 656 lines across 7 classes.
Covers: JWT payload construction, password hashing/verification, Google OAuth,
role whitelist enforcement, delegation contracts, and Redis error handling.

Author: Tolulope Babajide
"""

import os
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from fastapi import HTTPException

import asyncio
import requests as requests_lib

from services.auth_service import AuthService, _SELF_REGISTERABLE_ROLES
from services.token_service import TokenService
from models import User, UserRole
from schemas.users import UserCreate, UserLogin


class TestAuthService:
    """Test authentication service."""

    def test_auth_service_initialization(self, test_db):
        """Test AuthService initialization."""
        service = AuthService(test_db)
        assert service.db == test_db

    def test_self_registerable_roles_constant(self):
        """AWD-M-105: _SELF_REGISTERABLE_ROLES is a single module-level frozenset
        containing exactly PARENT and EDUCATOR — no more, no less."""

        # Must be a frozenset (immutable — cannot be mutated by accident)
        assert isinstance(_SELF_REGISTERABLE_ROLES, frozenset), (
            "_SELF_REGISTERABLE_ROLES must be a frozenset to prevent accidental mutation"
        )

        # Must contain exactly the two self-registerable roles.
        # Use value-based comparison to avoid cross-module enum identity failures
        # (conftest.py adds both repo root and apps/backend to sys.path, producing
        # two distinct UserRole enum classes that are not == even for same members).
        assert {r.value for r in _SELF_REGISTERABLE_ROLES} == {
            UserRole.PARENT.value, UserRole.EDUCATOR.value
        }, "_SELF_REGISTERABLE_ROLES must contain exactly PARENT and EDUCATOR"

        # ADMIN and SUPER_ADMIN must NOT be in the set.
        # Use value-based comparison — same cross-module identity issue as above.
        assert not any(r.value == UserRole.ADMIN.value for r in _SELF_REGISTERABLE_ROLES)
        assert not any(r.value == UserRole.SUPER_ADMIN.value for r in _SELF_REGISTERABLE_ROLES)

    def test_build_token_payload_returns_sub_and_email(self, test_db):
        """AWD-M-109 / AWD-M-108: _build_token_payload must return a dict with 'sub' and 'email'.
        Delegated to TokenService as part of the auth/token split."""
        service = TokenService(test_db)
        user = Mock(spec=["user_id", "email"])
        user.user_id = 42
        user.email = "tolu@example.com"

        payload = service._build_token_payload(user)

        assert payload == {"sub": "42", "email": "tolu@example.com"}, (
            "_build_token_payload must return {'sub': str(user.user_id), 'email': user.email}"
        )

    def test_build_token_payload_sub_is_string(self, test_db):
        """AWD-M-109 / AWD-M-108: 'sub' claim must always be a str, not an int — JWT spec requires string."""
        service = TokenService(test_db)
        user = Mock(spec=["user_id", "email"])
        user.user_id = 99
        user.email = "test@awade.ng"

        payload = service._build_token_payload(user)

        assert isinstance(payload["sub"], str), (
            "'sub' must be str(user.user_id) — integers are not valid JWT subject claims"
        )
        assert payload["sub"] == "99"

    def test_build_token_payload_called_by_authenticate_user(self, test_db):
        """AWD-M-109: authenticate_user must delegate payload construction to _build_token_payload."""
        service = AuthService(test_db)

        # Register a real user first so authenticate_user can find one
        user_data = UserCreate(
            email="payload_delegate@example.com",
            password="ValidPass1!",
            full_name="Payload Test",
            role=UserRole.EDUCATOR,
            country="NG",
        )
        service.register_user(user_data)

        # AWD-M-108: _build_token_payload is now on service.token_service (TokenService)
        with patch.object(service.token_service, "_build_token_payload", wraps=service.token_service._build_token_payload) as mock_build:
            login_data = UserLogin(email="payload_delegate@example.com", password="ValidPass1!")
            service.authenticate_user(login_data)

        assert mock_build.call_count == 1, (
            "authenticate_user must call token_service._build_token_payload exactly once"
        )

    def test_password_validation(self, test_db):
        """Test password validation."""
        service = AuthService(test_db)

        # Test valid password
        assert service.get_password_min_length() >= 8

        # Test password hashing
        password = "test_password_123"
        hashed = service._hash_password(password)
        assert hashed != password
        assert service._verify_password(password, hashed)

    @patch('services.auth_service.requests.get')
    def test_google_token_verification(self, mock_get, test_db):
        """Test Google OAuth token verification."""
        service = AuthService(test_db)

        # Mock successful Google response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "aud": "test_client_id",
            "email": "test@example.com",
            "name": "Test User"
        }
        mock_get.return_value = mock_response

        # Mock environment variable
        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test_client_id'}):
            result = service.verify_google_token("test_token")
            assert result["email"] == "test@example.com"
            assert result["name"] == "Test User"

    def test_google_token_verification_failure(self, test_db):
        """Test Google OAuth token verification failure."""
        service = AuthService(test_db)

        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test_client_id'}):
            with patch('services.auth_service.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 401
                mock_get.return_value = mock_response

                with pytest.raises(HTTPException) as exc_info:
                    service.verify_google_token("invalid_token")
                assert exc_info.value.status_code == 401

    def test_google_token_request_timeout_returns_503(self, test_db):
        """AWD-M-103: requests.get timeout must return 503, not stall worker."""
        service = AuthService(test_db)

        with patch.dict('os.environ', {'GOOGLE_CLIENT_ID': 'test_client_id'}):
            with patch('services.auth_service.requests.get') as mock_get:
                mock_get.side_effect = requests_lib.exceptions.Timeout()

                with pytest.raises(HTTPException) as exc_info:
                    service.verify_google_token("any_token")

        assert exc_info.value.status_code == 503
        assert "temporarily unavailable" in exc_info.value.detail.lower()
        # Must not leak internal details
        assert "timeout" not in exc_info.value.detail.lower()

    def test_google_token_unconfigured_does_not_leak_env_var_name(self, test_db):
        """AWD-H-72: 500 response must not reveal GOOGLE_CLIENT_ID env var name."""
        service = AuthService(test_db)

        # Ensure the env var is absent so get_google_client_id() returns ""
        with patch.dict('os.environ', {}, clear=False):
            os.environ.pop('GOOGLE_CLIENT_ID', None)
            with pytest.raises(HTTPException) as exc_info:
                service.verify_google_token("any_token")

        assert exc_info.value.status_code == 500
        detail = exc_info.value.detail
        # Generic message — must not reveal the internal env var name
        assert "GOOGLE_CLIENT_ID" not in detail
        assert "environment variable" not in detail
        assert "Please contact support" in detail

    def test_register_user_cannot_self_elevate_to_admin(self, test_db):
        """AWD-H-74: register_user must coerce ADMIN/SUPER_ADMIN roles to PARENT."""

        service = AuthService(test_db)

        for elevated_role in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
            payload = UserCreate(
                email=f"attacker_{elevated_role.value}@example.com",
                password="ValidPassword123!",
                full_name="Attacker",
                role=elevated_role,
                country="NG",
            )
            auth_response, _refresh = service.register_user(payload)
            assert auth_response.user.role == UserRole.PARENT.value, (
                f"register_user must coerce role={elevated_role.value} to PARENT, "
                f"got {auth_response.user.role}"
            )

    def test_register_user_delegates_hashing_to_hash_password(self, test_db):
        """AWD-M-106: register_user must call self._hash_password() — not inline bcrypt.

        Verifies that there is a single hashing path: any change to bcrypt work factor
        or encoding in _hash_password() automatically applies to registration too.
        """

        service = AuthService(test_db)
        payload = UserCreate(
            email="hash_delegation_test@example.com",
            password="SecurePass999!",
            full_name="Hash Test",
            role=UserRole.PARENT,
            country="NG",
        )

        with patch.object(service, "_hash_password", wraps=service._hash_password) as mock_hash:
            auth_response, _ = service.register_user(payload)
            mock_hash.assert_called_once_with(payload.password)

        # The stored hash must be verifiable — confirms the delegation produced a real hash
        db_user = test_db.query(__import__("models", fromlist=["User"]).User).filter_by(
            email="hash_delegation_test@example.com"
        ).first()
        assert db_user is not None
        assert service._verify_password(payload.password, db_user.password_hash)

    def test_authenticate_user_delegates_verification_to_verify_password(self, test_db):
        """AWD-M-107: authenticate_user must call self._verify_password() — not inline bcrypt.

        Verifies that there is a single verification path: any change to bcrypt work factor
        or encoding in _verify_password() automatically applies to authentication too.
        """

        service = AuthService(test_db)

        # First register a user so there is a real hashed password in the DB
        register_payload = UserCreate(
            email="verify_delegation_test@example.com",
            password="SecureVerify999!",
            full_name="Verify Test",
            role=UserRole.PARENT,
            country="NG",
        )
        service.register_user(register_payload)

        login_payload = UserLogin(
            email="verify_delegation_test@example.com",
            password="SecureVerify999!",
        )

        db_user = test_db.query(User).filter_by(
            email="verify_delegation_test@example.com"
        ).first()
        assert db_user is not None

        with patch.object(service, "_verify_password", wraps=service._verify_password) as mock_verify:
            auth_response, _ = service.authenticate_user(login_payload)
            mock_verify.assert_called_once_with(
                login_payload.password,
                db_user.password_hash,
            )

        assert auth_response.user.email == "verify_delegation_test@example.com"

    def test_register_user_delegates_user_response_to_get_current_user_profile(self, test_db):
        """AWD-M-98: register_user must build UserResponse via get_current_user_profile().

        Ensures a single JSON-parsing path with try/except guards — malformed subjects/
        grade_levels JSON in the DB cannot cause an unhandled JSONDecodeError at
        registration time.
        """

        service = AuthService(test_db)
        payload = UserCreate(
            email="profile_delegation_register@example.com",
            password="SecureProf999!",
            full_name="Profile Reg Test",
            role=UserRole.PARENT,
            country="NG",
        )

        with patch.object(
            service, "get_current_user_profile", wraps=service.get_current_user_profile
        ) as mock_profile:
            auth_response, _ = service.register_user(payload)
            mock_profile.assert_called_once()

        assert auth_response.user.email == "profile_delegation_register@example.com"

    def test_authenticate_user_delegates_user_response_to_get_current_user_profile(self, test_db):
        """AWD-M-98: authenticate_user must build UserResponse via get_current_user_profile().

        Ensures a single JSON-parsing path with try/except guards — malformed subjects/
        grade_levels JSON in the DB cannot cause an unhandled JSONDecodeError at
        login time.
        """

        service = AuthService(test_db)

        # Register first so there is a real user in the DB
        register_payload = UserCreate(
            email="profile_delegation_login@example.com",
            password="SecureProf888!",
            full_name="Profile Login Test",
            role=UserRole.PARENT,
            country="NG",
        )
        service.register_user(register_payload)

        login_payload = UserLogin(
            email="profile_delegation_login@example.com",
            password="SecureProf888!",
        )

        with patch.object(
            service, "get_current_user_profile", wraps=service.get_current_user_profile
        ) as mock_profile:
            auth_response, _ = service.authenticate_user(login_payload)
            mock_profile.assert_called_once()

        assert auth_response.user.email == "profile_delegation_login@example.com"

    def test_is_refresh_token_blacklisted_redis_error_logs_warning(self, test_db):
        """is_refresh_token_blacklisted returns False and logs a warning when
        the connected Redis pool raises an exception (AWD-L-19).
        AWD-M-108: method now lives on TokenService."""

        service = TokenService(test_db)

        # Redis pool that is present but raises on .exists()
        mock_redis = MagicMock()
        mock_redis.exists = AsyncMock(side_effect=Exception("Redis connection lost"))

        # Patch jwt.decode to return a payload with a jti so the error branch is reached
        fake_payload = {"sub": "1", "email": "u@example.com", "jti": "test-jti-abc"}

        with patch("services.token_service.jwt.decode", return_value=fake_payload), \
             patch("services.token_service.logger") as mock_logger:
            result = asyncio.run(
                service.is_refresh_token_blacklisted("fake.jwt.token", mock_redis)
            )

        assert result is False
        mock_logger.warning.assert_called_once()
        warning_msg = mock_logger.warning.call_args[0][0]
        assert "Error checking refresh token blacklist" in warning_msg
