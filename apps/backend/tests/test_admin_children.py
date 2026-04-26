"""
Tests for AWD-GRC-05: COPPA audit logs for admin access to child profiles.

Covers:
- 401 when unauthenticated on both admin/children endpoints
- 403 when EDUCATOR role attempts to access admin endpoints
- 403 when PARENT role attempts to access admin endpoints
- 200 list — returns all child profiles; audit log entry created
- 200 list with parent_id filter — returns only matching children
- 200 get single — returns child profile; audit log entry created
- 404 get single — child does not exist; not-found audit log entry created
- Audit log target_type is 'child_profile' for all actions
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_active_user
from apps.backend.models import User, UserRole, ChildProfile, AdminAuditLog


# ---------------------------------------------------------------------------
# Helpers / factories
# ---------------------------------------------------------------------------

def _make_user(user_id: int, role: UserRole, email: str = None) -> User:
    u = User()
    u.user_id = user_id
    u.email = email or f"user{user_id}@example.com"
    u.full_name = f"User {user_id}"
    u.role = role
    u.is_suspended = False
    return u


def _make_admin(user_id: int = 99, email: str = "admin@awade.test") -> User:
    return _make_user(user_id, UserRole.ADMIN, email)


def _make_educator(user_id: int = 10) -> User:
    return _make_user(user_id, UserRole.EDUCATOR)


def _make_parent(user_id: int = 20) -> User:
    return _make_user(user_id, UserRole.PARENT)


def _auth_override(user: User):
    def _dep():
        return user
    return _dep


def _make_child(child_id: int, parent_id: int, name: str = "Test Child") -> ChildProfile:
    from datetime import datetime, timezone
    c = ChildProfile()
    c.child_id = child_id
    c.parent_id = parent_id
    c.name = name
    c.age = 8
    c.school_name = "Test School"
    c.country_id = None
    c.curricula_id = None
    c.grade_level_id = None
    c.subjects = json.dumps([1, 2])
    c.created_at = datetime.now(timezone.utc)
    c.updated_at = datetime.now(timezone.utc)
    return c


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_overrides():
    """Ensure dependency overrides are cleared after every test."""
    yield
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Authentication / authorisation tests
# ---------------------------------------------------------------------------

class TestAdminChildrenAuth:
    """Unauthenticated and wrong-role requests must be rejected."""

    def test_list_children_unauthenticated(self):
        """GET /api/admin/children — no auth header → 401."""
        with TestClient(app) as client:
            response = client.get("/api/admin/children")
        assert response.status_code == 401

    def test_get_child_unauthenticated(self):
        """GET /api/admin/children/{id} — no auth header → 401."""
        with TestClient(app) as client:
            response = client.get("/api/admin/children/1")
        assert response.status_code == 401

    def test_list_children_educator_forbidden(self):
        """EDUCATOR role must receive 403 on admin/children list."""
        app.dependency_overrides[get_current_active_user] = _auth_override(_make_educator())
        with TestClient(app) as client:
            response = client.get("/api/admin/children")
        assert response.status_code == 403

    def test_get_child_educator_forbidden(self):
        """EDUCATOR role must receive 403 on admin/children/{id}."""
        app.dependency_overrides[get_current_active_user] = _auth_override(_make_educator())
        with TestClient(app) as client:
            response = client.get("/api/admin/children/1")
        assert response.status_code == 403

    def test_list_children_parent_forbidden(self):
        """PARENT role must receive 403 on admin/children list."""
        app.dependency_overrides[get_current_active_user] = _auth_override(_make_parent())
        with TestClient(app) as client:
            response = client.get("/api/admin/children")
        assert response.status_code == 403

    def test_get_child_parent_forbidden(self):
        """PARENT role must receive 403 on admin/children/{id}."""
        app.dependency_overrides[get_current_active_user] = _auth_override(_make_parent())
        with TestClient(app) as client:
            response = client.get("/api/admin/children/1")
        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Happy-path tests (DB mocked)
# ---------------------------------------------------------------------------

class TestAdminListChildren:
    """GET /api/admin/children — admin access and audit logging."""

    def _setup_db_mock(self, children: list):
        """Return a mock DB session whose query chain returns `children`."""
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = children
        # log_admin_action calls db.add() + db.commit()
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        return mock_db

    def test_list_children_admin_200(self):
        """Admin gets 200 with a list of child profiles."""
        admin = _make_admin()
        child = _make_child(child_id=1, parent_id=20)
        mock_db = self._setup_db_mock([child])

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            response = client.get("/api/admin/children")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["child_id"] == 1
        assert data[0]["parent_id"] == 20

    def test_list_children_audit_log_created(self):
        """list endpoint must add an AdminAuditLog row with correct fields."""
        admin = _make_admin()
        mock_db = self._setup_db_mock([])

        captured_logs = []

        def _capture_add(obj):
            captured_logs.append(obj)

        mock_db.add.side_effect = _capture_add

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            client.get("/api/admin/children")

        audit_entries = [o for o in captured_logs if isinstance(o, AdminAuditLog)]
        assert len(audit_entries) == 1
        log = audit_entries[0]
        assert log.actor_id == admin.user_id
        assert log.action == "view_child_profiles"
        assert log.target_type == "child_profile"

    def test_list_children_parent_id_filter(self):
        """parent_id query param is forwarded to the DB filter."""
        admin = _make_admin()
        child = _make_child(child_id=5, parent_id=42)
        mock_db = self._setup_db_mock([child])

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            response = client.get("/api/admin/children?parent_id=42")

        assert response.status_code == 200
        data = response.json()
        assert data[0]["parent_id"] == 42


class TestAdminGetChild:
    """GET /api/admin/children/{child_id} — admin access and audit logging."""

    def _setup_db_mock(self, child):
        mock_db = MagicMock()
        mock_query = MagicMock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = child
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        return mock_db

    def test_get_child_admin_200(self):
        """Admin gets 200 with the child profile."""
        admin = _make_admin()
        child = _make_child(child_id=7, parent_id=20)
        mock_db = self._setup_db_mock(child)

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            response = client.get("/api/admin/children/7")

        assert response.status_code == 200
        data = response.json()
        assert data["child_id"] == 7
        assert data["name"] == "Test Child"

    def test_get_child_audit_log_on_success(self):
        """Successful get must produce an audit log with view_child_profile action."""
        admin = _make_admin()
        child = _make_child(child_id=7, parent_id=20)
        mock_db = self._setup_db_mock(child)

        captured_logs = []
        mock_db.add.side_effect = captured_logs.append

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            client.get("/api/admin/children/7")

        audit_entries = [o for o in captured_logs if isinstance(o, AdminAuditLog)]
        assert len(audit_entries) == 1
        log = audit_entries[0]
        assert log.actor_id == admin.user_id
        assert log.action == "view_child_profile"
        assert log.target_type == "child_profile"
        assert log.target_id == 7

    def test_get_child_404_when_not_found(self):
        """Non-existent child_id must return 404."""
        admin = _make_admin()
        mock_db = self._setup_db_mock(None)

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            response = client.get("/api/admin/children/999")

        assert response.status_code == 404

    def test_get_child_not_found_still_audit_logged(self):
        """Even a 404 attempt must be audit-logged (view_child_profile_not_found)."""
        admin = _make_admin()
        mock_db = self._setup_db_mock(None)

        captured_logs = []
        mock_db.add.side_effect = captured_logs.append

        app.dependency_overrides[get_current_active_user] = _auth_override(admin)
        app.dependency_overrides[get_db] = lambda: mock_db

        with TestClient(app) as client:
            client.get("/api/admin/children/999")

        audit_entries = [o for o in captured_logs if isinstance(o, AdminAuditLog)]
        assert len(audit_entries) == 1
        log = audit_entries[0]
        assert log.action == "view_child_profile_not_found"
        assert log.target_type == "child_profile"
        assert log.target_id == 999
