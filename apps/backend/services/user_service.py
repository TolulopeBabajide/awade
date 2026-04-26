"""
User Service for Awade

This module provides service methods for user management, including profile updates,
user search, and user administration. It handles all business logic related to users,
separating concerns from the router layer.

Author: Tolulope Babajide
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import HTTPException, status
import json
import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

import logging

from apps.backend.models import User, UserRole, ChildProfile, ParentGuide, Topic
from apps.backend.schemas.users import UserUpdate, UserResponse, UserProfileResponse

logger = logging.getLogger(__name__)

class UserService:
    """Service class for user operations."""
    
    def __init__(self, db: Session):
        """
        Initialize the UserService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        role: Optional[UserRole] = None,
        country: Optional[str] = None,
        search: Optional[str] = None
    ) -> List[UserResponse]:
        """
        Get users with optional filtering and search.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            role (Optional[UserRole]): Filter by user role
            country (Optional[str]): Filter by country
            search (Optional[str]): Search in name and email
            
        Returns:
            List[UserResponse]: List of user responses
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            query = self.db.query(User)
            
            # Apply filters
            if role:
                query = query.filter(User.role == role)
            if country:
                query = query.filter(User.country == country)
            if search:
                search_filter = or_(
                    User.full_name.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%")
                )
                query = query.filter(search_filter)
            
            # Apply pagination
            users = query.offset(skip).limit(limit).all()
            
            return [self._create_user_response(user) for user in users]
            
        except Exception:
            logger.error("Failed to retrieve users", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving users"
            )
    
    def get_user(self, user_id: int, current_user: User) -> UserResponse:
        """
        Get a specific user by ID.

        Users may only retrieve their own record. ADMIN and SUPER_ADMIN may
        retrieve any record.

        Args:
            user_id (int): User ID
            current_user (User): The authenticated caller

        Returns:
            UserResponse: User response

        Raises:
            HTTPException: 403 if caller lacks ownership/admin role, 404 if not found
        """
        try:
            if (
                current_user.user_id != user_id
                and current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN)
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own profile",
                )

            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            return self._create_user_response(user)

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Failed to retrieve user %s", user_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving the user",
            )
    
    def update_user(self, user_id: int, user_data: UserUpdate, current_user: User) -> UserResponse:
        """
        Update a user profile.
        
        Args:
            user_id (int): User ID to update
            user_data (UserUpdate): Update data
            current_user (User): Current authenticated user
            
        Returns:
            UserResponse: Updated user response
            
        Raises:
            HTTPException: If update fails or access denied
        """
        try:
            # Check if user can update this profile
            if current_user.user_id != user_id and current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
                raise HTTPException(
                    status_code=403,
                    detail="You can only update your own profile"
                )

            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Update user fields
            update_data = user_data.dict(exclude_unset=True)
            
            # Handle JSON fields
            if 'subjects' in update_data and update_data['subjects'] is not None:
                update_data['subjects'] = json.dumps(update_data['subjects'])
            if 'grade_levels' in update_data and update_data['grade_levels'] is not None:
                update_data['grade_levels'] = json.dumps(update_data['grade_levels'])
            
            for field, value in update_data.items():
                setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            return self._create_user_response(user)
            
        except HTTPException:
            raise
        except Exception:
            logger.error("Failed to update user %s", user_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while updating the user"
            )
    
    def delete_user(self, user_id: int, current_user: User) -> Dict[str, str]:
        """
        Delete a user.
        
        Args:
            user_id (int): User ID to delete
            current_user (User): Current authenticated user
            
        Returns:
            Dict[str, str]: Success message
            
        Raises:
            HTTPException: If deletion fails or access denied
        """
        try:
            # Only admins and super admins can delete users
            if current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
                raise HTTPException(
                    status_code=403,
                    detail="Only administrators can delete users"
                )
            
            # Prevent self-deletion
            if current_user.user_id == user_id:
                raise HTTPException(
                    status_code=400,
                    detail="You cannot delete your own account"
                )
            
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            self.db.delete(user)
            self.db.commit()
            
            return {"message": "User deleted successfully"}
            
        except HTTPException:
            raise
        except Exception:
            logger.error("Failed to delete user %s", user_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while deleting the user"
            )
    
    def get_user_profile(self, user_id: int, current_user: User) -> UserProfileResponse:
        """
        Get a user's profile information.
        
        Args:
            user_id (int): User ID
            current_user (User): Current authenticated user
            
        Returns:
            UserProfileResponse: User profile response
            
        Raises:
            HTTPException: If user not found or access denied
        """
        try:
            # Users can view their own profile, admins and super admins can view any profile
            if current_user.user_id != user_id and current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
                raise HTTPException(
                    status_code=403,
                    detail="You can only view your own profile"
                )
            
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return self._create_user_profile_response(user)
            
        except HTTPException:
            raise
        except Exception:
            logger.error("Failed to retrieve user profile %s", user_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while retrieving the user profile"
            )
    
    def update_user_profile(self, user_id: int, profile_data: UserUpdate, current_user: User) -> UserProfileResponse:
        """
        Update a user's profile information.
        
        Args:
            user_id (int): User ID to update
            profile_data (UserUpdate): Profile update data
            current_user (User): Current authenticated user
            
        Returns:
            UserProfileResponse: Updated user profile response
            
        Raises:
            HTTPException: If update fails or access denied
        """
        try:
            # Users can update their own profile, admins and super admins can update any profile
            if current_user.user_id != user_id and current_user.role not in (UserRole.ADMIN, UserRole.SUPER_ADMIN):
                raise HTTPException(
                    status_code=403,
                    detail="You can only update your own profile"
                )
            
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Update profile fields
            update_data = profile_data.dict(exclude_unset=True)
            
            # Handle JSON fields
            if 'subjects' in update_data and update_data['subjects'] is not None:
                update_data['subjects'] = json.dumps(update_data['subjects'])
            if 'grade_levels' in update_data and update_data['grade_levels'] is not None:
                update_data['grade_levels'] = json.dumps(update_data['grade_levels'])
            
            for field, value in update_data.items():
                setattr(user, field, value)
            
            self.db.commit()
            self.db.refresh(user)
            
            return self._create_user_profile_response(user)
            
        except HTTPException:
            raise
        except Exception:
            logger.error("Failed to update user profile %s", user_id, exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An error occurred while updating the user profile"
            )
    
    def get_data_export(self, current_user: User) -> Dict[str, Any]:
        """
        Produce a full GDPR data export for the authenticated user.

        Returns a JSON-serialisable dict containing the caller's profile data
        and, for PARENT users, all child profiles with their associated
        AI-generated guides.  Password hashes and internal image blobs are
        intentionally excluded.

        Args:
            current_user (User): The authenticated user requesting the export.

        Returns:
            Dict[str, Any]: Structured export payload.

        Raises:
            HTTPException: 500 if export assembly fails.
        """
        try:
            from datetime import timezone as _tz

            def _fmt(dt: Optional[datetime]) -> Optional[str]:
                """ISO-8601 string with UTC marker, or None."""
                if dt is None:
                    return None
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=_tz.utc)
                return dt.isoformat()

            # --- user profile (no password_hash, no image blobs) ---
            subjects_list: Optional[List[str]] = None
            grade_levels_list: Optional[List[str]] = None

            if current_user.subjects:
                try:
                    subjects_list = json.loads(current_user.subjects)
                except (json.JSONDecodeError, TypeError):
                    subjects_list = None

            if current_user.grade_levels:
                try:
                    grade_levels_list = json.loads(current_user.grade_levels)
                except (json.JSONDecodeError, TypeError):
                    grade_levels_list = None

            user_data: Dict[str, Any] = {
                "user_id": current_user.user_id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role.value,
                "country": current_user.country,
                "region": current_user.region,
                "school_name": current_user.school_name,
                "subjects": subjects_list,
                "grade_levels": grade_levels_list,
                "languages_spoken": current_user.languages_spoken,
                "phone": current_user.phone,
                "bio": current_user.bio,
                "created_at": _fmt(current_user.created_at),
                "last_login": _fmt(current_user.last_login),
            }

            # --- children + guides (PARENT only) ---
            children_data: List[Dict[str, Any]] = []
            if current_user.role == UserRole.PARENT:
                children = (
                    self.db.query(ChildProfile)
                    .filter(ChildProfile.parent_id == current_user.user_id)
                    .order_by(ChildProfile.child_id)
                    .all()
                )
                for child in children:
                    child_subjects: Optional[List] = None
                    if child.subjects:
                        try:
                            child_subjects = json.loads(child.subjects)
                        except (json.JSONDecodeError, TypeError):
                            child_subjects = None

                    guides = (
                        self.db.query(ParentGuide)
                        .filter(ParentGuide.child_id == child.child_id)
                        .order_by(ParentGuide.guide_id)
                        .all()
                    )
                    guides_data: List[Dict[str, Any]] = []
                    for guide in guides:
                        topic_title: Optional[str] = None
                        topic = (
                            self.db.query(Topic)
                            .filter(Topic.topic_id == guide.topic_id)
                            .first()
                        )
                        if topic:
                            topic_title = topic.topic_title

                        guides_data.append({
                            "guide_id": guide.guide_id,
                            "topic_id": guide.topic_id,
                            "topic_title": topic_title,
                            "ai_generated_content": guide.ai_generated_content,
                            "user_edited_content": guide.user_edited_content,
                            "is_bookmarked": bool(guide.is_bookmarked),
                            "created_at": _fmt(guide.created_at),
                            "updated_at": _fmt(guide.updated_at),
                        })

                    children_data.append({
                        "child_id": child.child_id,
                        "name": child.name,
                        "age": child.age,
                        "school_name": child.school_name,
                        "country_id": child.country_id,
                        "curricula_id": child.curricula_id,
                        "grade_level_id": child.grade_level_id,
                        "subjects": child_subjects,
                        "created_at": _fmt(child.created_at),
                        "updated_at": _fmt(child.updated_at),
                        "guides": guides_data,
                    })

            return {
                "export_date": _fmt(datetime.now()),
                "user": user_data,
                "children": children_data,
            }

        except HTTPException:
            raise
        except Exception:
            logger.error(
                "Failed to assemble data export for user %s",
                current_user.user_id,
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail="An error occurred while generating the data export",
            )

    def _create_user_response(self, user: User) -> UserResponse:
        """
        Create a user response from a User model.
        
        Args:
            user (User): User model instance
            
        Returns:
            UserResponse: User response object
        """
        try:
            # Parse JSON strings back to lists
            subjects_list = None
            grade_levels_list = None
            
            if user.subjects:
                try:
                    subjects_list = json.loads(user.subjects)
                except (json.JSONDecodeError, TypeError):
                    subjects_list = None
            
            if user.grade_levels:
                try:
                    grade_levels_list = json.loads(user.grade_levels)
                except (json.JSONDecodeError, TypeError):
                    grade_levels_list = None
            
            return UserResponse(
                user_id=user.user_id,
                email=user.email,
                full_name=user.full_name,
                role=user.role.value,
                country=user.country,
                region=user.region,
                school_name=user.school_name,
                subjects=subjects_list,
                grade_levels=grade_levels_list,
                languages_spoken=user.languages_spoken,
                phone=user.phone,
                bio=user.bio,
                created_at=user.created_at,
                last_login=user.last_login
            )
        except Exception:
            logger.error("Failed to create user response", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An internal error occurred while processing the user data"
            )
    
    def _create_user_profile_response(self, user: User) -> UserProfileResponse:
        """
        Create a user profile response from a User model.
        
        Args:
            user (User): User model instance
            
        Returns:
            UserProfileResponse: User profile response object
        """
        try:
            # Parse JSON strings back to lists
            subjects_list = None
            grade_levels_list = None
            
            if user.subjects:
                try:
                    subjects_list = json.loads(user.subjects)
                except (json.JSONDecodeError, TypeError):
                    subjects_list = None
            
            if user.grade_levels:
                try:
                    grade_levels_list = json.loads(user.grade_levels)
                except (json.JSONDecodeError, TypeError):
                    grade_levels_list = None
            
            return UserProfileResponse(
                user_id=user.user_id,
                full_name=user.full_name,
                country=user.country,
                region=user.region,
                school_name=user.school_name,
                subjects=subjects_list,
                grade_levels=grade_levels_list
            )
        except Exception:
            logger.error("Failed to create user profile response", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="An internal error occurred while processing the user profile data"
            )
