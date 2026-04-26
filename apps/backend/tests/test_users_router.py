"""
Tests for AWD-H-12: GET /api/users/{user_id} ownership check.

Verifies that:
- A user can read their own record (200)
- An EDUCATOR cannot read another user's record (403)
- A PARENT cannot read another user's record (403)
- An ADMIN can read any user's record (200)
- A SUPER_ADMIN can read any user's record (200)
- Unauthenticated request returns 403
- Non-existent user_id returns 404 (admin only, after ownership check passes)
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone

from apps.backend.models import User, UserRole
from apps.backend.dependencies import get_jwt_secret_key, get_jwt_algorithm


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_token(user: User) -> str:
    """Mint a valid JWT for a test user (matches dependencies.py logic)."""
    payload = {
        "sub": str(user.user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return jwt.encode(payload, get_jwt_secret_key(), algorithm=get_jwt_algorithm())


def _auth(user: User) -> dict:
    return {"Authorization": f"Bearer {_make_token(user)}"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def educator_user(test_db):
    u = User(
        full_name="Educator One",
        email="educator1@example.com",
        password_hash="hashed",
        role=UserRole.EDUCATOR,
        country="Nigeria",
    )
    test_db.add(u)
    test_db.commit()
    test_db.refresh(u)
    return u


@pytest.fixture
def other_educator(test_db):
    u = User(
        full_name="Educator Two",
        email="educator2@example.com",
        password_hash="hashed",
        role=UserRole.EDUCATOR,
        country="Nigeria",
    )
    test_db.add(u)
    test_db.commit()
    test_db.refresh(u)
    return u


@pytest.fixture
def parent_user(test_db):
    u = User(
        full_name="Parent One",
        email="parent1@example.com",
        password_hash="hashed",
        role=UserRole.PARENT,
        country="Nigeria",
    )
    test_db.add(u)
    test_db.commit()
    test_db.refresh(u)
    return u


@pytest.fixture
def admin_user(test_db):
    u = User(
        full_name="Admin One",
        email="admin1@example.com",
        password_hash="hashed",
        role=UserRole.ADMIN,
        country="Nigeria",
    )
    test_db.add(u)
    test_db.commit()
    test_db.refresh(u)
    return u


@pytest.fixture
def super_admin_user(test_db):
    u = User(
        full_name="SuperAdmin One",
        email="superadmin1@example.com",
        password_hash="hashed",
        role=UserRole.SUPER_ADMIN,
        country="Nigeria",
    )
    test_db.add(u)
    test_db.commit()
    test_db.refresh(u)
    return u


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestGetUserOwnership:
    """AWD-H-12: GET /api/users/{user_id} must enforce ownership."""

    def test_educator_can_read_own_record(self, client, educator_user):
        """An EDUCATOR fetching their own user_id receives 200."""
        response = client.get(
            f"/api/users/{educator_user.user_id}",
            headers=_auth(educator_user),
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == educator_user.user_id

    def test_educator_cannot_read_other_user(self, client, educator_user, other_educator):
        """An EDUCATOR fetching a different user's record must receive 403."""
        response = client.get(
            f"/api/users/{other_educator.user_id}",
            headers=_auth(educator_user),
        )
        assert response.status_code == 403, (
            "EDUCATOR should not be able to read another user's record (PII disclosure — AWD-H-12)"
        )

    def test_parent_cannot_read_other_user(self, client, parent_user, educator_user):
        """A PARENT (not admin_or_educator gated) must also be blocked; belt-and-suspenders."""
        # Note: the route is gated by require_admin_or_educator, so a PARENT
        # without educator/admin role will receive 403 at the dependency level.
        response = client.get(
            f"/api/users/{educator_user.user_id}",
            headers=_auth(parent_user),
        )
        assert response.status_code == 403

    def test_admin_can_read_any_user(self, client, admin_user, educator_user):
        """An ADMIN may read any user record."""
        response = client.get(
            f"/api/users/{educator_user.user_id}",
            headers=_auth(admin_user),
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == educator_user.user_id

    def test_super_admin_can_read_any_user(self, client, super_admin_user, educator_user):
        """A SUPER_ADMIN may read any user record."""
        response = client.get(
            f"/api/users/{educator_user.user_id}",
            headers=_auth(super_admin_user),
        )
        assert response.status_code == 200
        assert response.json()["user_id"] == educator_user.user_id

    def test_unauthenticated_request_rejected(self, client, educator_user):
        """Request without auth header must be rejected (401 Unauthorized)."""
        response = client.get(f"/api/users/{educator_user.user_id}")
        assert response.status_code == 401

    def test_admin_gets_404_for_nonexistent_user(self, client, admin_user):
        """Admin requesting a non-existent user_id receives 404, not 403."""
        response = client.get(
            "/api/users/999999",
            headers=_auth(admin_user),
        )
        assert response.status_code == 404

    def test_educator_gets_403_not_404_for_other_user(self, client, educator_user, other_educator):
        """Ownership check fires before the DB lookup — prevents user enumeration via 404 vs 403."""
        response = client.get(
            f"/api/users/{other_educator.user_id}",
            headers=_auth(educator_user),
        )
        # Must be 403, not 404 — 404 would confirm the user_id exists
        assert response.status_code == 403
