from fastapi.testclient import TestClient

from apps.backend.main import app

client = TestClient(app)


def test_metrics_endpoint_exists():
    """Test that /metrics endpoint is exposed and returns Prometheus data."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "# HELP" in response.text or "http_requests_total" in response.text
