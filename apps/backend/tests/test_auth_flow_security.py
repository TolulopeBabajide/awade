
import pytest
import bcrypt
from fastapi.testclient import TestClient

def test_login_sets_httponly_cookie(client, sample_user, test_db):
    """Test that login response includes HttpOnly refresh token cookie."""
    # Update sample_user with valid password hash
    password = "testpassword123"
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    sample_user.password_hash = pw_hash
    test_db.commit()
    
    login_data = {
        "email": sample_user.email,
        "password": password
    }
    
    response = client.post("/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
    assert response.status_code == 200
    
    # Check cookies
    cookies = response.cookies
    assert "refresh_token" in cookies
    
    # Verify cookie attributes
    set_cookie = response.headers.get("set-cookie")
    assert set_cookie is not None
    assert "refresh_token" in set_cookie
    assert "HttpOnly" in set_cookie
    # assert "Secure" in set_cookie # Not in test env
    # Check lax case insensitive
    assert "lax" in set_cookie.lower()

def test_refresh_token_flow(client, sample_user, test_db):
    """Test utilizing the refresh token cookie to get a new access token."""
    # 0. Setup user password
    password = "testpassword123"
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    sample_user.password_hash = pw_hash
    test_db.commit()

    # 1. Login to get cookie
    login_data = {
        "email": sample_user.email,
        "password": password
    }
    login_response = client.post("/api/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    # 2. Call refresh endpoint
    refresh_response = client.post("/api/auth/refresh")
    
    if refresh_response.status_code != 200:
        print(f"Refresh failed: {refresh_response.json()}")
        
    assert refresh_response.status_code == 200
    data = refresh_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
def test_logout_clears_cookie(client, sample_user, test_db):
    """Test that logout endpoint clears the refresh token cookie."""
    # 0. Setup user password
    password = "testpassword123"
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    sample_user.password_hash = pw_hash
    test_db.commit()
    
    # 1. Login
    login_data = {
        "email": sample_user.email,
        "password": "testpassword123"
    }
    client.post("/api/auth/login", json=login_data)
    
    # 2. Logout
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    
    # Check Set-Cookie for deletion
    set_cookie = response.headers.get("set-cookie")
    # Should expire or be empty
    assert 'refresh_token=""' in set_cookie or "Max-Age=0" in set_cookie or "Expires=" in set_cookie
