"""
Tests for GET /api/users/me/data-export (GDPR data export endpoint).

AWD-GRC-02: Any authenticated user can export their own data.
AWD-H-83: Export must eager-load children/guides/topics — no N+1 queries.
AWD-M-172: subjects/grade_levels JSON list fields must be deserialised.
"""

import pytest
from sqlalchemy import event

from apps.backend.models import User, UserRole, ChildProfile, ParentGuide

from users_test_helpers import _auth


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
        child = ChildProfile(
            parent_id=parent_user.user_id,
            name="Test Child",
            age=8,
        )
        test_db.add(child)
        test_db.commit()
        test_db.refresh(child)

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
        self, client, test_db, test_engine, parent_user, sample_curriculum_structure
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
        from apps.backend.models import Topic

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

        engine = test_engine
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
                assert g["topic_title"] in {"H-83 Topic 0", "H-83 Topic 1"}

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
        for i in range(5):
            resp = client.get("/api/users/me/data-export", headers=headers)
            assert resp.status_code == 200, (
                f"Request {i + 1}/5 should succeed but got {resp.status_code}"
            )
        resp = client.get("/api/users/me/data-export", headers=headers)
        assert resp.status_code == 429, (
            f"Expected 429 after exceeding rate limit but got {resp.status_code}"
        )
