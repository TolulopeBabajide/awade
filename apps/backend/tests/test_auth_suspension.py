"""
Tests that suspended users are blocked by get_current_active_user (AWD-M-129 split).

Covers H-24: Suspended users must be blocked at the auth dependency layer.
"""

import jwt as pyjwt
from datetime import datetime, timedelta, timezone


# ---------------------------------------------------------------------------
# H-24: Suspended users must be blocked by get_current_active_user
# ---------------------------------------------------------------------------

class TestSuspendedUserAuthBypass:
    """Verify that a suspended user cannot access protected endpoints."""

    def _make_token(self, user_id: int) -> str:
        """Mint a valid JWT for the given user_id using the test secret."""
        payload = {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }
        return pyjwt.encode(payload, "test_jwt_secret", algorithm="HS256")

    def test_active_user_can_access_protected_endpoint(self, client, sample_user):
        """Baseline: a non-suspended user with a valid token gets through."""
        token = self._make_token(sample_user.user_id)
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        # 200 means the dependency chain passed; any other 4xx would indicate
        # the endpoint itself requires something extra — we only care it isn't 403.
        assert response.status_code != 403, (
            "Active user should not receive 403 from get_current_active_user"
        )

    def test_suspended_user_receives_403(self, client, sample_user, test_db):
        """A user with is_suspended=1 must receive 403 on every protected endpoint."""
        sample_user.is_suspended = 1
        test_db.commit()

        token = self._make_token(sample_user.user_id)
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "Account suspended"

    def test_suspended_user_unblocked_after_unsuspend(self, client, sample_user, test_db):
        """After clearing is_suspended the user can authenticate again."""
        # Suspend then re-activate
        sample_user.is_suspended = 1
        test_db.commit()
        sample_user.is_suspended = 0
        test_db.commit()

        token = self._make_token(sample_user.user_id)
        response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code != 403, (
            "Re-activated user must not receive 403 from get_current_active_user"
        )
