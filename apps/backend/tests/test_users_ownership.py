"""
Tests for GET /api/users/{user_id} ownership enforcement.

AWD-H-12: A user may read their own record; EDUCATOR/PARENT cannot read
another user's record; ADMIN and SUPER_ADMIN can read any record.
"""

import pytest

from users_test_helpers import _auth


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
