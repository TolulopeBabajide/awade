"""
main.py - Awade Backend API Entrypoint

This module initializes and configures the Awade FastAPI application, which serves as the backend for the Awade platform—an AI-powered educator support system for African teachers.

Key Features:
- Loads environment variables and configures CORS for cross-origin requests.
- Registers all API routers, including lesson plans, curriculum, authentication, country, grade level, subject, curriculum structure, and users.
- Provides root and health check endpoints for service status and API information.
- Integrates with SQLAlchemy for database access and dependency injection.
- Designed for extensibility and deployment in both development and production environments.
- Auto-runs database migrations on startup.

Usage:
- Run this module directly or with a WSGI/ASGI server (e.g., Uvicorn) to start the API.
- API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

Author: Tolulope Babajide
"""
from fastapi import FastAPI, HTTPException, Depends, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from pathlib import Path

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

# Import routers
from apps.backend.routers import (
    lesson_plans, curriculum, users, contexts, auth,
    country, grade_level, subject, curriculum_structure, admin,
    children
)
from apps.backend.database import get_db, engine
from apps.backend.models import Base

# Load environment variables
load_dotenv()

# ---------------------------------------------------------------------------
# Sentry error monitoring (AWD-H-01)
# Initialised early, before the app is created, so all exceptions are captured.
# Only active when SENTRY_DSN is set and ENVIRONMENT is not "testing".
# ---------------------------------------------------------------------------
import logging as _logging

_sentry_logger = _logging.getLogger(__name__)
logger = _sentry_logger  # module-level structured logger (AWD-M-50)

def _init_sentry() -> None:
    sentry_dsn = os.getenv("SENTRY_DSN", "")
    environment = os.getenv("ENVIRONMENT", "development")
    if not sentry_dsn:
        _sentry_logger.info("Sentry DSN not set — error monitoring disabled")
        return
    if environment == "testing":
        _sentry_logger.info("Sentry disabled in testing environment")
        return
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=environment,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                LoggingIntegration(
                    level=_logging.INFO,       # breadcrumbs from INFO+
                    event_level=_logging.ERROR, # send Sentry events for ERROR+
                ),
            ],
            # Capture 10 % of transactions for performance monitoring;
            # set to 1.0 in production if budget allows.
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            # Never forward raw request bodies — COPPA / GDPR safety.
            send_default_pii=False,
        )
        _sentry_logger.info("Sentry initialised (env=%s)", environment)
    except ImportError:
        _sentry_logger.warning("sentry-sdk not installed — error monitoring disabled")
    except Exception as exc:
        _sentry_logger.warning("Sentry initialisation failed: %s", exc)

_init_sentry()

# Auto-run database fix on startup
def run_database_fix():
    """Run database fix script automatically on startup."""
    try:
        logger.info("Running database fix script...")

        # Import and run our fix script
        from apps.backend.init_db_fix import fix_database
        success = fix_database()

        if success:
            logger.info("Database fix completed successfully")
        else:
            logger.warning("Database fix had issues, but continuing startup...")

    except Exception as e:
        logger.error("Database fix failed", exc_info=True)
        logger.warning("Continuing startup despite database fix failure...")
        # Don't fail startup, just log the error
        pass

from contextlib import asynccontextmanager
from apps.backend.redis_client import create_redis_pool
from apps.backend.dependencies import get_jwt_secret_key

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validate required secrets before accepting traffic.
    # get_jwt_secret_key() raises RuntimeError in production when unset.
    get_jwt_secret_key()

    # Startup: Create Redis pool
    try:
        app.state.redis = await create_redis_pool()
        logger.info("Redis pool created")
    except Exception as e:
        logger.error("Failed to create Redis pool", exc_info=True)
        app.state.redis = None

    yield

    # Shutdown: Close Redis pool
    if getattr(app.state, "redis", None):
        await app.state.redis.close()
        logger.info("Redis pool closed")

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from apps.backend.middleware import SecurityHeadersMiddleware
from apps.backend.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# ... existing code ...

# Run database fix before creating the app
run_database_fix()

# ---------------------------------------------------------------------------
# AWD-M-10: Hide API documentation in production.
# docs_url and redoc_url are set to None when ENVIRONMENT=production so that
# the Swagger UI and ReDoc pages are not publicly accessible on the live server.
# ---------------------------------------------------------------------------
_APP_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
_docs_url = None if _APP_ENVIRONMENT == "production" else "/docs"
_redoc_url = None if _APP_ENVIRONMENT == "production" else "/redoc"

app = FastAPI(
    title="Awade API",
    description="AI-powered educator support platform for African teachers",
    version="1.0.0",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    lifespan=lifespan
)

# Prometheus Metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)
except ImportError:
    logger.warning("Prometheus Instrumentator not found, skipping metrics exposure")

# Register Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Audit Logging Middleware
from apps.backend.middleware import AuditMiddleware
app.add_middleware(AuditMiddleware)

# ---------------------------------------------------------------------------
# AWD-L-04 / AWD-L-54: TrustedHostMiddleware guards against HTTP Host header
# injection (OWASP A05 — Security Misconfiguration).
# Set ALLOWED_HOSTS to a comma-separated list of valid host(s) in production
# (e.g. "awade.app,www.awade.app"). Defaults to "*" (allow all) in dev/test.
# ---------------------------------------------------------------------------
_TRUSTED_HOST_SAFE_ENVIRONMENTS: frozenset[str] = frozenset(
    {"development", "test", "testing"}
)


def _get_allowed_hosts() -> list[str]:
    """Return the allowed-host list for TrustedHostMiddleware.

    Raises RuntimeError when ENVIRONMENT is not in the safe-fallback set and
    ALLOWED_HOSTS is unset or a bare wildcard, mirroring the JWT_SECRET_KEY
    guard in dependencies.py (AWD-L-54).
    """
    raw = os.getenv("ALLOWED_HOSTS", "")
    if not raw or raw.strip() == "*":
        environment = os.getenv("ENVIRONMENT", "development")
        if environment not in _TRUSTED_HOST_SAFE_ENVIRONMENTS:
            raise RuntimeError(
                f"ALLOWED_HOSTS environment variable must be set to a specific "
                f"host list when ENVIRONMENT='{environment}'. "
                "Set ALLOWED_HOSTS to a comma-separated list of valid hostnames "
                "(e.g. 'awade.app,www.awade.app') before starting the server. "
                "The wildcard '*' is only allowed when ENVIRONMENT is one of: "
                "development, test, testing."
            )
        return ["*"]
    return [h.strip() for h in raw.split(",") if h.strip()] or ["*"]


app.add_middleware(TrustedHostMiddleware, allowed_hosts=_get_allowed_hosts())

# CORS middleware
# In production, set ALLOWED_ORIGINS to your frontend domain(s)
# For development, we default to common local ports if env var is generic
env_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if env_allowed_origins == "*":
    # If wildcard is set, we must specify origins to allow credentials
    allowed_origins = [
        "http://localhost:5173", # Vite default
        "http://localhost:3001", # React default
        "http://localhost:3000", # Vite (custom)
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3000"
    ]
else:
    allowed_origins = env_allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)

# Create uploads directory if it doesn't exist
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Mount static files for profile images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(lesson_plans.router)
app.include_router(curriculum.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(country.router)
app.include_router(grade_level.router)
app.include_router(subject.router)
app.include_router(curriculum_structure.router)
app.include_router(contexts.router)
app.include_router(admin.router)
app.include_router(children.router)

# Basic health and info endpoints
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Awade API",
        "version": "1.0.0",
        "description": "AI-powered educator support platform for African teachers",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 