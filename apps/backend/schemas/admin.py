from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any
from datetime import datetime
from apps.backend.models import UserRole

class AdminUserUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_suspended: Optional[bool] = None

class AdminUserResponse(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: UserRole
    country: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class AdminAuditLogResponse(BaseModel):
    log_id: int
    actor_id: int
    action: str
    target_type: str
    target_id: Optional[int]
    metadata_json: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    actor_name: Optional[str]
    
    class Config:
        from_attributes = True

class ResourceModerationUpdate(BaseModel):
    status: str  # safe, flagged, removed
    notes: Optional[str] = None

class LessonTemplateCreate(BaseModel):
    name: str
    version: str
    schema_json: str
    is_active: Optional[int] = 1

class LessonTemplateResponse(LessonTemplateCreate):
    template_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DashboardMetrics(BaseModel):
    total_users: int
    new_users_7d: int
    total_lessons: int
    lessons_7d: int
    flagged_resources: int
    system_health: str


class AdminChildProfileResponse(BaseModel):
    """Read-only view of a child profile for admin/COPPA oversight.

    Excludes AI-generated guide content — admins see structural data only.
    Every request that returns this schema must log via log_admin_action
    with target_type='child_profile' (GRC-05).
    """
    child_id: int
    parent_id: int
    name: str
    age: Optional[int]
    school_name: Optional[str]
    country_id: Optional[int]
    curricula_id: Optional[int]
    grade_level_id: Optional[int]
    subjects: Optional[str]  # JSON array of subject IDs (M-16 tracks migration to join table)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
