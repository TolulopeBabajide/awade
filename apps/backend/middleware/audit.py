
import json
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from datetime import datetime, timezone

# Configure audit logger
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
audit_logger.addHandler(handler)

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Only log sensitive or state-changing operations
        # Filter out health checks, metrics, and static files
        path = request.url.path
        if path.startswith("/api") and not path.startswith("/api/health") and not path.startswith("/api/metrics"):
            
            # Extract user ID if available in state (set by auth middleware)
            user_id = getattr(request.state, "user_id", None)
            
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event_type": "api_access",
                "method": request.method,
                "path": path,
                "status_code": response.status_code,
                "user_id": user_id,
                "ip_address": request.client.host if request.client else None,
                "process_time_ms": round(process_time * 1000, 2),
                "user_agent": request.headers.get("user-agent")
            }
            
            # Log as JSON for easy parsing
            audit_logger.info(json.dumps(log_entry))
            
        return response
