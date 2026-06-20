"""
Tests for TokenService — JWT lifecycle: token creation, refresh rotation,
blacklisting, and blacklist checks.

Covers the security-critical path extracted by AWD-M-108.  DB is mocked
throughout; crypto is exercised end-to-end using the dev-secret fallback so we
assert payload shape and expiry without hitting a real JWT service.

Filed as AWD-M-265.
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import jwt
import pytest

from apps.backend.services.token_service import TokenService, _build_user_response
from apps.backend.models import UserRole
from apps.backend.schemas.users import AuthResponse, UserResponse
from apps.backend.dependencies import get_jwt_secret_key, get_jwt_algorithm

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user(**overrides):
    """Return a Mock that satisfies the field access patterns used in token_service."""
    defaults = {
        "user_id": 1,
        "email": "test@awade.ng",
        "full_name": "Test User",
        "role": UserRole.EDUCATOR,
        "country": "Nigeria",
        "region": None,
        "school_name": None,
        "subjects": None,
        "grade_levels": None,
        "languages_spoken": None,
        "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "last_login": None,
    }
    defaults.update(overrides)
    user = Mock()
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


def _decode(token: str) -> dict:
    return jwt.decode(token, get_jwt_secret_key(), algorithms=[get_jwt_algorithm()])


def _make_svc() -> "TokenService":
    """Return a TokenService backed by a MagicMock DB.

    Used by tests that exercise crypto/env-var paths only and have no need
    for a real database session.
    """
    return TokenService(MagicMock())


def _make_refresh_jwt(sub: str = "1", token_type: str = "refresh", include_jti: bool = True) -> str:
    payload: dict = {
        "sub": sub,
        "email": "test@awade.ng",
        "type": token_type,
        "exp": datetime.now(timezone.utc) + timedelta(days=7),
    }
    if include_jti:
        payload["jti"] = "test-jti-abc123"
    return jwt.encode(payload, get_jwt_secret_key(), algorithm=get_jwt_algorithm())


# ---------------------------------------------------------------------------
# _build_user_response (module-level helper)
# ---------------------------------------------------------------------------

class TestBuildUserResponseM265:
    def test_returns_user_response_instance(self):
        user = _make_user()
        result = _build_user_response(user)
        assert isinstance(result, UserResponse)

    def test_maps_core_fields(self):
        user = _make_user(user_id=7, email="u@awade.ng", full_name="Ada")
        result = _build_user_response(user)
        assert result.user_id == 7
        assert result.email == "u@awade.ng"
        assert result.full_name == "Ada"
        assert result.role == UserRole.EDUCATOR.value

    def test_subjects_none_returns_none(self):
        user = _make_user(subjects=None)
        assert _build_user_response(user).subjects is None

    def test_subjects_valid_json_parsed(self):
        user = _make_user(subjects=json.dumps(["Math", "English"]))
        assert _build_user_response(user).subjects == ["Math", "English"]

    def test_subjects_malformed_json_returns_none(self):
        user = _make_user(subjects="not-json")
        assert _build_user_response(user).subjects is None

    def test_grade_levels_none_returns_none(self):
        user = _make_user(grade_levels=None)
        assert _build_user_response(user).grade_levels is None

    def test_grade_levels_valid_json_parsed(self):
        user = _make_user(grade_levels=json.dumps(["JSS1", "JSS2"]))
        assert _build_user_response(user).grade_levels == ["JSS1", "JSS2"]

    def test_grade_levels_malformed_json_returns_none(self):
        user = _make_user(grade_levels="{bad json}")
        assert _build_user_response(user).grade_levels is None


# ---------------------------------------------------------------------------
# TokenService.create_access_token
# ---------------------------------------------------------------------------

class TestCreateAccessTokenM265:
    def test_returns_string(self):
        svc = _make_svc()
        token = svc.create_access_token({"sub": "1", "email": "u@awade.ng"})
        assert isinstance(token, str)
        assert len(token) > 0

    def test_type_claim_is_access(self):
        svc = _make_svc()
        token = svc.create_access_token({"sub": "1"})
        payload = _decode(token)
        assert payload["type"] == "access"

    def test_exp_claim_is_approximately_60_minutes_out(self):
        svc = _make_svc()
        before = datetime.now(timezone.utc)
        token = svc.create_access_token({"sub": "1"})
        after = datetime.now(timezone.utc)
        payload = _decode(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        assert before + timedelta(minutes=59) < exp < after + timedelta(minutes=61)

    def test_sub_claim_preserved(self):
        svc = _make_svc()
        token = svc.create_access_token({"sub": "42", "email": "u@awade.ng"})
        assert _decode(token)["sub"] == "42"

    def test_original_data_dict_not_mutated(self):
        svc = _make_svc()
        data = {"sub": "1"}
        svc.create_access_token(data)
        assert "exp" not in data
        assert "type" not in data

    def test_env_var_overrides_expiry(self, monkeypatch):
        monkeypatch.setenv("JWT_EXPIRES_MINUTES", "30")
        svc = _make_svc()
        before = datetime.now(timezone.utc)
        token = svc.create_access_token({"sub": "1"})
        after = datetime.now(timezone.utc)
        exp = datetime.fromtimestamp(_decode(token)["exp"], tz=timezone.utc)
        assert before + timedelta(minutes=29) < exp < after + timedelta(minutes=31)


# ---------------------------------------------------------------------------
# TokenService.create_refresh_token
# ---------------------------------------------------------------------------

class TestCreateRefreshTokenM265:
    def test_returns_string(self):
        svc = _make_svc()
        token = svc.create_refresh_token({"sub": "1"})
        assert isinstance(token, str)

    def test_type_claim_is_refresh(self):
        svc = _make_svc()
        payload = _decode(svc.create_refresh_token({"sub": "1"}))
        assert payload["type"] == "refresh"

    def test_exp_claim_is_approximately_7_days_out(self):
        svc = _make_svc()
        before = datetime.now(timezone.utc)
        token = svc.create_refresh_token({"sub": "1"})
        after = datetime.now(timezone.utc)
        exp = datetime.fromtimestamp(_decode(token)["exp"], tz=timezone.utc)
        assert before + timedelta(days=6, hours=23) < exp < after + timedelta(days=7, hours=1)

    def test_jti_claim_present_and_non_empty(self):
        svc = _make_svc()
        payload = _decode(svc.create_refresh_token({"sub": "1"}))
        assert "jti" in payload
        assert payload["jti"]

    def test_consecutive_tokens_have_unique_jtis(self):
        svc = _make_svc()
        p1 = _decode(svc.create_refresh_token({"sub": "1"}))
        p2 = _decode(svc.create_refresh_token({"sub": "1"}))
        assert p1["jti"] != p2["jti"]

    def test_original_data_dict_not_mutated(self):
        svc = _make_svc()
        data = {"sub": "1"}
        svc.create_refresh_token(data)
        assert "jti" not in data
        assert "type" not in data


# ---------------------------------------------------------------------------
# TokenService.refresh_access_token
# ---------------------------------------------------------------------------

class TestRefreshAccessTokenM265:
    def _make_service_with_user(self, user):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = user
        return TokenService(db)

    def test_happy_path_returns_auth_response_and_new_refresh_token(self):
        user = _make_user()
        svc = self._make_service_with_user(user)
        refresh_token = _make_refresh_jwt(sub=str(user.user_id))
        auth, new_refresh = asyncio.run(
            svc.refresh_access_token(refresh_token, redis_pool=None)
        )
        assert isinstance(auth, AuthResponse)
        assert isinstance(new_refresh, str)
        assert _decode(new_refresh)["type"] == "refresh"

    def test_happy_path_new_access_token_type(self):
        user = _make_user()
        svc = self._make_service_with_user(user)
        refresh_token = _make_refresh_jwt(sub=str(user.user_id))
        auth, _ = asyncio.run(svc.refresh_access_token(refresh_token, redis_pool=None))
        assert _decode(auth.access_token)["type"] == "access"

    def test_wrong_token_type_raises_401(self):
        user = _make_user()
        svc = self._make_service_with_user(user)
        access_token = _make_refresh_jwt(sub="1", token_type="access")
        with pytest.raises(Exception) as exc_info:
            asyncio.run(svc.refresh_access_token(access_token, redis_pool=None))
        assert exc_info.value.status_code == 401
        assert "Invalid token type" in exc_info.value.detail

    def test_blacklisted_token_raises_401(self):
        user = _make_user()
        svc = self._make_service_with_user(user)
        refresh_token = _make_refresh_jwt(sub="1")
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        with pytest.raises(Exception) as exc_info:
            asyncio.run(svc.refresh_access_token(refresh_token, redis_pool=mock_redis))
        assert exc_info.value.status_code == 401
        assert "revoked" in exc_info.value.detail

    def test_user_not_found_raises_401(self):
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        svc = TokenService(db)
        refresh_token = _make_refresh_jwt(sub="999")
        with pytest.raises(Exception) as exc_info:
            asyncio.run(svc.refresh_access_token(refresh_token, redis_pool=None))
        assert exc_info.value.status_code == 401

    def test_expired_jwt_raises_401(self):
        db = MagicMock()
        svc = TokenService(db)
        expired = jwt.encode(
            {"sub": "1", "type": "refresh", "exp": datetime(2000, 1, 1, tzinfo=timezone.utc)},
            get_jwt_secret_key(),
            algorithm=get_jwt_algorithm(),
        )
        with pytest.raises(Exception) as exc_info:
            asyncio.run(svc.refresh_access_token(expired, redis_pool=None))
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_invalid_jwt_raises_401(self):
        db = MagicMock()
        svc = TokenService(db)
        with pytest.raises(Exception) as exc_info:
            asyncio.run(svc.refresh_access_token("not.a.jwt", redis_pool=None))
        assert exc_info.value.status_code == 401

    def test_db_error_raises_500(self):
        db = MagicMock()
        db.query.side_effect = RuntimeError("DB gone")
        svc = TokenService(db)
        refresh_token = _make_refresh_jwt(sub="1")
        with pytest.raises(Exception) as exc_info:
            asyncio.run(svc.refresh_access_token(refresh_token, redis_pool=None))
        assert exc_info.value.status_code == 500


# ---------------------------------------------------------------------------
# TokenService.blacklist_refresh_token
# ---------------------------------------------------------------------------

class TestBlacklistRefreshTokenM265:
    def test_happy_path_calls_setex_with_correct_key(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt()
        payload = _decode(token)
        jti = payload["jti"]
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        asyncio.run(svc.blacklist_refresh_token(token, mock_redis))
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]
        assert call_args[0] == f"blacklist:{jti}"
        assert isinstance(call_args[1], int) and call_args[1] > 0
        assert call_args[2] == "true"

    def test_no_jti_in_payload_skips_redis(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt(include_jti=False)
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        asyncio.run(svc.blacklist_refresh_token(token, mock_redis))
        mock_redis.setex.assert_not_called()

    def test_already_expired_token_skips_redis(self):
        db = MagicMock()
        svc = TokenService(db)
        expired_payload = {
            "sub": "1",
            "type": "refresh",
            "jti": "stale-jti",
            "exp": 1,
        }
        # encode without verifying expiry so we can create an expired token
        expired_token = jwt.encode(expired_payload, get_jwt_secret_key(), algorithm=get_jwt_algorithm())
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock()
        # patch decode to return the raw payload (otherwise jwt.decode raises ExpiredSignatureError)
        with patch("apps.backend.services.token_service.jwt.decode", return_value=expired_payload):
            asyncio.run(svc.blacklist_refresh_token(expired_token, mock_redis))
        mock_redis.setex.assert_not_called()

    def test_redis_error_does_not_raise(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt()
        mock_redis = AsyncMock()
        mock_redis.setex = AsyncMock(side_effect=Exception("Redis down"))
        asyncio.run(svc.blacklist_refresh_token(token, mock_redis))


# ---------------------------------------------------------------------------
# TokenService.is_refresh_token_blacklisted
# ---------------------------------------------------------------------------

class TestIsRefreshTokenBlacklistedM265:
    def test_redis_none_returns_false_and_warns(self):
        db = MagicMock()
        svc = TokenService(db)
        with patch("apps.backend.services.token_service.logger") as mock_log:
            result = asyncio.run(svc.is_refresh_token_blacklisted("any.token", redis_pool=None))
        assert result is False
        mock_log.warning.assert_called_once()
        assert "Redis unavailable" in mock_log.warning.call_args[0][0]

    def test_not_blacklisted_returns_false(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt()
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        result = asyncio.run(svc.is_refresh_token_blacklisted(token, mock_redis))
        assert not result

    def test_blacklisted_returns_true(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt()
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)
        result = asyncio.run(svc.is_refresh_token_blacklisted(token, mock_redis))
        assert result

    def test_no_jti_in_payload_returns_false(self):
        db = MagicMock()
        svc = TokenService(db)
        fake_payload = {"sub": "1", "type": "refresh"}
        mock_redis = AsyncMock()
        with patch("apps.backend.services.token_service.jwt.decode", return_value=fake_payload):
            result = asyncio.run(svc.is_refresh_token_blacklisted("fake.token", mock_redis))
        assert result is False
        mock_redis.exists.assert_not_called()

    def test_redis_exception_returns_false(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt()
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(side_effect=Exception("connection reset"))
        result = asyncio.run(svc.is_refresh_token_blacklisted(token, mock_redis))
        assert result is False

    def test_correct_redis_key_pattern_used(self):
        db = MagicMock()
        svc = TokenService(db)
        token = _make_refresh_jwt()
        jti = _decode(token)["jti"]
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=0)
        asyncio.run(svc.is_refresh_token_blacklisted(token, mock_redis))
        call_key = mock_redis.exists.call_args[0][0]
        assert call_key == f"blacklist:{jti}"
