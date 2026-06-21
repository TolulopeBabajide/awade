import pytest
from fastapi.testclient import TestClient

from apps.backend.main import app

client = TestClient(app)


def test_metrics_endpoint_exists():
    """Test that /metrics endpoint is exposed and returns Prometheus data."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text or "http_requests_total" in response.text


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
