"""
Tests for DELETE /api/users/me — GDPR account deletion endpoint.

AWD-GRC-03: Authenticated users can permanently delete their own accounts.
Verifies cascade deletion of ChildProfile and ParentGuide records.
"""

import pytest

from apps.backend.models import User, ChildProfile, ParentGuide

from users_test_helpers import _auth


class TestAccountDeletion:
    """AWD-GRC-03: Authenticated users can permanently delete their own accounts.

    Verifies:
    - Any authenticated role receives 200 and a confirmation message
    - ChildProfile rows belonging to a PARENT are deleted (cascade)
    - ParentGuide rows belonging to those children are deleted (cascade)
    - Unauthenticated requests receive 401
    - The deleted user's record is no longer present in the DB
    """

    def test_educator_can_delete_own_account(self, client, test_db, educator_user):
        """Authenticated EDUCATOR receives 200 with confirmation message."""
        uid = educator_user.user_id
        response = client.delete("/api/users/me", headers=_auth(educator_user))
        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.json()}"
        )
        assert response.json()["message"] == "Account deleted successfully"

        remaining = test_db.query(User).filter(User.user_id == uid).first()
        assert remaining is None, "User record should be deleted from the database"

    def test_parent_can_delete_own_account(self, client, test_db, parent_user):
        """Authenticated PARENT receives 200 with confirmation message."""
        uid = parent_user.user_id
        response = client.delete("/api/users/me", headers=_auth(parent_user))
        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.json()}"
        )
        assert response.json()["message"] == "Account deleted successfully"

        remaining = test_db.query(User).filter(User.user_id == uid).first()
        assert remaining is None

    def test_account_deletion_cascades_to_child_profiles(
        self, client, test_db, parent_user
    ):
        """Deleting a PARENT account also removes all associated ChildProfile rows."""
        child = ChildProfile(
            parent_id=parent_user.user_id,
            name="Cascade Child",
            age=9,
        )
        test_db.add(child)
        test_db.commit()
        test_db.refresh(child)
        child_id = child.child_id

        response = client.delete("/api/users/me", headers=_auth(parent_user))
        assert response.status_code == 200

        remaining = test_db.query(ChildProfile).filter(
            ChildProfile.child_id == child_id
        ).first()
        assert remaining is None, (
            "ChildProfile should be cascade-deleted when the parent account is removed"
        )

    def test_account_deletion_cascades_to_parent_guides(
        self, client, test_db, parent_user, sample_topic
    ):
        """Deleting a PARENT account also removes all ParentGuide records for their children."""
        child = ChildProfile(
            parent_id=parent_user.user_id,
            name="Guide Cascade Child",
            age=7,
        )
        test_db.add(child)
        test_db.commit()
        test_db.refresh(child)

        guide = ParentGuide(
            child_id=child.child_id,
            topic_id=sample_topic.topic_id,
            ai_generated_content='{"steps": ["read together"]}',
        )
        test_db.add(guide)
        test_db.commit()
        test_db.refresh(guide)
        guide_id = guide.guide_id

        response = client.delete("/api/users/me", headers=_auth(parent_user))
        assert response.status_code == 200

        remaining_guide = test_db.query(ParentGuide).filter(
            ParentGuide.guide_id == guide_id
        ).first()
        assert remaining_guide is None, (
            "ParentGuide should be cascade-deleted when the parent account is removed"
        )

    def test_unauthenticated_request_rejected(self, client):
        """Request without auth token must be rejected with 401."""
        response = client.delete("/api/users/me")
        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated account deletion but got {response.status_code}"
        )
