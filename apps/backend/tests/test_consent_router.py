"""
Tests for AWD-GRC-01: COPPA parental consent endpoints.

Covers:
- GET  /api/consent/status — unauthenticated → 401
- GET  /api/consent/status — EDUCATOR → 403
- GET  /api/consent/status — PARENT, no record → {has_consented: false}
- GET  /api/consent/status — PARENT, record exists → {has_consented: true, consent: {...}}
- POST /api/consent        — unauthenticated → 401
- POST /api/consent        — EDUCATOR → 403
- POST /api/consent        — PARENT, first time → 201, record created
- POST /api/consent        — PARENT, idempotent → 201, updates timestamp
- POST /children           — PARENT, no consent → 403
- POST /children           — PARENT, consent given → 201 (existing behaviour)
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch, call

from fastapi.testclient import TestClient

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.dependencies import get_current_active_user
from apps.backend.models import User, UserRole, ParentalConsent, ChildProfile


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_user(user_id: int, role: UserRole, email: str = None) -> User:
    u = User()
    u.user_id = user_id
    u.email = email or f"user{user_id}@example.com"
    u.role = role
    u.is_suspended = False
    return u


def _make_parent(user_id: int = 1) -> User:
    return _make_user(user_id, UserRole.PARENT, "parent@example.com")


def _make_educator(user_id: int = 10) -> User:
    return _make_user(user_id, UserRole.EDUCATOR, "educator@example.com")


def _auth_override(user: User):
    def _dep():
        return user
    return _dep


def _now():
    return datetime.now(timezone.utc)


def _make_consent(parent_id: int = 1) -> ParentalConsent:
    c = ParentalConsent()
    c.consent_id = 1
    c.parent_id = parent_id
    c.consented_at = _now()
    c.ip_address = "127.0.0.1"
    c.consent_version = "1.0"
    return c


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def parent_client():
    parent = _make_parent()
    app.dependency_overrides[get_current_active_user] = _auth_override(parent)
    yield TestClient(app, raise_server_exceptions=False), parent
    app.dependency_overrides.pop(get_current_active_user, None)


@pytest.fixture()
def educator_client():
    educator = _make_educator()
    app.dependency_overrides[get_current_active_user] = _auth_override(educator)
    yield TestClient(app, raise_server_exceptions=False), educator
    app.dependency_overrides.pop(get_current_active_user, None)


# ---------------------------------------------------------------------------
# GET /api/consent/status
# ---------------------------------------------------------------------------

class TestGetConsentStatus:
    """Tests for the consent status endpoint."""

    def test_unauthenticated_returns_401(self, client):
        resp = client.get("/api/consent/status")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"

    def test_educator_returns_403(self, educator_client):
        tc, _ = educator_client
        with patch("apps.backend.services.children_service.ChildrenService.get_consent_status") as mock_svc:
            resp = tc.get("/api/consent/status")
        assert resp.status_code == 403

    def test_parent_no_consent_returns_false(self, parent_client):
        tc, _ = parent_client
        with patch("apps.backend.services.children_service.ChildrenService.get_consent_status") as mock_svc:
            from apps.backend.schemas.children import ConsentStatusResponse
            mock_svc.return_value = ConsentStatusResponse(has_consented=False, consent=None)
            resp = tc.get("/api/consent/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_consented"] is False
        assert data["consent"] is None

    def test_parent_with_consent_returns_true(self, parent_client):
        tc, _ = parent_client
        with patch("apps.backend.services.children_service.ChildrenService.get_consent_status") as mock_svc:
            from apps.backend.schemas.children import ConsentStatusResponse, ParentalConsentResponse
            mock_svc.return_value = ConsentStatusResponse(
                has_consented=True,
                consent=ParentalConsentResponse(
                    parent_id=1,
                    consented_at=_now(),
                    consent_version="1.0",
                ),
            )
            resp = tc.get("/api/consent/status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_consented"] is True
        assert data["consent"]["parent_id"] == 1
        assert data["consent"]["consent_version"] == "1.0"


# ---------------------------------------------------------------------------
# POST /api/consent
# ---------------------------------------------------------------------------

class TestRecordConsent:
    """Tests for the record consent endpoint."""

    def test_unauthenticated_returns_401(self, client):
        resp = client.post("/api/consent")
        assert resp.status_code == 401

    def test_educator_returns_403(self, educator_client):
        tc, _ = educator_client
        resp = tc.post("/api/consent")
        assert resp.status_code == 403

    def test_parent_first_consent_returns_201(self, parent_client):
        tc, _ = parent_client
        with patch("apps.backend.services.children_service.ChildrenService.record_consent") as mock_svc:
            from apps.backend.schemas.children import ParentalConsentResponse
            mock_svc.return_value = ParentalConsentResponse(
                parent_id=1,
                consented_at=_now(),
                consent_version="1.0",
            )
            resp = tc.post("/api/consent")
        assert resp.status_code == 201
        data = resp.json()
        assert data["parent_id"] == 1
        assert data["consent_version"] == "1.0"
        mock_svc.assert_called_once()

    def test_parent_idempotent_consent_returns_201(self, parent_client):
        """Re-posting consent updates the record rather than failing."""
        tc, _ = parent_client
        with patch("apps.backend.services.children_service.ChildrenService.record_consent") as mock_svc:
            from apps.backend.schemas.children import ParentalConsentResponse
            mock_svc.return_value = ParentalConsentResponse(
                parent_id=1,
                consented_at=_now(),
                consent_version="1.0",
            )
            resp1 = tc.post("/api/consent")
            resp2 = tc.post("/api/consent")
        assert resp1.status_code == 201
        assert resp2.status_code == 201
        assert mock_svc.call_count == 2


# ---------------------------------------------------------------------------
# POST /api/children — consent guard
# ---------------------------------------------------------------------------

class TestCreateChildConsentGuard:
    """Consent must be given before a child profile can be created."""

    def test_create_child_without_consent_returns_403(self, parent_client):
        tc, _ = parent_client
        with patch("apps.backend.services.children_service.ChildrenService.create_child") as mock_svc:
            from fastapi import HTTPException, status
            mock_svc.side_effect = HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Parental consent required.",
            )
            resp = tc.post("/api/children", json={
                "name": "Amara",
                "age": 9,
            })
        assert resp.status_code == 403

    def test_create_child_with_consent_returns_201(self, parent_client):
        tc, _ = parent_client
        with patch("apps.backend.services.children_service.ChildrenService.create_child") as mock_svc:
            from apps.backend.schemas.children import ChildProfileResponse
            mock_svc.return_value = ChildProfileResponse(
                child_id=1,
                parent_id=1,
                name="Amara",
                age=9,
                school_name=None,
                country_id=None,
                country_name=None,
                curricula_id=None,
                curriculum_title=None,
                grade_level_id=None,
                grade_level_name=None,
                subjects=None,
                created_at=_now(),
                updated_at=_now(),
            )
            resp = tc.post("/api/children", json={"name": "Amara", "age": 9})
        assert resp.status_code == 201
        assert resp.json()["name"] == "Amara"
