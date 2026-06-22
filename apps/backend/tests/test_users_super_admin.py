"""
Tests for SUPER_ADMIN role parity in user management endpoints.

AWD-M-48: SUPER_ADMIN must have the same privileges as ADMIN across all
user_service methods (delete_user, update_user, get_user_profile,
update_user_profile).
"""

import pytest

from users_test_helpers import _auth


class TestSuperAdminRoleParity:
    """AWD-M-48: SUPER_ADMIN must have the same privileges as ADMIN in user_service methods.

    Prior to this fix, require_admin (router guard) allowed SUPER_ADMIN through but
    user_service.delete_user / update_user / get_user_profile / update_user_profile
    all checked ``role != UserRole.ADMIN``, causing 403 for SUPER_ADMIN callers.
    """

    def test_super_admin_can_delete_user(self, client, super_admin_user, educator_user):
        """SUPER_ADMIN receives 200 when deleting another user (AWD-M-48)."""
        response = client.delete(
            f"/api/users/{educator_user.user_id}",
            headers=_auth(super_admin_user),
        )
        assert response.status_code == 200, (
            f"SUPER_ADMIN should be able to delete a user but got {response.status_code}: "
            f"{response.json()}"
        )
        assert response.json().get("message") == "User deleted successfully"

    def test_super_admin_cannot_delete_self(self, client, super_admin_user):
        """SUPER_ADMIN gets 400 when attempting to delete their own account (self-deletion guard)."""
        response = client.delete(
            f"/api/users/{super_admin_user.user_id}",
            headers=_auth(super_admin_user),
        )
        assert response.status_code == 400

    def test_super_admin_can_update_any_user(self, client, super_admin_user, educator_user):
        """SUPER_ADMIN receives 200 when updating another user's record (AWD-M-48)."""
        response = client.put(
            f"/api/users/{educator_user.user_id}",
            json={"full_name": "Updated By SuperAdmin"},
            headers=_auth(super_admin_user),
        )
        assert response.status_code == 200, (
            f"SUPER_ADMIN should be able to update a user but got {response.status_code}: "
            f"{response.json()}"
        )

    def test_super_admin_can_view_user_profile(self, client, super_admin_user, educator_user):
        """SUPER_ADMIN receives 200 when viewing another user's profile (AWD-M-48)."""
        response = client.get(
            f"/api/users/{educator_user.user_id}/profile",
            headers=_auth(super_admin_user),
        )
        assert response.status_code == 200, (
            f"SUPER_ADMIN should be able to view any user profile but got {response.status_code}: "
            f"{response.json()}"
        )

    def test_super_admin_can_update_user_profile(self, client, super_admin_user, educator_user):
        """SUPER_ADMIN receives 200 when updating another user's profile (AWD-M-48)."""
        response = client.put(
            f"/api/users/{educator_user.user_id}/profile",
            json={"full_name": "Profile Updated By SuperAdmin"},
            headers=_auth(super_admin_user),
        )
        assert response.status_code == 200, (
            f"SUPER_ADMIN should be able to update any user profile but got {response.status_code}: "
            f"{response.json()}"
        )

    def test_non_admin_cannot_delete_user(self, client, educator_user, other_educator):
        """A plain EDUCATOR is still blocked from deleting another user (403)."""
        response = client.delete(
            f"/api/users/{other_educator.user_id}",
            headers=_auth(educator_user),
        )
        assert response.status_code == 403
