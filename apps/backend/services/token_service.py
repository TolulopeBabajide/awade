"""
Token Service for Awade

Handles all JWT token lifecycle operations: creation, rotation, refresh, and
blacklisting.  User-identity operations (login, register, password reset) live
in AuthService.

Extracted from AuthService per AWD-M-108 — the 400-line split threshold was
reached and the token-lifecycle concern is structurally independent.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple
import json
import logging
import os
import secrets

import jwt
from fastapi import HTTPException
from sqlalchemy.orm import Session

from apps.backend.dependencies import get_jwt_algorithm, get_jwt_secret_key
from apps.backend.models import User
from apps.backend.schemas.users import AuthResponse, UserResponse

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level helper — shared with AuthService.get_current_user_profile
# ---------------------------------------------------------------------------

def _build_user_response(user: User) -> UserResponse:
    """Build a :class:`UserResponse` from a :class:`User` ORM instance.

    Module-level so that both :class:`TokenService` (used inside
    ``refresh_access_token``) and :class:`AuthService` (exposed via
    ``get_current_user_profile``) can call the same field-mapping logic
    without circular imports.
    """
    try:
        subjects_list = json.loads(user.subjects) if user.subjects else None
    except (json.JSONDecodeError, TypeError):
        subjects_list = None

    try:
        grade_levels_list = json.loads(user.grade_levels) if user.grade_levels else None
    except (json.JSONDecodeError, TypeError):
        grade_levels_list = None

    return UserResponse(
        user_id=user.user_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        country=user.country,
        region=user.region,
        school_name=user.school_name,
        subjects=subjects_list,
        grade_levels=grade_levels_list,
        languages_spoken=user.languages_spoken,
        created_at=user.created_at,
        last_login=user.last_login,
    )


# ---------------------------------------------------------------------------
# TokenService
# ---------------------------------------------------------------------------

class TokenService:
    """Service class for JWT token lifecycle operations.

    Responsibilities:
    - Create access tokens (short-lived JWTs)
    - Create refresh tokens (long-lived JWTs with JTI for revocation)
    - Refresh an access token using a valid refresh token (rotation)
    - Blacklist a refresh token in Redis on logout
    - Check whether a refresh token's JTI is blacklisted

    User-identity concerns (Google OAuth, email/password auth, password reset)
    remain in :class:`~apps.backend.services.auth_service.AuthService`.
    """

    def __init__(self, db: Session) -> None:
        """Initialise with a database session (needed for user look-ups in refresh)."""
        self.db = db

    # ------------------------------------------------------------------
    # Configuration helpers
    # ------------------------------------------------------------------

    def _get_jwt_expires_minutes(self) -> int:
        """Return the configured access-token lifetime in minutes (default 60)."""
        return int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

    # ------------------------------------------------------------------
    # Token construction
    # ------------------------------------------------------------------

    def _build_token_payload(self, user: User) -> dict:
        """Build the JWT payload for a given user.

        Centralises the ``sub`` + ``email`` payload construction so that
        adding a new claim requires a single edit here.

        Args:
            user: The authenticated :class:`User` ORM instance.

        Returns:
            dict: Payload dict ready for :meth:`create_access_token` or
                  :meth:`create_refresh_token`.
        """
        return {"sub": str(user.user_id), "email": user.email}

    def create_access_token(self, data: dict) -> str:
        """Create a signed access token (JWT).

        Args:
            data: Claims to embed.  An ``exp`` claim and ``"type": "access"``
                  are added automatically.

        Returns:
            str: Encoded JWT string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._get_jwt_expires_minutes())
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, get_jwt_secret_key(), algorithm=get_jwt_algorithm())

    def create_refresh_token(self, data: dict) -> str:
        """Create a signed refresh token (JWT) with a unique JTI.

        The JTI is used for per-token revocation in Redis.  The token is
        valid for 7 days.

        Args:
            data: Claims to embed.  ``exp``, ``"type": "refresh"``, and
                  ``jti`` are added automatically.

        Returns:
            str: Encoded JWT string.
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=7)
        jti = secrets.token_urlsafe(16)
        to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
        return jwt.encode(to_encode, get_jwt_secret_key(), algorithm=get_jwt_algorithm())

    # ------------------------------------------------------------------
    # Token refresh (rotation)
    # ------------------------------------------------------------------

    async def refresh_access_token(
        self,
        refresh_token: str,
        redis_pool: Optional[Any] = None,
    ) -> Tuple[AuthResponse, str]:
        """Validate a refresh token and issue a new access/refresh token pair.

        Args:
            refresh_token: The existing refresh token (read from the HttpOnly cookie).
            redis_pool: Optional Redis connection for blacklist checks.

        Returns:
            Tuple of (AuthResponse, new_refresh_token_str).

        Raises:
            HTTPException 401: On invalid, expired, or revoked tokens.
            HTTPException 500: On unexpected server errors.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                get_jwt_secret_key(),
                algorithms=[get_jwt_algorithm()],
            )

            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            if await self.is_refresh_token_blacklisted(refresh_token, redis_pool):
                raise HTTPException(status_code=401, detail="Token has been revoked")

            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token payload")

            user = self.db.query(User).filter(User.user_id == int(user_id)).first()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid token")

            token_payload = self._build_token_payload(user)
            new_access_token = self.create_access_token(token_payload)
            new_refresh_token = self.create_refresh_token(token_payload)
            user_response = _build_user_response(user)

            return (
                AuthResponse(
                    access_token=new_access_token,
                    token_type="bearer",
                    user=user_response,
                ),
                new_refresh_token,
            )

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        except Exception as exc:
            if isinstance(exc, HTTPException):
                raise
            logger.error("Unexpected error during token refresh: %s", exc, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred during token refresh",
            )

    # ------------------------------------------------------------------
    # Blacklist (Redis)
    # ------------------------------------------------------------------

    async def blacklist_refresh_token(
        self, refresh_token: str, redis_pool: Any
    ) -> None:
        """Blacklist a refresh token in Redis until its natural expiry.

        Uses the token's JTI as the Redis key and the token's ``exp`` claim
        to set the TTL, so the Redis entry is self-cleaning.

        Args:
            refresh_token: The JWT refresh token to revoke.
            redis_pool: Active Redis connection.  If the token is already
                expired or lacks a JTI, the call is a no-op.
        """
        try:
            payload = jwt.decode(
                refresh_token,
                get_jwt_secret_key(),
                algorithms=[get_jwt_algorithm()],
            )
            jti = payload.get("jti")
            exp = payload.get("exp")
            if not jti or not exp:
                return

            ttl = int(exp - datetime.now(timezone.utc).timestamp())
            if ttl <= 0:
                return

            key = f"blacklist:{jti}"
            await redis_pool.setex(key, ttl, "true")

        except Exception as exc:
            logger.error("Error blacklisting token: %s", exc, exc_info=True)

    async def is_refresh_token_blacklisted(
        self, refresh_token: str, redis_pool: Any
    ) -> bool:
        """Check whether a refresh token's JTI is present in the Redis blacklist.

        Degraded mode: when ``redis_pool`` is ``None`` (Redis unavailable), the
        blacklist check is skipped and the token is treated as valid.  This is a
        deliberate fail-open trade-off — logged as a WARNING so the
        nightly-monitor surfaces the outage.
        See ``docs/agentic/mcp-circuit-breaker-policy.md §auth-service``.

        Args:
            refresh_token: The JWT refresh token to check.
            redis_pool: Active Redis connection, or ``None`` when degraded.

        Returns:
            bool: ``True`` if revoked, ``False`` if valid or Redis is unavailable.
        """
        if not redis_pool:
            logger.warning(
                "Redis unavailable — refresh token blacklist check skipped; "
                "revoked tokens may be reusable until Redis recovers (AWD-M-102)"
            )
            return False

        try:
            payload = jwt.decode(
                refresh_token,
                get_jwt_secret_key(),
                algorithms=[get_jwt_algorithm()],
            )
            jti = payload.get("jti")
            if not jti:
                return False

            key = f"blacklist:{jti}"
            return await redis_pool.exists(key)

        except Exception as exc:
            logger.warning(
                "Error checking refresh token blacklist: %s", exc, exc_info=True
            )
            return False
