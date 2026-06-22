"""Shared helpers for test_users_*.py split files (AWD-M-221)."""

import jwt
from datetime import datetime, timedelta, timezone

from apps.backend.models import User
from apps.backend.dependencies import get_jwt_secret_key, get_jwt_algorithm


def _make_token(user: User) -> str:
    """Mint a valid JWT for a test user (matches dependencies.py logic)."""
    payload = {
        "sub": str(user.user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, get_jwt_secret_key(), algorithm=get_jwt_algorithm())


def _auth(user: User) -> dict:
    return {"Authorization": f"Bearer {_make_token(user)}"}
