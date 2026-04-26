"""
Users Router for Awade API

This module provides endpoints for user management, including profile updates,
user search, and user administration. It delegates business logic to the UserService
for clean separation of concerns.

Endpoints:
- /api/users: Get all users with filtering
- /api/users/me/data-export: GDPR data export for the authenticated user (GRC-02)
- /api/users/me: Delete own account with full data cascade (GRC-03)
- /api/users/{user_id}: Get specific user
- /api/users/{user_id}: Update user profile
- /api/users/{user_id}: Delete user
- /api/users/{user_id}/profile: Get user profile
- /api/users/{user_id}/profile: Update user profile

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

from apps.backend.database import get_db
from apps.backend.limiter import limiter
from apps.backend.models import User, UserRole
from apps.backend.dependencies import get_current_active_user, get_current_user, require_admin, require_admin_or_educator
from apps.backend.services.user_service import UserService
from apps.backend.schemas.users import UserResponse, UserUpdate, UserProfileResponse

router = APIRouter(prefix="/api/users", tags=["users"])

# NOTE: /me/... routes MUST be declared before /{user_id}/... routes so FastAPI
# does not attempt to parse the literal string "me" as an integer user_id.

@router.get("/me/data-export")
@limiter.limit("5/minute")
async def export_my_data(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    GDPR data export — returns a JSON document containing all data Awade
    holds about the authenticated user.

    For PARENT users the response includes child profiles and all associated
    AI-generated guides.  Password hashes and profile image blobs are
    intentionally excluded from the export.

    All authenticated roles are permitted to export their own data.
    """
    service = UserService(db)
    return service.get_data_export(current_user)


@router.delete("/me")
@limiter.limit("3/minute")
async def delete_my_account(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    GDPR account deletion (GRC-03) — permanently delete the authenticated
    user's own account together with all dependent data:

    - PARENT users: all ChildProfile records and their associated ParentGuide records
    - EDUCATOR users: all LessonPlan records (and their resources / contexts)

    The response is a plain ``{"message": "Account deleted successfully"}`` body.
    Callers should treat the returned 200 as a signal to clear local auth state
    and redirect to the landing page.

    Rate-limited to 3 requests / minute as an extra guard against accidental
    or automated mass-deletion attempts.
    """
    service = UserService(db)
    return service.delete_account(current_user)


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
    Requires authentication; caller must own the record or hold ADMIN/SUPER_ADMIN role.
    """
    service = UserService(db)
    return service.get_user(user_id, current_user)

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