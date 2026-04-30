"""
Tests for AWD-H-40 — lesson_plans router export endpoint does not leak
internal error details in HTTPException.detail.

Covers:
- 404 when resource not found
- 404 when educator tries to export another user's resource (AWD-M-67: no 403 leakage)
- 400 for unsupported export format
- 500 for unexpected export failure uses static detail (no str(e))
- 200 PDF happy path
- 200 DOCX happy path
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(backend_dir))
sys.path.insert(0, backend_dir)
sys.path.insert(0, root_dir)

from apps.backend.main import app
from apps.backend.database import get_db
from apps.backend.models import User, UserRole, LessonResource
from apps.backend.dependencies import get_current_user


def _make_user(user_id: int, role: UserRole = UserRole.EDUCATOR) -> User:
    u = User()
    u.user_id = user_id
    u.full_name = f"User {user_id}"
    u.email = f"user{user_id}@example.com"
    u.role = role
    u.is_active = True
    u.is_suspended = False
    return u


def _make_resource(resource_id: int, owner_user_id: int) -> LessonResource:
    r = LessonResource()
    r.lesson_resources_id = resource_id
    r.user_id = owner_user_id
    r.lesson_plan_id = 1
    r.ai_generated_content = "Some content"
    r.user_edited_content = None
    return r


@pytest.fixture()
def educator():
    return _make_user(user_id=1, role=UserRole.EDUCATOR)


@pytest.fixture()
def other_educator():
    return _make_user(user_id=2, role=UserRole.EDUCATOR)


@pytest.fixture()
def admin_user():
    return _make_user(user_id=99, role=UserRole.ADMIN)


@pytest.fixture()
def resource(educator):
    return _make_resource(resource_id=42, owner_user_id=educator.user_id)


def _client_for_user(user: User, db_mock: MagicMock) -> TestClient:
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = lambda: db_mock
    client = TestClient(app, raise_server_exceptions=False)
    return client


class TestExportLessonResource:
    """AWD-H-40 — export endpoint error-handling tests."""

    def teardown_method(self):
        app.dependency_overrides.clear()

    def _db_with_resource(self, resource: LessonResource) -> MagicMock:
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = resource
        return db

    def _db_without_resource(self) -> MagicMock:
        db = MagicMock()
        db.query.return_value.filter.return_value.first.return_value = None
        return db

    # ── 404 ──────────────────────────────────────────────────────────────────

    def test_resource_not_found_returns_404(self, educator):
        db = self._db_without_resource()
        client = _client_for_user(educator, db)
        resp = client.post(
            "/api/lesson-plans/resources/99/export",
            json={"format": "pdf"},
        )
        assert resp.status_code == 404

    # ── 404 (cross-user — AWD-M-67) ──────────────────────────────────────────

    def test_cross_user_export_returns_404_not_403(self, other_educator, resource):
        # AWD-M-67: non-admin requesting another owner's resource must get 404,
        # not 403, so the resource's existence is not revealed.
        # The scoped query returns None for the other_educator's user_id.
        db = self._db_without_resource()
        client = _client_for_user(other_educator, db)
        resp = client.post(
            f"/api/lesson-plans/resources/{resource.lesson_resources_id}/export",
            json={"format": "pdf"},
        )
        assert resp.status_code == 404

    def test_admin_can_export_any_resource(self, admin_user, resource):
        db = self._db_with_resource(resource)
        client = _client_for_user(admin_user, db)
        with patch(
            "apps.backend.services.pdf_service.PDFService.generate_lesson_resource_pdf",
            return_value=b"%PDF-1.4 fake",
        ):
            resp = client.post(
                f"/api/lesson-plans/resources/{resource.lesson_resources_id}/export",
                json={"format": "pdf"},
            )
        assert resp.status_code == 200

    # ── 400 ──────────────────────────────────────────────────────────────────

    def test_unsupported_format_returns_400(self, educator, resource):
        db = self._db_with_resource(resource)
        client = _client_for_user(educator, db)
        resp = client.post(
            f"/api/lesson-plans/resources/{resource.lesson_resources_id}/export",
            json={"format": "xlsx"},
        )
        assert resp.status_code == 400

    # ── 500 — AWD-H-40 core assertion ────────────────────────────────────────

    def test_unexpected_error_returns_static_detail(self, educator, resource):
        """H-40: 500 detail must NOT expose str(e) — must be a static string."""
        db = self._db_with_resource(resource)
        client = _client_for_user(educator, db)
        secret_message = "WeasyPrint internal traceback: /etc/secrets/db.cred"
        with patch(
            "apps.backend.services.pdf_service.PDFService.generate_lesson_resource_pdf",
            side_effect=RuntimeError(secret_message),
        ):
            resp = client.post(
                f"/api/lesson-plans/resources/{resource.lesson_resources_id}/export",
                json={"format": "pdf"},
            )
        assert resp.status_code == 500
        detail = resp.json().get("detail", "")
        assert secret_message not in detail, (
            f"H-40: internal error detail leaked in response: {detail}"
        )
        # Static message must be present
        assert "exporting the resource" in detail.lower()

    # ── 200 happy paths ───────────────────────────────────────────────────────

    def test_pdf_export_happy_path(self, educator, resource):
        db = self._db_with_resource(resource)
        client = _client_for_user(educator, db)
        with patch(
            "apps.backend.services.pdf_service.PDFService.generate_lesson_resource_pdf",
            return_value=b"%PDF-1.4 fake",
        ):
            resp = client.post(
                f"/api/lesson-plans/resources/{resource.lesson_resources_id}/export",
                json={"format": "pdf"},
            )
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"

    def test_docx_export_happy_path(self, educator, resource):
        db = self._db_with_resource(resource)
        client = _client_for_user(educator, db)
        with patch(
            "apps.backend.services.pdf_service.PDFService.export_to_docx",
            return_value=b"PK fake docx",
        ):
            resp = client.post(
                f"/api/lesson-plans/resources/{resource.lesson_resources_id}/export",
                json={"format": "docx"},
            )
        assert resp.status_code == 200
        assert "wordprocessingml" in resp.headers["content-type"]
