from fastapi import FastAPI, Request
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

@app.get("/api/test-audit-with-user")
async def route_audit_with_user(request: Request):
    # Simulate what get_current_user does: set user_id on request.state
    request.state.user_id = 42
    return {"message": "audit me with user"}

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

def test_audit_middleware_records_user_id_when_set_by_dependency():
    """AWD-M-197: user_id is recorded when get_current_user sets request.state.user_id."""
    with patch("apps.backend.middleware.audit.audit_logger") as mock_logger:
        client.get("/api/test-audit-with-user")

        assert mock_logger.info.called
        log_json = json.loads(mock_logger.info.call_args[0][0])
        assert log_json["user_id"] == 42

def test_audit_middleware_records_null_user_id_for_unauthenticated():
    """AWD-M-197: user_id is null when request is unauthenticated (no state set)."""
    with patch("apps.backend.middleware.audit.audit_logger") as mock_logger:
        client.get("/api/test-audit")

        assert mock_logger.info.called
        log_json = json.loads(mock_logger.info.call_args[0][0])
        assert log_json["user_id"] is None
