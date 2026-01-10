
import pytest
import bcrypt
import json
from unittest.mock import AsyncMock, patch, MagicMock
from apps.backend.services.auth_service import AuthService
from packages.ai.gpt_service import AwadeGPTService
from apps.backend.main import app

@pytest.mark.asyncio
async def test_refresh_token_rotation(client, sample_user, test_db):
    """Test that refresh token is rotated on every refresh."""
    # Setup user
    password = "testpassword123"
    sample_user.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    test_db.commit()

    # 1. Login to get initial refresh token
    login_data = {"email": sample_user.email, "password": password}
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    first_refresh_token = login_response.cookies.get("refresh_token")
    assert first_refresh_token is not None

    # 2. Refresh to get rotated token
    # Mock redis check
    with patch("apps.backend.services.auth_service.AuthService.is_refresh_token_blacklisted", new_callable=AsyncMock) as mock_blacklist:
        mock_blacklist.return_value = False
        
        refresh_response = client.post("/api/auth/refresh")
        assert refresh_response.status_code == 200
        
        second_refresh_token = refresh_response.cookies.get("refresh_token")
        
        # Verify Rotation: new token should be different from the first one
        assert second_refresh_token is not None
        assert second_refresh_token != first_refresh_token

@pytest.mark.asyncio
async def test_token_revocation_on_logout(client, sample_user, test_db):
    """Test that logout blacklists the token and prevents subsequent refresh."""
    # Setup user
    password = "testpassword123"
    sample_user.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    test_db.commit()

    # 1. Login
    login_data = {"email": sample_user.email, "password": password}
    client.post("/api/auth/login", json=login_data)
    refresh_token = client.cookies.get("refresh_token")
    assert refresh_token is not None

    # 2. Logout (should trigger blacklisting)
    with patch("apps.backend.services.auth_service.AuthService.blacklist_refresh_token", new_callable=AsyncMock) as mock_blacklist:
        # Mock app.state.redis so the router calls blacklist_refresh_token
        old_redis = getattr(app.state, "redis", None)
        app.state.redis = MagicMock()
        try:
            logout_response = client.post("/api/auth/logout")
            assert logout_response.status_code == 200
            mock_blacklist.assert_called_once()
        finally:
            app.state.redis = old_redis

    # 3. Try to refresh using the "revoked" token (simulated by mock)
    with patch("apps.backend.services.auth_service.AuthService.is_refresh_token_blacklisted", new_callable=AsyncMock) as mock_is_blacklisted:
        mock_is_blacklisted.return_value = True
        # Manually set the revoked cookie back because logout cleared it
        client.cookies.set("refresh_token", refresh_token)
        refresh_response = client.post("/api/auth/refresh")
        
        assert refresh_response.status_code == 401
        assert "revoked" in refresh_response.json()["detail"].lower()

def test_ai_safety_filters_input_sanitization():
    """Test that sensitive data is removed from AI prompts."""
    service = AwadeGPTService(api_key="test-key")
    dirty_input = "Contact me at teacher@example.com or call +2348012345678. My key is sk-1234567890abcdef1234567890abcdef"
    sanitized = service._sanitize_input(dirty_input)
    
    assert "teacher@example.com" not in sanitized
    assert "[REDACTED_EMAIL]" in sanitized
    assert "+2348012345678" not in sanitized
    assert "[REDACTED_PHONE]" in sanitized
    assert "sk-1234567890abcdef1234567890abcdef" not in sanitized
    assert "[REDACTED_KEY]" in sanitized

def test_ai_safety_filters_output_validation():
    """Test that AI output is validated for structure and harmful content."""
    service = AwadeGPTService(api_key="test-key")
    
    # Valid output
    valid_content = json.dumps({
        "title_header": {"topic": "Math"},
        "learning_objectives": ["Obj 1"],
        "lesson_content": {"introduction": "Hello"}
    })
    assert service._validate_output(valid_content) is True
    
    # Missing required fields
    invalid_structure = json.dumps({
        "title_header": {"topic": "Math"}
    })
    assert service._validate_output(invalid_structure) is False
    
    # Harmful pattern detection (using example harmful words from code)
    harmful_content = json.dumps({
        "title_header": {"topic": "Math"},
        "learning_objectives": ["This lesson contains badword1"],
        "lesson_content": {"introduction": "Hello"}
    })
    assert service._validate_output(harmful_content) is False

@pytest.mark.asyncio
async def test_rate_limiting_enforcement(client):
    """Test that rate limiting blocks excessive requests (429)."""
    # Note: We'll hit the login endpoint which has a limit of 10/minute
    # we use a loop to exceed the limit.
    # We might need to handle the fact that TestClient is fast.
    
    responses = []
    for i in range(12):
        # We don't care about the content, just the status
        resp = client.post("/api/auth/login", json={"email": f"test{i}@example.com", "password": "any"})
        responses.append(resp.status_code)
    
    # At least one of the later requests should be 429
    assert 429 in responses
