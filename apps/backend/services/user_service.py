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

from apps.backend.models import User, UserRole
from apps.backend.schemas.users import UserUpdate, UserResponse, UserProfileResponse

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
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving users: {str(e)}"
            )
    
    def get_user(self, user_id: int) -> UserResponse:
        """
        Get a specific user by ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            UserResponse: User response
            
        Raises:
            HTTPException: If user not found
        """
        try:
            user = self.db.query(User).filter(User.user_id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            return self._create_user_response(user)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving the user: {str(e)}"
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
            if current_user.user_id != user_id and current_user.role != UserRole.ADMIN:
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the user: {str(e)}"
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
            # Only admins can delete users
            if current_user.role != UserRole.ADMIN:
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while deleting the user: {str(e)}"
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
            # Users can view their own profile, admins can view any profile
            if current_user.user_id != user_id and current_user.role != UserRole.ADMIN:
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while retrieving the user profile: {str(e)}"
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
            # Users can update their own profile, admins can update any profile
            if current_user.user_id != user_id and current_user.role != UserRole.ADMIN:
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while updating the user profile: {str(e)}"
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating user response: {str(e)}"
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
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating user profile response: {str(e)}"
            )
