import json
from sqlalchemy.orm import Session
from apps.backend.models import AdminAuditLog
from typing import Optional, Any
from fastapi import Request

def log_admin_action(
    db: Session,
    actor_id: int,
    action: str,
    target_type: str,
    target_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    request: Request = None
):
    """
    Helper to log administrative actions.
    """
    metadata_str = json.dumps(metadata) if metadata else None
    ip_address = request.client.host if request and request.client else None
    
    db_log = AdminAuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        metadata_json=metadata_str,
        ip_address=ip_address
    )
    db.add(db_log)
    db.commit()
