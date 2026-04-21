
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


# ---------------------------------------------------------------------------
# H-05: Account enumeration protection
# ---------------------------------------------------------------------------

class TestAccountEnumerationProtection:
    """Verify login endpoint does not leak whether an email address is registered."""

    def test_unknown_email_returns_generic_error(self, client):
        """Attempting login with a non-existent email must return 401 with generic message."""
        response = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "SomePassword1!"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_wrong_password_returns_generic_error(self, client, sample_user, test_db):
        """Attempting login with wrong password returns 401 with same generic message."""
        import bcrypt as _bcrypt
        salt = _bcrypt.gensalt()
        sample_user.password_hash = _bcrypt.hashpw(b"CorrectPass1!", salt).decode("utf-8")
        test_db.commit()

        response = client.post("/api/auth/login", json={
            "email": sample_user.email,
            "password": "WrongPass999!"
        })
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid email or password"

    def test_google_oauth_account_returns_generic_error(self, client, test_db):
        """Attempting password login on a Google-OAuth-only account must return the SAME
        generic message as an unknown email — prevents enumeration via auth-method disclosure."""
        import datetime, pytz
        from apps.backend.models import User, UserRole

        oauth_user = User(
            email="google_only@example.com",
            password_hash="google-oauth",
            full_name="Google User",
            role=UserRole.PARENT,
            country="NG",
            created_at=datetime.datetime.now(pytz.UTC),
        )
        test_db.add(oauth_user)
        test_db.commit()

        response = client.post("/api/auth/login", json={
            "email": "google_only@example.com",
            "password": "AnyPassword1!"
        })
        assert response.status_code == 401
        # Must be IDENTICAL to the message returned for unknown emails
        assert response.json()["detail"] == "Invalid email or password", (
            "Google OAuth account must not reveal its existence via a distinct error message"
        )
