"""
Security Middleware

This module provides middleware to add security headers to all responses.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # AWD-M-35: 'unsafe-inline' removed from script-src.
        # AWD-M-43: 'unsafe-inline' removed from style-src.
        #   React inline style props (style={{ ... }}) are applied via the JS DOM
        #   API (element.style), which is controlled by script-src, not style-src,
        #   so no nonce/hash is required for them.
        #   Google Fonts is loaded via @import in index.css:
        #     - style-src requires fonts.googleapis.com (CSS stylesheet)
        #     - font-src requires fonts.gstatic.com (woff2 font files)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self'; "
            "base-uri 'self'"
        )
        
        return response
