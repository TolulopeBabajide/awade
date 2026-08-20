"""
Authentication and Authorization Dependencies

This module provides FastAPI dependencies for handling user authentication and authorization.
It includes JWT token validation, user session management, and role-based access control.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
import os
from datetime import datetime

from apps.backend.database import get_db
from apps.backend.models import User, UserRole

# Security scheme for JWT tokens — auto_error=False so the dependency does not
# immediately reject requests that carry the token in an HttpOnly cookie instead
# of an Authorization header.
security = HTTPBearer(auto_error=False)

# Environments in which a "dev-secret" JWT fallback is tolerated.  Allocated
# once at import time instead of inside get_jwt_secret_key() to avoid repeated
# set construction on every authenticated request.
_SAFE_FALLBACK_ENVIRONMENTS: frozenset[str] = frozenset(
    {"development", "test", "testing"}
)


def get_jwt_secret_key() -> str:
    """Get JWT secret key from environment variables.

    The dev-secret fallback is only permitted when ENVIRONMENT is one of the
    explicit safe values: "development", "test", or "testing".  Any other value
    — including "staging", "preview", or an unrecognised string — raises
    RuntimeError so that a misconfigured server fails loudly rather than
    silently accepting forged JWTs signed with the well-known dev-secret.

    Raises:
        RuntimeError: If JWT_SECRET_KEY is unset and ENVIRONMENT is not in the
            safe-fallback allowlist {"development", "test", "testing"}.
    """
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        environment = os.getenv("ENVIRONMENT", "development")
        if environment not in _SAFE_FALLBACK_ENVIRONMENTS:
            raise RuntimeError(
                f"JWT_SECRET_KEY environment variable is required when "
                f"ENVIRONMENT='{environment}'. "
                "Set a strong random secret before starting the server. "
                "The dev-secret fallback is only allowed when ENVIRONMENT is "
                "one of: development, test, testing."
            )
        # Development / testing fallback — never safe for production or staging.
        secret = "dev-secret"
    return secret

def get_jwt_algorithm() -> str:
    """
    Get JWT algorithm for token signing and verification.
    
    Returns:
        str: The JWT algorithm used for token operations (currently "HS256")
        
    Note:
        This function returns a hardcoded algorithm for consistency.
        In production, this could be made configurable via environment variables.
    """
    return "HS256"

def verify_jwt_token(token: str) -> dict:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        secret_key = get_jwt_secret_key()
        algorithm = get_jwt_algorithm()
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, jwt.DecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.

    Accepts the token via:
    1. ``Authorization: Bearer <token>`` header (API clients, Swagger UI)
    2. ``access_token`` HttpOnly cookie (browser-based clients)

    Args:
        request: Incoming FastAPI request (used to read cookies)
        credentials: Optional HTTP authorization credentials
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If no token is present, or the token is invalid/expired
    """
    token: Optional[str] = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_jwt_token(token)

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.user_id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Expose user_id on request.state so AuditMiddleware can attribute the
    # request after call_next() returns (OWASP A09 / AWD-M-197).
    request.state.user_id = user.user_id

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user

    Raises:
        HTTPException: If the user account has been suspended
    """
    if current_user.is_suspended:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended",
        )
    return current_user

def require_role(required_role: UserRole):
    """
    Dependency factory for role-based authorization.
    
    Args:
        required_role: Required user role
        
    Returns:
        function: Dependency function that checks user role
    """
    def check_role(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )
        return current_user
    
    return check_role

def require_roles(required_roles: list[UserRole]):
    """
    Dependency factory for multiple role authorization.
    
    Args:
        required_roles: List of required user roles
        
    Returns:
        function: Dependency function that checks user role
    """
    def check_roles(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied."
            )
        return current_user
    
    return check_roles

# Convenience dependencies for common role requirements
require_super_admin = require_role(UserRole.SUPER_ADMIN)
require_admin = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN])
require_educator = require_role(UserRole.EDUCATOR)
require_parent = require_roles([UserRole.PARENT, UserRole.ADMIN, UserRole.SUPER_ADMIN])
require_admin_or_educator = require_roles([UserRole.ADMIN, UserRole.SUPER_ADMIN, UserRole.EDUCATOR])
require_any_role = require_roles([UserRole.EDUCATOR, UserRole.PARENT, UserRole.ADMIN, UserRole.SUPER_ADMIN])

async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work both with and without authentication.

    Accepts the token via:
    1. ``Authorization: Bearer <token>`` header (API clients, Swagger UI)
    2. ``access_token`` HttpOnly cookie (browser-based clients)

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    try:
        token: Optional[str] = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = request.cookies.get("access_token")

        if not token:
            return None

        payload = verify_jwt_token(token)

        user_id = payload.get("sub")
        if user_id is None:
            return None

        return db.query(User).filter(User.user_id == int(user_id)).first()
    except Exception:
        return None