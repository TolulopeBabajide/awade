import logging
import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app

client = TestClient(app)


def test_metrics_endpoint_exists():
    """Test that /metrics endpoint is exposed and returns Prometheus data."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text and "http_requests_total" in response.text


class TestPfiMonkeyPatchGuardH131:
    def test_pfi_routing_has_get_route_name_attribute(self):
        """CI sentinel: fails if pfi renames _get_route_name, surfacing AWD-H-131 shim breakage."""
        pfi_routing = pytest.importorskip(
            "prometheus_fastapi_instrumentator.routing",
            reason="prometheus-fastapi-instrumentator not installed",
        )
        assert hasattr(pfi_routing, "_get_route_name"), (
            "pfi internals changed: _get_route_name no longer exists — update AWD-H-131 shim in main.py"
        )


class TestPfiMonkeyPatchGuardOptimizeM284:
    def test_guard_raises_runtime_error_when_attribute_missing(self, monkeypatch):
        """Guard raises RuntimeError (not assert) so it survives -O and propagates at startup.

        Covers AWD-M-284 (RuntimeError not assert) and AWD-M-280 (error propagates
        through the ImportError guard — _check_pfi_routing_compat is called outside
        the except ImportError block).
        """
        import prometheus_fastapi_instrumentator.routing as pfi_routing
        from apps.backend import main as main_module
        monkeypatch.delattr(pfi_routing, "_get_route_name")
        with pytest.raises(RuntimeError, match="pfi internals changed"):
            main_module._check_pfi_routing_compat()


class TestPrometheusImportErrorGuardM280:
    def test_pfi_available_flag_set_when_installed(self):
        """_pfi_available is True when prometheus-fastapi-instrumentator is importable (AWD-M-280)."""
        pytest.importorskip(
            "prometheus_fastapi_instrumentator",
            reason="prometheus-fastapi-instrumentator not installed",
        )
        from apps.backend import main as main_module
        assert getattr(main_module, "_pfi_available", None) is True


class TestPfiRouteNameCompatMetricsGapM281:
    """logger.warning emitted when _IncludedRouter lacks callable effective_candidates (AWD-M-281)."""

    def _make_no_path_route(self, candidates_value):
        """Return a mock route that matches FULL but has no .path attribute."""
        from starlette.routing import Match

        class FakeIncludedRouter:
            def matches(self, scope):
                return Match.FULL, {}

        route = FakeIncludedRouter()
        if candidates_value is not None:
            # Set on the instance to avoid Python binding a callable class attribute
            # as a bound method (which would add an unexpected `self` argument).
            route.effective_candidates = candidates_value
        return route

    def test_warns_when_effective_candidates_absent(self, caplog):
        pytest.importorskip(
            "prometheus_fastapi_instrumentator",
            reason="prometheus-fastapi-instrumentator not installed",
        )
        from apps.backend import main as main_module

        route = self._make_no_path_route(None)
        with caplog.at_level(logging.WARNING, logger="apps.backend.main"):
            result = main_module._pfi_get_route_name_compat({}, [route])
        assert result is None
        assert any(
            "_pfi_compat" in r.message and "metrics gap" in r.message
            for r in caplog.records
        )

    def test_warns_when_effective_candidates_not_callable(self, caplog):
        pytest.importorskip(
            "prometheus_fastapi_instrumentator",
            reason="prometheus-fastapi-instrumentator not installed",
        )
        from apps.backend import main as main_module

        route = self._make_no_path_route("not_callable")
        with caplog.at_level(logging.WARNING, logger="apps.backend.main"):
            result = main_module._pfi_get_route_name_compat({}, [route])
        assert result is None
        assert any(
            "_pfi_compat" in r.message and "metrics gap" in r.message
            for r in caplog.records
        )

    def test_no_warning_when_effective_candidates_callable(self, caplog):
        pytest.importorskip(
            "prometheus_fastapi_instrumentator",
            reason="prometheus-fastapi-instrumentator not installed",
        )
        from apps.backend import main as main_module

        route = self._make_no_path_route(lambda: [])
        with caplog.at_level(logging.WARNING, logger="apps.backend.main"):
            result = main_module._pfi_get_route_name_compat({}, [route])
        assert result is None
        assert not any(
            "_pfi_compat" in r.message and "metrics gap" in r.message
            for r in caplog.records
        )
