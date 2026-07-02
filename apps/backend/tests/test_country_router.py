"""
Unit tests for ``apps/backend/routers/country.py`` — AWD-M-312.

Verifies that the route ordering fix makes /search and /region/{region}
reachable. Before the fix, GET /{country_id} was registered first; FastAPI
matched /search and /region/West%20Africa at that slot, failed int() coercion,
and returned 422 instead of delegating to the correct handler.

Covers (handler-level, no HTTP stack):
- search_countries: delegates to service.search_countries(q, skip, limit)
- get_countries_by_region: delegates to service.get_countries_by_region(region, skip, limit)
- get_country: still delegates to service.get_country(country_id)
- Route reachability via the registered FastAPI route list — /search and
  /region/{region} appear BEFORE /{country_id} after the fix.
"""

import pytest
from unittest.mock import MagicMock

import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(os.path.dirname(backend_dir))
sys.path.insert(0, backend_dir)
sys.path.insert(0, root_dir)

from apps.backend.routers.country import (
    search_countries,
    get_countries_by_region,
    get_country,
)


def _mock_user():
    u = MagicMock()
    u.is_suspended = False
    return u


def _mock_db():
    return MagicMock()


class TestSearchCountriesHandler:
    """search_countries handler delegates correctly to CountryService."""

    def test_delegates_to_service_search(self):
        expected = [MagicMock()]
        db = _mock_db()
        with MagicMock() as svc_cls:
            svc_instance = MagicMock()
            svc_instance.search_countries.return_value = expected
            svc_cls.return_value = svc_instance

            import apps.backend.routers.country as country_module
            original = country_module.CountryService
            country_module.CountryService = lambda db: svc_instance
            try:
                result = search_countries(
                    q="Nigeria",
                    skip=0,
                    limit=10,
                    current_user=_mock_user(),
                    db=db,
                )
            finally:
                country_module.CountryService = original

        svc_instance.search_countries.assert_called_once_with("Nigeria", 0, 10)
        assert result == expected

    def test_delegates_skip_and_limit(self):
        db = _mock_db()
        svc_instance = MagicMock()
        svc_instance.search_countries.return_value = []

        import apps.backend.routers.country as country_module
        original = country_module.CountryService
        country_module.CountryService = lambda db: svc_instance
        try:
            search_countries(
                q="test",
                skip=5,
                limit=20,
                current_user=_mock_user(),
                db=db,
            )
        finally:
            country_module.CountryService = original

        svc_instance.search_countries.assert_called_once_with("test", 5, 20)


class TestGetCountriesByRegionHandler:
    """get_countries_by_region handler delegates correctly to CountryService."""

    def test_delegates_to_service_region(self):
        expected = [MagicMock()]
        db = _mock_db()
        svc_instance = MagicMock()
        svc_instance.get_countries_by_region.return_value = expected

        import apps.backend.routers.country as country_module
        original = country_module.CountryService
        country_module.CountryService = lambda db: svc_instance
        try:
            result = get_countries_by_region(
                region="West Africa",
                skip=0,
                limit=100,
                current_user=_mock_user(),
                db=db,
            )
        finally:
            country_module.CountryService = original

        svc_instance.get_countries_by_region.assert_called_once_with("West Africa", 0, 100)
        assert result == expected

    def test_region_string_not_coerced_to_int(self):
        db = _mock_db()
        svc_instance = MagicMock()
        svc_instance.get_countries_by_region.return_value = []

        import apps.backend.routers.country as country_module
        original = country_module.CountryService
        country_module.CountryService = lambda db: svc_instance
        try:
            get_countries_by_region(
                region="search",
                skip=0,
                limit=100,
                current_user=_mock_user(),
                db=db,
            )
        finally:
            country_module.CountryService = original

        args = svc_instance.get_countries_by_region.call_args[0]
        assert args[0] == "search"


class TestGetCountryHandler:
    """get_country handler still works by integer ID."""

    def test_delegates_to_service_get_country(self):
        expected = MagicMock()
        db = _mock_db()
        svc_instance = MagicMock()
        svc_instance.get_country.return_value = expected

        import apps.backend.routers.country as country_module
        original = country_module.CountryService
        country_module.CountryService = lambda db: svc_instance
        try:
            result = get_country(
                country_id=42,
                current_user=_mock_user(),
                db=db,
            )
        finally:
            country_module.CountryService = original

        svc_instance.get_country.assert_called_once_with(42)
        assert result == expected


class TestRouteOrdering:
    """Route ordering in the registered router — /search and /region/{region}
    must appear before /{country_id} to be reachable by FastAPI's matcher."""

    def _route_paths(self):
        from apps.backend.routers.country import router
        return [r.path for r in router.routes]

    def test_search_registered_before_country_id(self):
        paths = self._route_paths()
        search_path = next((p for p in paths if p.endswith("/search")), None)
        id_path = next((p for p in paths if p.endswith("/{country_id}")), None)
        assert search_path is not None, "/search route missing from router"
        assert id_path is not None, "/{country_id} route missing from router"
        assert paths.index(search_path) < paths.index(id_path), (
            "/search must be registered before /{country_id}"
        )

    def test_region_registered_before_country_id(self):
        paths = self._route_paths()
        region_path = next((p for p in paths if p.endswith("/region/{region}")), None)
        id_path = next((p for p in paths if p.endswith("/{country_id}")), None)
        assert region_path is not None, "/region/{region} route missing from router"
        assert id_path is not None, "/{country_id} route missing from router"
        assert paths.index(region_path) < paths.index(id_path), (
            "/region/{region} must be registered before /{country_id}"
        )
