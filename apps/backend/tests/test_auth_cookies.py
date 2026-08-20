"""
Tests for cookie security on auth endpoints (AWD-M-129 split from test_auth_flow_security.py).

Covers: login, refresh, and logout HttpOnly cookie behaviour.
"""

import bcrypt
import pytest
from fastapi import Response

from apps.backend.routers import auth


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_COOKIE_TEST_PASSWORD = "testpassword123"


@pytest.fixture
def hashed_user(sample_user, test_db):
    """Hash a known password onto sample_user and commit.

    Returns the raw password string so tests can use it in login requests.
    Extracted from three identical 5-line blocks (AWD-L-28).
    """
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(_COOKIE_TEST_PASSWORD.encode("utf-8"), salt).decode("utf-8")
    sample_user.password_hash = pw_hash
    test_db.commit()
    return _COOKIE_TEST_PASSWORD


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_login_sets_httponly_cookies(client, sample_user, hashed_user):
    """Test that login sets both access_token and refresh_token as HttpOnly cookies."""
    response = client.post("/api/auth/login", json={"email": sample_user.email, "password": hashed_user})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
    assert response.status_code == 200

    # Both tokens must be present as cookies
    cookies = response.cookies
    assert "access_token" in cookies, "access_token cookie missing from login response"
    assert "refresh_token" in cookies, "refresh_token cookie missing from login response"

    # Verify HttpOnly + SameSite on Set-Cookie headers
    set_cookie_headers = response.headers.get_list("set-cookie") if hasattr(response.headers, "get_list") else [response.headers.get("set-cookie", "")]
    combined = " ".join(set_cookie_headers).lower()
    assert "httponly" in combined
    assert "lax" in combined

    # access_token must NOT appear in the JSON body
    body = response.json()
    assert "access_token" not in body, "access_token must not be returned in the response body"
    assert "user" in body, "user payload missing from login response"


def test_production_auth_cookies_support_cross_site_requests(monkeypatch):
    """Production auth cookies must be accepted on cross-site credentialed fetches."""
    monkeypatch.setattr(auth, "IS_PRODUCTION", True)
    response = Response()

    auth._set_auth_cookies(response, "access", "refresh")

    set_cookie_headers = response.headers.getlist("set-cookie")
    assert len(set_cookie_headers) == 2
    for header in set_cookie_headers:
        assert "HttpOnly" in header
        assert "Secure" in header
        assert "SameSite=none" in header


def test_non_production_auth_cookies_remain_localhost_compatible(monkeypatch):
    monkeypatch.setattr(auth, "IS_PRODUCTION", False)
    response = Response()

    auth._set_auth_cookies(response, "access", "refresh")

    for header in response.headers.getlist("set-cookie"):
        assert "Secure" not in header
        assert "SameSite=lax" in header


def test_refresh_token_flow(client, sample_user, hashed_user):
    """Refresh rotates both cookies; response body contains user but no raw token."""
    # 1. Login to establish cookies
    login_response = client.post("/api/auth/login", json={"email": sample_user.email, "password": hashed_user})
    assert login_response.status_code == 200

    # 2. Call refresh — cookies are forwarded automatically by TestClient
    refresh_response = client.post("/api/auth/refresh")
    if refresh_response.status_code != 200:
        print(f"Refresh failed: {refresh_response.json()}")
    assert refresh_response.status_code == 200

    data = refresh_response.json()
    # Body must contain user + token_type but NOT the raw access_token
    assert "user" in data
    assert data["token_type"] == "bearer"
    assert "access_token" not in data, "access_token must not be returned in refresh response body"

    # Rotated access_token cookie must be present
    assert "access_token" in refresh_response.cookies, "rotated access_token cookie missing"


def test_logout_clears_cookies(client, sample_user, hashed_user):
    """Logout clears both access_token and refresh_token cookies."""
    client.post("/api/auth/login", json={"email": sample_user.email, "password": hashed_user})

    response = client.post("/api/auth/logout")
    assert response.status_code == 200

    # Both cookies must be cleared (empty value or Max-Age=0)
    set_cookie = response.headers.get("set-cookie", "")
    assert (
        'access_token=""' in set_cookie
        or "Max-Age=0" in set_cookie
        or "Expires=" in set_cookie
    ), f"Cookies not cleared — Set-Cookie: {set_cookie}"
