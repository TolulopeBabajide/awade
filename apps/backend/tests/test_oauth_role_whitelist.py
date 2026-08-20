"""Google OAuth role-whitelist tests (AWD-M-223 split from test_security.py)."""

import datetime

import pytest

from apps.backend.models import User, UserRole


class TestGoogleOAuthRoleWhitelist:
    """
    C-03 — Privilege escalation via Google OAuth.

    Verifies that `authenticate_google_user` never assigns ADMIN or SUPER_ADMIN
    regardless of what the client sends in the `role` field.
    """

    @pytest.mark.parametrize("requested_role,expected_role", [
        ("PARENT", "PARENT"),
        ("EDUCATOR", "EDUCATOR"),
        ("ADMIN", "PARENT"),          # must be coerced to PARENT
        ("SUPER_ADMIN", "PARENT"),    # must be coerced to PARENT
        ("completely_invalid", "PARENT"),  # unknown value → PARENT
        ("", "PARENT"),               # empty string → PARENT
    ])
    def test_role_whitelist(self, test_db, requested_role, expected_role):
        """Client-supplied role is restricted to PARENT / EDUCATOR."""
        from unittest.mock import patch
        from apps.backend.services.auth_service import AuthService

        unique_email = f"oauthtest_{requested_role or 'empty'}@example.com"
        mock_data = {
            "aud": "test_google_client_id",
            "email": unique_email,
            "name": "OAuth Test User",
        }
        service = AuthService(test_db)
        with patch.object(AuthService, "verify_google_token", return_value=mock_data):
            auth_resp, _ = service.authenticate_google_user("fake_token", requested_role=requested_role)

        # Verify the created user has the expected (safe) role
        user = test_db.query(User).filter(User.email == unique_email).first()
        assert user is not None, "User should have been created"
        assert user.role == UserRole(expected_role), (
            f"requested_role={requested_role!r} → expected {expected_role}, got {user.role}"
        )

    def test_existing_user_role_not_changed_by_oauth(self, test_db):
        """Signing in via Google must never mutate the role of an existing user."""
        from unittest.mock import patch
        from apps.backend.services.auth_service import AuthService

        existing_email = "existing_admin@example.com"
        existing_user = User(
            email=existing_email,
            password_hash="google-oauth",
            full_name="Existing Admin",
            role=UserRole.ADMIN,  # already elevated in DB (set by a SUPER_ADMIN, not self-assigned)
            country="",
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
        test_db.add(existing_user)
        test_db.commit()

        mock_data = {
            "aud": "test_google_client_id",
            "email": existing_email,
            "name": "Existing Admin",
        }
        service = AuthService(test_db)
        with patch.object(AuthService, "verify_google_token", return_value=mock_data):
            # Even if attacker passes SUPER_ADMIN, existing user's role must not change
            service.authenticate_google_user("fake_token", requested_role="SUPER_ADMIN")

        test_db.refresh(existing_user)
        assert existing_user.role == UserRole.ADMIN, "Existing user role must not be overwritten"
