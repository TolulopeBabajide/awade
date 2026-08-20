"""
Shared helpers for ChildrenService and ParentGuideService (AWD-M-331).

Both services need identical role-gating and ownership checks.
Extracting them here removes the byte-identical duplication that resulted
from the AWD-M-214 service split.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from apps.backend.models import ChildProfile, User, UserRole


def verify_parent(user: User) -> None:
    """Raise HTTP 403 if the user does not have a parent-level role."""
    if user.role not in (UserRole.PARENT, UserRole.ADMIN, UserRole.SUPER_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parent accounts can manage child profiles",
        )


def get_child_or_404(db: Session, child_id: int, parent_id: int) -> ChildProfile:
    """Fetch a child profile owned by parent_id, or raise HTTP 404."""
    child = (
        db.query(ChildProfile)
        .options(
            joinedload(ChildProfile.country),
            joinedload(ChildProfile.curriculum),
            joinedload(ChildProfile.grade_level),
        )
        .filter(
            ChildProfile.child_id == child_id,
            ChildProfile.parent_id == parent_id,
        )
        .first()
    )
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found",
        )
    return child
