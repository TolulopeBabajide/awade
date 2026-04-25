from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock
import sys

# Mock prometheus_fastapi_instrumentator if not installed
try:
    from prometheus_fastapi_instrumentator import Instrumentator
except ImportError:
    # Create a dummy mock to allow import of main.py
    sys.modules["prometheus_fastapi_instrumentator"] = MagicMock()
    Instrumentator = MagicMock()
    Instrumentator.return_value.instrument.return_value.expose.return_value = None

from apps.backend.main import app

client = TestClient(app)

def test_metrics_endpoint_exists():
    """Test that /metrics endpoint is exposed (if instrumentator is active)."""
    # If using the mock, this test might not find the route if the mock didn't add it.
    # But if real module is installed, it should work.
    
    # Check if we are running with real instrumentator
    is_real = "prometheus_fastapi_instrumentator" in sys.modules and not isinstance(sys.modules["prometheus_fastapi_instrumentator"], MagicMock)
    
    if is_real:
        response = client.get("/metrics")
        # Just check it exists and returns text (Prometheus format)
        assert response.status_code == 200
        assert "http_requests_total" in response.text or "# HELP" in response.text
    else:
        pytest.skip("Prometheus Instrumentator not installed, skipping metrics test")
