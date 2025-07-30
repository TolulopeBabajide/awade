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

# Security scheme for JWT tokens
security = HTTPBearer()

def get_jwt_secret_key() -> str:
    """Get JWT secret key from environment variables."""
    return os.getenv("JWT_SECRET_KEY", "dev-secret")

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
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials containing the JWT token
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If user is not found or token is invalid
    """
    token = credentials.credentials
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
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (additional checks can be added here).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Current active user
    """
    # Add any additional checks for user status here
    # For example, check if user is banned, suspended, etc.
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
                detail=f"Access denied. Required role: {required_role.value}"
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
                detail=f"Access denied. Required roles: {[role.value for role in required_roles]}"
            )
        return current_user
    
    return check_roles

# Convenience dependencies for common role requirements
require_admin = require_role(UserRole.ADMIN)
require_educator = require_role(UserRole.EDUCATOR)
require_admin_or_educator = require_roles([UserRole.ADMIN, UserRole.EDUCATOR])

async def get_optional_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work both with and without authentication.
    
    Args:
        request: FastAPI request object
        db: Database session
        
    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = verify_jwt_token(token)
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        user = db.query(User).filter(User.user_id == int(user_id)).first()
        return user
    except Exception:
        return None 