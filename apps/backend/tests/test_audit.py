from fastapi import FastAPI
from fastapi.testclient import TestClient
from apps.backend.middleware.audit import AuditMiddleware
import logging
import json
import pytest
from unittest.mock import patch, MagicMock

# Setup simple app for testing middleware
app = FastAPI()
app.add_middleware(AuditMiddleware)

@app.get("/api/test-audit")
async def route_audit():
    return {"message": "audit me"}

@app.get("/health")
async def health():
    return {"status": "ok"}

client = TestClient(app)

def test_audit_middleware_logs_api_request():
    """Test that API requests are logged."""
    with patch("apps.backend.middleware.audit.audit_logger") as mock_logger:
        client.get("/api/test-audit")
        
        # Verify log call
        assert mock_logger.info.called
        
        # Verify log content
        log_json = json.loads(mock_logger.info.call_args[0][0])
        assert log_json["path"] == "/api/test-audit"
        assert log_json["method"] == "GET"
        assert log_json["event_type"] == "api_access"
        assert "timestamp" in log_json
        assert "process_time_ms" in log_json

def test_audit_middleware_ignores_health_check():
    """Test that health checks are NOT logged."""
    with patch("apps.backend.middleware.audit.audit_logger") as mock_logger:
        client.get("/health")
        assert not mock_logger.info.called
