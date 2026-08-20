"""
Rate-limit structural tests for curriculum read endpoints.

Covers AWD-M-200:
- All GET (read) endpoints in curriculum, curriculum_structure, grade_level, and subject
  routers must carry the `request: Request` parameter required by slowapi.
- The routes must still be registered after decorator application.
"""

import inspect
import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app


@pytest.fixture(autouse=True)
def set_env(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    monkeypatch.setenv("ENVIRONMENT", "testing")


@pytest.fixture()
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


class TestCurriculumReadRateLimitM200:
    """
    M-200 — curriculum read endpoints must be rate-limited at 60/minute.

    Structural checks: request parameter present + route still registered.
    """

    # --- curriculum router ---

    @pytest.mark.parametrize("func_name", [
        "get_curriculums",
        "get_topics",
        "get_topic",
        "get_learning_objectives",
        "get_contents",
        "get_curriculum",
    ])
    def test_curriculum_read_has_request_param(self, func_name):
        from apps.backend.routers import curriculum as m
        func = getattr(m, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"curriculum.{func_name} is missing `request: Request` — "
            "@limiter.limit() will silently fail without it (AWD-M-200)."
        )

    def test_get_curriculums_route_registered(self, client):
        resp = client.get("/api/curriculum/")
        assert resp.status_code != 404, "GET /api/curriculum/ returned 404 after @limiter.limit"

    def test_get_topics_route_registered(self, client):
        resp = client.get("/api/curriculum/topics")
        assert resp.status_code != 404, "GET /api/curriculum/topics returned 404 after @limiter.limit"

    def test_get_topic_route_registered(self, client):
        resp = client.get("/api/curriculum/topics/1")
        assert resp.status_code != 404, "GET /api/curriculum/topics/1 returned 404 after @limiter.limit"

    def test_get_learning_objectives_route_registered(self, client):
        resp = client.get("/api/curriculum/topics/1/learning-objectives")
        assert resp.status_code != 404, "GET /api/curriculum/topics/1/learning-objectives returned 404"

    def test_get_contents_route_registered(self, client):
        resp = client.get("/api/curriculum/topics/1/contents")
        assert resp.status_code != 404, "GET /api/curriculum/topics/1/contents returned 404"

    def test_get_curriculum_by_id_route_registered(self, client):
        resp = client.get("/api/curriculum/1")
        assert resp.status_code != 404, "GET /api/curriculum/1 returned 404 after @limiter.limit"

    # --- curriculum_structure router ---

    @pytest.mark.parametrize("func_name", [
        "list_curriculum_structures",
        "get_curriculum_structure",
    ])
    def test_curriculum_structure_read_has_request_param(self, func_name):
        from apps.backend.routers import curriculum_structure as m
        func = getattr(m, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"curriculum_structure.{func_name} is missing `request: Request` — "
            "@limiter.limit() will silently fail without it (AWD-M-200)."
        )

    def test_list_curriculum_structures_route_registered(self, client):
        resp = client.get("/api/curriculum-structures/")
        assert resp.status_code != 404, "GET /api/curriculum-structures/ returned 404"

    def test_get_curriculum_structure_route_registered(self, client):
        resp = client.get("/api/curriculum-structures/1")
        assert resp.status_code != 404, "GET /api/curriculum-structures/1 returned 404"

    # --- grade_level router ---

    @pytest.mark.parametrize("func_name", [
        "list_grade_levels",
        "get_grade_level",
        "search_grade_levels",
        "get_grade_levels_by_curriculum",
        "get_grade_levels_by_subject",
    ])
    def test_grade_level_read_has_request_param(self, func_name):
        from apps.backend.routers import grade_level as m
        func = getattr(m, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"grade_level.{func_name} is missing `request: Request` — "
            "@limiter.limit() will silently fail without it (AWD-M-200)."
        )

    def test_list_grade_levels_route_registered(self, client):
        resp = client.get("/api/grade-levels/")
        assert resp.status_code != 404, "GET /api/grade-levels/ returned 404"

    def test_search_grade_levels_route_registered(self, client):
        resp = client.get("/api/grade-levels/search?q=JSS1")
        assert resp.status_code != 404, "GET /api/grade-levels/search returned 404"

    def test_grade_levels_by_curriculum_route_registered(self, client):
        resp = client.get("/api/grade-levels/curriculum/1")
        assert resp.status_code != 404, "GET /api/grade-levels/curriculum/1 returned 404"

    def test_grade_levels_by_subject_route_registered(self, client):
        resp = client.get("/api/grade-levels/subject/1")
        assert resp.status_code != 404, "GET /api/grade-levels/subject/1 returned 404"

    def test_get_grade_level_route_registered(self, client):
        resp = client.get("/api/grade-levels/1")
        assert resp.status_code != 404, "GET /api/grade-levels/1 returned 404"

    # --- subject router ---

    @pytest.mark.parametrize("func_name", [
        "list_subjects",
        "get_subject",
        "search_subjects",
        "get_subjects_by_curriculum",
    ])
    def test_subject_read_has_request_param(self, func_name):
        from apps.backend.routers import subject as m
        func = getattr(m, func_name)
        sig = inspect.signature(func)
        assert "request" in sig.parameters, (
            f"subject.{func_name} is missing `request: Request` — "
            "@limiter.limit() will silently fail without it (AWD-M-200)."
        )

    def test_list_subjects_route_registered(self, client):
        resp = client.get("/api/subjects/")
        assert resp.status_code != 404, "GET /api/subjects/ returned 404"

    def test_search_subjects_route_registered(self, client):
        resp = client.get("/api/subjects/search?q=Math")
        assert resp.status_code != 404, "GET /api/subjects/search returned 404"

    def test_subjects_by_curriculum_route_registered(self, client):
        resp = client.get("/api/subjects/curriculum/1")
        assert resp.status_code != 404, "GET /api/subjects/curriculum/1 returned 404"

    def test_get_subject_route_registered(self, client):
        resp = client.get("/api/subjects/1")
        assert resp.status_code != 404, "GET /api/subjects/1 returned 404"
