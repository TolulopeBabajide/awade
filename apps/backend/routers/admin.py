from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from apps.backend.database import get_db
from apps.backend.models import (
    User, UserRole, LessonPlan, LessonResource, AdminAuditLog, 
    ResourceModeration, LessonTemplate
)
from apps.backend.dependencies import require_admin, require_super_admin
from apps.backend.schemas.admin import (
    AdminUserResponse, AdminUserUpdate, AdminAuditLogResponse, 
    DashboardMetrics, ResourceModerationUpdate, LessonTemplateCreate, LessonTemplateResponse
)
from apps.backend.utils.admin_logs import log_admin_action

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])

@router.get("/metrics", response_model=DashboardMetrics)
async def get_admin_metrics(db: Session = Depends(get_db)):
    """Get dashboard metrics for administrative overview."""
    now = datetime.now()
    seven_days_ago = now - timedelta(days=7)
    
    total_users = db.query(func.count(User.user_id)).scalar()
    new_users_7d = db.query(func.count(User.user_id)).filter(User.created_at >= seven_days_ago).scalar()
    
    total_lessons = db.query(func.count(LessonPlan.lesson_plan_id)).scalar()
    lessons_7d = db.query(func.count(LessonPlan.lesson_plan_id)).filter(LessonPlan.created_at >= seven_days_ago).scalar()
    
    flagged_resources = db.query(func.count(ResourceModeration.moderation_id)).filter(ResourceModeration.status == 'flagged').scalar()
    
    return DashboardMetrics(
        total_users=total_users or 0,
        new_users_7d=new_users_7d or 0,
        total_lessons=total_lessons or 0,
        lessons_7d=lessons_7d or 0,
        flagged_resources=flagged_resources or 0,
        system_health="healthy"
    )

@router.get("/users", response_model=List[AdminUserResponse])
async def list_users(
    skip: int = 0, 
    limit: int = 100,
    role: Optional[UserRole] = None,
    query: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all users with filtering and search."""
    stmt = db.query(User)
    
    if role:
        stmt = stmt.filter(User.role == role)
    if query:
        stmt = stmt.filter(User.email.ilike(f"%{query}%") | User.full_name.ilike(f"%{query}%"))
        
    users = stmt.offset(skip).limit(limit).all()
    return users

@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user_status(
    user_id: int,
    user_update: AdminUserUpdate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role or suspension status."""
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Prevent self-modification of role
    if user_update.role and db_user.user_id == current_admin.user_id:
        raise HTTPException(status_code=400, detail="Admins cannot change their own roles")
    
    # Only super admin can change roles
    if user_update.role and current_admin.role != UserRole.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Only Super Admins can change user roles")
        
    if user_update.role:
        old_role = db_user.role
        db_user.role = user_update.role
        log_admin_action(
            db, current_admin.user_id, "change_role", "user", 
            user_id, {"old_role": old_role.value, "new_role": user_update.role.value},
            request
        )
        
    if user_update.is_suspended is not None:
        db_user.is_suspended = 1 if user_update.is_suspended else 0
        action = "suspend_user" if user_update.is_suspended else "unsuspend_user"
        log_admin_action(
            db, current_admin.user_id, action, "user",
            user_id, {"is_suspended": user_update.is_suspended},
            request
        )
        
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/audit-logs", response_model=List[AdminAuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 50,
    actor_id: Optional[int] = None,
    target_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """View administrative audit logs."""
    stmt = db.query(AdminAuditLog)
    
    if actor_id:
        stmt = stmt.filter(AdminAuditLog.actor_id == actor_id)
    if target_type:
        stmt = stmt.filter(AdminAuditLog.target_type == target_type)
        
    logs = stmt.order_by(desc(AdminAuditLog.created_at)).offset(skip).limit(limit).all()
    
    # Enrichment: add actor names manually if needed or via relationship
    results = []
    for log in logs:
        log_data = AdminAuditLogResponse.from_orm(log)
        if log.actor:
            log_data.actor_name = log.actor.full_name
        results.append(log_data)
        
    return results

@router.get("/resources")
async def list_resources(
    skip: int = 0,
    limit: int = 50,
    flagged_only: bool = False,
    db: Session = Depends(get_db)
):
    """List lesson resources with moderation info."""
    stmt = db.query(LessonResource)
    
    if flagged_only:
        stmt = stmt.join(ResourceModeration).filter(ResourceModeration.status == 'flagged')
        
    resources = stmt.order_by(desc(LessonResource.created_at)).offset(skip).limit(limit).all()
    return resources
@router.patch("/resources/{resource_id}")
async def moderate_resource(
    resource_id: int,
    moderation_data: ResourceModerationUpdate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Moderate a lesson resource (Approve, Flag, Remove)."""
    resource = db.query(LessonResource).filter(LessonResource.lesson_resources_id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    # Get or create moderation entry
    moderation = db.query(ResourceModeration).filter(ResourceModeration.lesson_resource_id == resource_id).first()
    if not moderation:
        moderation = ResourceModeration(lesson_resource_id=resource_id)
        db.add(moderation)
        
    # Update moderation status
    old_status = moderation.status
    moderation.status = moderation_data.status
    moderation.notes = moderation_data.notes
    moderation.reviewed_by = current_admin.user_id
    moderation.reviewed_at = datetime.now()
    
    # Also update the actual resource status if it should be hidden
    if moderation_data.status == 'removed':
        resource.status = 'hidden'
    elif moderation_data.status == 'safe':
        resource.status = 'approved'
        
    log_admin_action(
        db, current_admin.user_id, "moderate_resource", "lesson_resource",
        resource_id, {"old_status": old_status, "new_status": moderation_data.status, "notes": moderation_data.notes},
        request
    )
    
    db.commit()
    return {"status": "success", "message": f"Resource {resource_id} set to {moderation_data.status}"}

# Lesson Template Management
@router.post("/templates", response_model=LessonTemplateResponse)
async def create_template(
    template_data: LessonTemplateCreate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new AI lesson template."""
    # If this is active, deactivate other templates
    if template_data.is_active:
        db.query(LessonTemplate).update({LessonTemplate.is_active: 0})
        
    db_template = LessonTemplate(**template_data.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    log_admin_action(
        db, current_admin.user_id, "create_template", "lesson_template",
        db_template.template_id, {"name": db_template.name, "version": db_template.version},
        request
    )
    
    return db_template

@router.get("/templates", response_model=List[LessonTemplateResponse])
async def list_templates(
    db: Session = Depends(get_db)
):
    """List all AI lesson templates."""
    return db.query(LessonTemplate).order_by(desc(LessonTemplate.created_at)).all()

@router.patch("/templates/{template_id}", response_model=LessonTemplateResponse)
async def update_template(
    template_id: int,
    template_data: LessonTemplateCreate,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an existing AI lesson template."""
    db_template = db.query(LessonTemplate).filter(LessonTemplate.template_id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    # If setting to active, deactivate others
    if template_data.is_active and not db_template.is_active:
        db.query(LessonTemplate).filter(LessonTemplate.template_id != template_id).update({LessonTemplate.is_active: 0})
        
    for key, value in template_data.dict(exclude_unset=True).items():
        setattr(db_template, key, value)
        
    db.commit()
    db.refresh(db_template)
    
    log_admin_action(
        db, current_admin.user_id, "update_template", "lesson_template",
        template_id, {"name": db_template.name, "version": db_template.version},
        request
    )
    
    return db_template

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    request: Request,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete an AI lesson template."""
    db_template = db.query(LessonTemplate).filter(LessonTemplate.template_id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
        
    db.delete(db_template)
    db.commit()
    
    log_admin_action(
        db, current_admin.user_id, "delete_template", "lesson_template",
        template_id, {"name": db_template.name},
        request
    )
    
    return {"status": "success", "message": "Template deleted"}
