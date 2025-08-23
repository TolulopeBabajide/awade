"""
Users Router for Awade API

This module provides endpoints for user management, including profile updates,
user search, and user administration. It delegates business logic to the UserService
for clean separation of concerns.

Endpoints:
- /api/users: Get all users with filtering
- /api/users/{user_id}: Get specific user
- /api/users/{user_id}: Update user profile
- /api/users/{user_id}: Delete user
- /api/users/{user_id}/profile: Get user profile
- /api/users/{user_id}/profile: Update user profile

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from apps.backend.database import get_db
from apps.backend.models import User, UserRole
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator
from apps.backend.services.user_service import UserService
from apps.backend.schemas.users import UserResponse, UserUpdate, UserProfileResponse

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    country: Optional[str] = Query(None, description="Filter by country"),
    search: Optional[str] = Query(None, description="Search in name and email"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get users with optional filtering and search.
    Requires admin authentication.
    """
    service = UserService(db)
    return service.get_users(skip, limit, role, country, search)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    Requires authentication and ownership or admin role.
    """
    service = UserService(db)
    return service.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Update a user profile.
    Requires authentication and ownership or admin role.
    """
    service = UserService(db)
    return service.update_user(user_id, user_data, current_user)

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user.
    Requires admin authentication.
    """
    service = UserService(db)
    return service.delete_user(user_id, current_user)

@router.get("/{user_id}/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Get a user's profile information.
    Requires authentication and ownership or admin role.
    """
    service = UserService(db)
    return service.get_user_profile(user_id, current_user)

@router.put("/{user_id}/profile", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: int,
    profile_data: UserUpdate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Update a user's profile information.
    Requires authentication and ownership or admin role.
    """
    service = UserService(db)
    return service.update_user_profile(user_id, profile_data, current_user) 