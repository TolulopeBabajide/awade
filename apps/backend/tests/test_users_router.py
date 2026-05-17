"""
Tests for user management endpoints.

AWD-H-12: GET /api/users/{user_id} ownership check.
AWD-GRC-02: GET /api/users/me/data-export GDPR data export.
AWD-GRC-03: DELETE /api/users/me GDPR account deletion.
AWD-M-48: SUPER_ADMIN role parity — service methods must accept both ADMIN and SUPER_ADMIN.

Verifies that:
- A user can read their own record (200)
- An EDUCATOR cannot read another user's record (403)
- A PARENT cannot read another user's record (403)
- An ADMIN can read any user's record (200)
- A SUPER_ADMIN can read any user's record (200)
- Unauthenticated request returns 403
- Non-existent user_id returns 404 (admin only, after ownership check passes)
- Data export returns 200 with expected structure for any authenticated user
- Data export includes children + guides for PARENT users
- Unauthenticated data export request returns 401
- SUPER_ADMIN can delete any user (200) — AWD-M-48
- SUPER_ADMIN can update any user (200) — AWD-M-48
- SUPER_ADMIN can view any user profile (200) — AWD-M-48
- SUPER_ADMIN can update any user profile (200) — AWD-M-48
- Authenticated user can delete their own account (200) — AWD-GRC-03
- Account deletion cascades to ChildProfile and ParentGuide records — AWD-GRC-03
- Unauthenticated account deletion request returns 401 — AWD-GRC-03
- AWD-H-83: data export eager-loads children/guides/topics — no N+1 query growth
- AWD-M-172: data export deserialises subjects/grade_levels JSON list fields via _parse_json_list
"""

import pytest
import jwt
from datetime import datetime, timedelta, timezone

from sqlalchemy import event

from apps.backend.models import User, UserRole, ChildProfile, ParentGuide, Topic
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


# ---------------------------------------------------------------------------
# GRC-02: GET /api/users/me/data-export
# ---------------------------------------------------------------------------

class TestDataExport:
    """AWD-GRC-02: GDPR data export endpoint."""

    def test_unauthenticated_request_rejected(self, client):
        """Request without auth header must be rejected (401 Unauthorized)."""
        response = client.get("/api/users/me/data-export")
        assert response.status_code == 401

    def test_educator_export_returns_200_with_user_block(self, client, educator_user):
        """Authenticated EDUCATOR receives 200 with a 'user' block and empty children list."""
        response = client.get(
            "/api/users/me/data-export",
            headers=_auth(educator_user),
        )
        assert response.status_code == 200
        data = response.json()
        assert "export_date" in data
        assert "user" in data
        assert "children" in data
        assert data["user"]["user_id"] == educator_user.user_id
        assert data["user"]["email"] == educator_user.email
        # Password hash must never appear in the export
        assert "password_hash" not in data["user"]
        # EDUCATOR has no children
        assert data["children"] == []

    def test_parent_export_includes_no_children_when_none_exist(self, client, parent_user):
        """A PARENT with no children gets an empty children list (not an error)."""
        response = client.get(
            "/api/users/me/data-export",
            headers=_auth(parent_user),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["role"] == "PARENT"
        assert data["children"] == []

    def test_parent_export_includes_children_and_guides(self, client, test_db, parent_user, sample_topic):
        """A PARENT with children and guides sees them all in the export."""
        # Create a child profile for this parent
        child = ChildProfile(
            parent_id=parent_user.user_id,
            name="Test Child",
            age=8,
        )
        test_db.add(child)
        test_db.commit()
        test_db.refresh(child)

        # Create a guide linked to the child and topic
        guide = ParentGuide(
            child_id=child.child_id,
            topic_id=sample_topic.topic_id,
            ai_generated_content='{"steps": ["step 1"]}',
            is_bookmarked=True,
        )
        test_db.add(guide)
        test_db.commit()
        test_db.refresh(guide)

        response = client.get(
            "/api/users/me/data-export",
            headers=_auth(parent_user),
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["children"]) == 1
        exported_child = data["children"][0]
        assert exported_child["child_id"] == child.child_id
        assert exported_child["name"] == "Test Child"
        assert exported_child["age"] == 8

        assert len(exported_child["guides"]) == 1
        exported_guide = exported_child["guides"][0]
        assert exported_guide["guide_id"] == guide.guide_id
        assert exported_guide["topic_id"] == sample_topic.topic_id
        assert exported_guide["topic_title"] == sample_topic.topic_title
        assert exported_guide["is_bookmarked"] is True

    def test_export_does_not_include_other_parents_children(self, client, test_db, parent_user):
        """A second parent's child must not appear in the first parent's export."""
        # Create a second parent
        other_parent = User(
            full_name="Other Parent",
            email="other_parent@example.com",
            password_hash="hashed",
            role=UserRole.PARENT,
            country="Nigeria",
        )
        test_db.add(other_parent)
        test_db.commit()
        test_db.refresh(other_parent)

        # Add a child to the OTHER parent
        other_child = ChildProfile(
            parent_id=other_parent.user_id,
            name="Other Child",
            age=10,
        )
        test_db.add(other_child)
        test_db.commit()

        response = client.get(
            "/api/users/me/data-export",
            headers=_auth(parent_user),
        )
        assert response.status_code == 200
        data = response.json()
        child_ids = [c["child_id"] for c in data["children"]]
        assert other_child.child_id not in child_ids

    def test_parent_export_eager_loads_children_guides_and_topics_no_n_plus_one(
        self, client, test_db, parent_user, sample_curriculum_structure
    ):
        """AWD-H-83: ``get_data_export`` must not grow SQL query count with N children · M guides.

        The previous implementation issued ``1 + N + N·M`` SELECTs (one per child for guides,
        one per guide for topic). The eager-load fix should fetch the entire child→guide→topic
        tree in a single SELECT regardless of N and M.

        This test seeds a parent with 3 children · 2 guides each (6 guides total, 6 topic rows)
        and counts the SQL statements emitted while assembling the export. The count must stay
        well below the old ``1 + 3 + 6 = 10`` baseline. We assert an upper bound of 4 SQL
        statements for the children/guides/topics block — that bound holds whether SQLAlchemy
        bundles the joinedload into one statement or splits it into a few, and it fails loudly
        if anyone reintroduces a per-child or per-guide loop query.
        """
        # Seed: 3 children, each with 2 guides bound to 2 different topics
        topics = []
        for i in range(2):
            t = Topic(
                curriculum_structure_id=sample_curriculum_structure.curriculum_structure_id,
                topic_title=f"H-83 Topic {i}",
            )
            test_db.add(t)
            topics.append(t)
        test_db.commit()
        for t in topics:
            test_db.refresh(t)

        children = []
        for i in range(3):
            c = ChildProfile(
                parent_id=parent_user.user_id,
                name=f"H-83 Child {i}",
                age=7 + i,
            )
            test_db.add(c)
            children.append(c)
        test_db.commit()
        for c in children:
            test_db.refresh(c)
            for t in topics:
                test_db.add(ParentGuide(
                    child_id=c.child_id,
                    topic_id=t.topic_id,
                    ai_generated_content='{"steps": []}',
                    is_bookmarked=False,
                ))
        test_db.commit()

        # Count SQL statements issued during the export.
        engine = test_db.get_bind()
        statements: list[str] = []

        def _record(conn, cursor, statement, parameters, context, executemany):
            statements.append(statement)

        event.listen(engine, "before_cursor_execute", _record)
        try:
            response = client.get(
                "/api/users/me/data-export",
                headers=_auth(parent_user),
            )
        finally:
            event.remove(engine, "before_cursor_execute", _record)

        assert response.status_code == 200

        data = response.json()
        assert len(data["children"]) == 3
        for exported_child in data["children"]:
            assert len(exported_child["guides"]) == 2
            for g in exported_child["guides"]:
                # Eager-loaded topic_title must be present, not None
                assert g["topic_title"] in {"H-83 Topic 0", "H-83 Topic 1"}

        # Count statements that touch the parent-pivot tables. The old code path
        # issued one per child + one per guide; the new path must stay flat as
        # the data grows. We use a generous upper bound of 4 to allow for
        # joinedload variants, but it is far below the old 10 (1 + 3 + 6).
        target_tokens = ("child_profiles", "parent_guides", "topics")
        relevant = [
            s for s in statements
            if any(tok in s.lower() for tok in target_tokens)
        ]
        assert len(relevant) <= 4, (
            "AWD-H-83 regression: data export issued "
            f"{len(relevant)} SQL statements against child_profiles/parent_guides/topics — "
            "expected ≤4 (single eager-loaded round-trip). Statements: "
            + "\n---\n".join(relevant)
        )

    # --- AWD-M-172: _parse_json_list adoption in get_data_export ---

    def test_export_deserialises_user_subjects_json_list(self, client, test_db, educator_user):
        """AWD-M-172: subjects stored as JSON list string must arrive deserialised in export."""
        educator_user.subjects = '["Mathematics", "Science"]'
        test_db.commit()

        response = client.get("/api/users/me/data-export", headers=_auth(educator_user))
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["subjects"] == ["Mathematics", "Science"]

    def test_export_deserialises_user_grade_levels_json_list(self, client, test_db, educator_user):
        """AWD-M-172: grade_levels stored as JSON list string must arrive deserialised in export."""
        educator_user.grade_levels = '["Grade 1", "Grade 2"]'
        test_db.commit()

        response = client.get("/api/users/me/data-export", headers=_auth(educator_user))
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["grade_levels"] == ["Grade 1", "Grade 2"]

    def test_export_returns_none_for_null_user_subjects(self, client, test_db, educator_user):
        """AWD-M-172: subjects=None on the user row must produce null in the export (not an error)."""
        educator_user.subjects = None
        test_db.commit()

        response = client.get("/api/users/me/data-export", headers=_auth(educator_user))
        assert response.status_code == 200
        assert response.json()["user"]["subjects"] is None

    def test_export_deserialises_child_subjects_json_list(self, client, test_db, parent_user):
        """AWD-M-172: child.subjects stored as JSON list string must arrive deserialised in export."""
        child = ChildProfile(
            parent_id=parent_user.user_id,
            name="M-172 Child",
            age=9,
            subjects='["English", "Art"]',
        )
        test_db.add(child)
        test_db.commit()

        response = client.get("/api/users/me/data-export", headers=_auth(parent_user))
        assert response.status_code == 200
        children = response.json()["children"]
        assert len(children) == 1
        assert children[0]["subjects"] == ["English", "Art"]

    def test_export_returns_none_for_null_child_subjects(self, client, test_db, parent_user):
        """AWD-M-172: child.subjects=None must produce null in the export (not an error)."""
        child = ChildProfile(
            parent_id=parent_user.user_id,
            name="M-172 Child No Subjects",
            age=7,
            subjects=None,
        )
        test_db.add(child)
        test_db.commit()

        response = client.get("/api/users/me/data-export", headers=_auth(parent_user))
        assert response.status_code == 200
        children = response.json()["children"]
        assert len(children) == 1
        assert children[0]["subjects"] is None

    def test_rate_limit_returns_429_after_limit_exceeded(self, client, educator_user):
        """AWD-H-49: data-export endpoint returns 429 once the per-minute rate limit is exceeded.

        The conftest rate_limiter_reset autouse fixture clears limiter state before
        and after this test, so 5 clean requests are expected before the limit fires.
        """
        headers = _auth(educator_user)
        # Exhaust the 5/minute allowance
        for i in range(5):
            resp = client.get("/api/users/me/data-export", headers=headers)
            assert resp.status_code == 200, (
                f"Request {i + 1}/5 should succeed but got {resp.status_code}"
            )
        # Sixth request must be rate-limited
        resp = client.get("/api/users/me/data-export", headers=headers)
        assert resp.status_code == 429, (
            f"Expected 429 after exceeding rate limit but got {resp.status_code}"
        )


# ---------------------------------------------------------------------------
# AWD-M-48: SUPER_ADMIN role parity in service-layer checks
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# GRC-03: DELETE /api/users/me — GDPR account deletion
# ---------------------------------------------------------------------------

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

        # Verify the user is actually gone from the DB
        from apps.backend.models import User as UserModel
        remaining = test_db.query(UserModel).filter(UserModel.user_id == uid).first()
        assert remaining is None, "User record should be deleted from the database"

    def test_parent_can_delete_own_account(self, client, test_db, parent_user):
        """Authenticated PARENT receives 200 with confirmation message."""
        uid = parent_user.user_id
        response = client.delete("/api/users/me", headers=_auth(parent_user))
        assert response.status_code == 200, (
            f"Expected 200 but got {response.status_code}: {response.json()}"
        )
        assert response.json()["message"] == "Account deleted successfully"

        from apps.backend.models import User as UserModel
        remaining = test_db.query(UserModel).filter(UserModel.user_id == uid).first()
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


# ---------------------------------------------------------------------------
# AWD-M-173: _assert_user_access unit tests
# ---------------------------------------------------------------------------

class TestAssertUserAccessM173:
    """
    Unit tests for UserService._assert_user_access (AWD-M-173).

    Tests the extracted helper directly — no HTTP layer needed.
    Covers: owner access, cross-user 403, ADMIN bypass, SUPER_ADMIN bypass.
    """

    def _make_service(self, test_db):
        from apps.backend.services.user_service import UserService
        return UserService(test_db)

    def _make_user(self, user_id: int, role: UserRole) -> User:
        """Build an unsaved User stub with the given id and role."""
        u = User.__new__(User)
        u.user_id = user_id
        u.role = role
        return u

    def test_owner_can_access_own_resource(self, test_db):
        """Caller whose user_id matches target should not raise."""
        svc = self._make_service(test_db)
        caller = self._make_user(42, UserRole.EDUCATOR)
        # Should not raise
        svc._assert_user_access(caller, 42)

    def test_non_owner_educator_raises_403(self, test_db):
        """EDUCATOR accessing a different user's resource must get 403."""
        from fastapi import HTTPException
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.EDUCATOR)
        with pytest.raises(HTTPException) as exc_info:
            svc._assert_user_access(caller, 999)
        assert exc_info.value.status_code == 403

    def test_non_owner_parent_raises_403(self, test_db):
        """PARENT accessing a different user's resource must get 403."""
        from fastapi import HTTPException
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.PARENT)
        with pytest.raises(HTTPException) as exc_info:
            svc._assert_user_access(caller, 999)
        assert exc_info.value.status_code == 403

    def test_admin_bypasses_ownership_check(self, test_db):
        """ADMIN can access any user_id without raising."""
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.ADMIN)
        # Should not raise for a different user_id
        svc._assert_user_access(caller, 999)

    def test_super_admin_bypasses_ownership_check(self, test_db):
        """SUPER_ADMIN can access any user_id without raising."""
        svc = self._make_service(test_db)
        caller = self._make_user(1, UserRole.SUPER_ADMIN)
        # Should not raise for a different user_id
        svc._assert_user_access(caller, 999)
