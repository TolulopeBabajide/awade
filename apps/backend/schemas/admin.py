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
