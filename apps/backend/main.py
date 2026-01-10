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
try:
    from apps.backend.routers import lesson_plans, curriculum, users, contexts, auth
    from apps.backend.database import get_db, engine
    from apps.backend.routers import country, grade_level, subject, curriculum_structure
    from apps.backend.models import Base
except ImportError:
    # Fallback for Docker container
    from apps.backend.routers import lesson_plans, curriculum, users, contexts, auth
    from apps.backend.database import get_db, engine
    from apps.backend.routers import country, grade_level, subject, curriculum_structure
    from apps.backend.models import Base

# Load environment variables
load_dotenv()

# Auto-run database fix on startup
def run_database_fix():
    """Run database fix script automatically on startup."""
    try:
        print("🔧 Running database fix script...")
        
        # Import and run our fix script
        from apps.backend.init_db_fix import fix_database
        success = fix_database()
        
        if success:
            print("✅ Database fix completed successfully!")
        else:
            print("⚠️ Database fix had issues, but continuing startup...")
            
    except Exception as e:
        print(f"❌ Database fix failed: {e}")
        print("⚠️ Continuing startup despite database fix failure...")
        # Don't fail startup, just log the error
        pass

from contextlib import asynccontextmanager
from apps.backend.redis_client import create_redis_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create Redis pool
    try:
        app.state.redis = await create_redis_pool()
        print("✅ Redis pool created")
    except Exception as e:
        print(f"⚠️ Failed to create Redis pool: {e}")
        app.state.redis = None

    yield
    
    # Shutdown: Close Redis pool
    if getattr(app.state, "redis", None):
        await app.state.redis.close()
        print("🛑 Redis pool closed")

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from apps.backend.middleware import SecurityHeadersMiddleware
from apps.backend.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# ... existing code ...

# Run database fix before creating the app
run_database_fix()

app = FastAPI(
    title="Awade API",
    description="AI-powered educator support platform for African teachers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Prometheus Metrics
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    Instrumentator().instrument(app).expose(app)
except ImportError:
    print("⚠️ Prometheus Instrumentator not found, skipping metrics exposure.")

# Register Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Audit Logging Middleware
from apps.backend.middleware import AuditMiddleware
app.add_middleware(AuditMiddleware)

# Trusted Host Middleware
# In production, set ALLOWED_HOSTS to your domain(s)
# allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
# app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# CORS middleware
# In production, set ALLOWED_ORIGINS to your frontend domain(s)
# For development, we default to common local ports if env var is generic
env_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if env_allowed_origins == "*":
    # If wildcard is set, we must specify origins to allow credentials
    allowed_origins = [
        "http://localhost:5173", # Vite default
        "http://localhost:3001", # React default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3001"
    ]
else:
    allowed_origins = env_allowed_origins.split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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