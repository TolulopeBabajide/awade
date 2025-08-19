"""
User Management Router for Awade API

This module provides endpoints for user management operations, including user profile updates,
user listing, profile image uploads, and administrative functions. Most endpoints require admin authentication.

Endpoints:
- /api/users: Get all users (admin only)
- /api/users/profile: Update own profile (authenticated users)
- /api/users/profile/upload-image: Upload profile image (authenticated users)
- /api/users/profile/delete-image: Delete profile image (authenticated users)
- /api/users/{user_id}: Get specific user (admin only)
- /api/users/{user_id}/update: Update user profile (admin or self)
- /api/users/{user_id}/delete: Delete user (admin only)

Author: Tolulope Babajide
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from apps.backend.database import get_db
from apps.backend.dependencies import get_current_user, require_admin, require_admin_or_educator
from apps.backend.models import User, UserRole
from apps.backend.schemas.users import UserResponse, UserUpdate, UserProfileResponse
from apps.backend.services.file_upload_service import file_upload_service

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get all users with optional filtering.
    Requires admin authentication.
    """
    try:
        query = db.query(User)
        
        # Filter by role if specified
        if role:
            try:
                user_role = UserRole(role)
                query = query.filter(User.role == user_role)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid role specified")
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        return [
            UserResponse(
                user_id=user.user_id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                country=user.country,
                region=user.region,
                school_name=user.school_name,
                subjects=json.loads(user.subjects) if user.subjects else None,
                grade_levels=json.loads(user.grade_levels) if user.grade_levels else None,
                languages_spoken=user.languages_spoken,
                profile_image_url=user.profile_image_url,
                phone=user.phone,
                bio=user.bio,
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

# Profile management endpoints (must come before /{user_id} routes)
@router.put("/profile", response_model=UserResponse)
def update_own_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's own profile.
    Requires authentication.
    """
    try:
        # Update user fields
        if user_data.full_name is not None:
            current_user.full_name = user_data.full_name
        if user_data.country is not None:
            current_user.country = user_data.country
        if user_data.region is not None:
            current_user.region = user_data.region
        if user_data.school_name is not None:
            current_user.school_name = user_data.school_name
        if user_data.subjects is not None:
            current_user.subjects = json.dumps(user_data.subjects)
        if user_data.grade_levels is not None:
            current_user.grade_levels = json.dumps(user_data.grade_levels)
        if user_data.languages_spoken is not None:
            current_user.languages_spoken = user_data.languages_spoken
        if user_data.profile_image_url is not None:
            current_user.profile_image_url = user_data.profile_image_url
        if user_data.phone is not None:
            current_user.phone = user_data.phone
        if user_data.bio is not None:
            current_user.bio = user_data.bio
        
        db.commit()
        db.refresh(current_user)
        
        return UserResponse(
            user_id=current_user.user_id,
            email=current_user.email,
            full_name=current_user.full_name,
            role=current_user.role.value,
            country=current_user.country,
            region=current_user.region,
            school_name=current_user.school_name,
            subjects=json.loads(current_user.subjects) if current_user.subjects else None,
            grade_levels=json.loads(current_user.grade_levels) if current_user.grade_levels else None,
            languages_spoken=current_user.languages_spoken,
            profile_image_url=current_user.profile_image_url,
            profile_image_data=current_user.profile_image_data,
            profile_image_type=current_user.profile_image_type,
            phone=current_user.phone,
            bio=current_user.bio,
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
    except Exception as e:
        print(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")

@router.get("/profile", response_model=UserResponse)
def get_own_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's own profile.
    Requires authentication.
    """
    return UserResponse(
        user_id=current_user.user_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value,
        country=current_user.country,
        region=current_user.region,
        school_name=current_user.school_name,
        subjects=json.loads(current_user.subjects) if current_user.subjects else None,
        grade_levels=json.loads(current_user.grade_levels) if current_user.grade_levels else None,
        languages_spoken=current_user.languages_spoken,
        profile_image_url=current_user.profile_image_url,
        profile_image_data=current_user.profile_image_data,
        profile_image_type=current_user.profile_image_type,
        phone=current_user.phone,
        bio=current_user.bio,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/profile/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a profile image for the current user.
    Requires authentication.
    """
    try:
        # Delete old profile image data if it exists
        if current_user.profile_image_data:
            await file_upload_service.delete_profile_image(current_user.profile_image_data)
        
        # Process and store new image in database
        base64_data, mime_type, file_extension = await file_upload_service.save_profile_image(file, current_user.user_id)
        
        # Update user profile with image data
        current_user.profile_image_data = base64_data
        current_user.profile_image_type = mime_type
        current_user.profile_image_url = None  # Clear old URL since we're storing data directly
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Profile image uploaded successfully",
            "profile_image_data": base64_data,
            "profile_image_type": mime_type
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading profile image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading profile image: {str(e)}")

@router.delete("/profile/delete-image")
async def delete_profile_image(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete the current user's profile image.
    Requires authentication.
    """
    try:
        if not current_user.profile_image_data:
            raise HTTPException(status_code=404, detail="No profile image to delete")
        
        # Clear image data from database
        current_user.profile_image_data = None
        current_user.profile_image_type = None
        current_user.profile_image_url = None
        
        db.commit()
        db.refresh(current_user)
        
        return {"message": "Profile image deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting profile image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting profile image: {str(e)}")

# User management endpoints (admin only)
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID.
    Requires admin authentication.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            country=user.country,
            region=user.region,
            school_name=user.school_name,
            subjects=json.loads(user.subjects) if user.subjects else None,
            grade_levels=json.loads(user.grade_levels) if user.grade_levels else None,
            languages_spoken=user.languages_spoken,
            profile_image_url=user.profile_image_url,
            profile_image_data=user.profile_image_data,
            profile_image_type=user.profile_image_type,
            phone=user.phone,
            bio=user.bio,
            created_at=user.created_at,
            last_login=user.last_login
        )
    except Exception as e:
        print(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_admin_or_educator),
    db: Session = Depends(get_db)
):
    """
    Update a user's profile.
    Requires admin authentication or the user updating their own profile.
    """
    try:
        # Check if user exists
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if current user is admin or updating their own profile
        if current_user.role != UserRole.ADMIN and current_user.user_id != user_id:
            raise HTTPException(
                status_code=403, 
                detail="You can only update your own profile"
            )
        
        # Update user fields
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        if user_data.country is not None:
            user.country = user_data.country
        if user_data.region is not None:
            user.region = user_data.region
        if user_data.school_name is not None:
            user.school_name = user_data.school_name
        if user_data.subjects is not None:
            user.subjects = json.dumps(user_data.subjects)
        if user_data.grade_levels is not None:
            user.grade_levels = json.dumps(user_data.grade_levels)
        if user_data.languages_spoken is not None:
            user.languages_spoken = user_data.languages_spoken
        if user_data.profile_image_url is not None:
            user.profile_image_url = user_data.profile_image_url
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.bio is not None:
            user.bio = user_data.bio
        
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            country=user.country,
            region=user.region,
            school_name=user.school_name,
            subjects=json.loads(user.subjects) if user.subjects else None,
            grade_levels=json.loads(user.grade_levels) if user.grade_levels else None,
            languages_spoken=user.languages_spoken,
            profile_image_url=user.profile_image_url,
            profile_image_data=user.profile_image_data,
            profile_image_type=user.profile_image_type,
            phone=user.phone,
            bio=user.bio,
            created_at=user.created_at,
            last_login=user.last_login
        )
    except Exception as e:
        print(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Delete a user.
    Requires admin authentication.
    """
    try:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent admin from deleting themselves
        if current_user.user_id == user_id:
            raise HTTPException(
                status_code=400, 
                detail="You cannot delete your own account"
            )
        
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}") 