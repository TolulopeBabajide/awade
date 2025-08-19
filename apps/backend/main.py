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

# Auto-run database migrations on startup
def run_migrations():
    """Run database migrations automatically on startup."""
    try:
        print("🔄 Running database migrations...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database migrations completed successfully!")
    except Exception as e:
        print(f"❌ Database migration failed: {e}")
        # Don't fail startup, just log the error
        pass

# Run migrations before creating the app
run_migrations()

app = FastAPI(
    title="Awade API",
    description="AI-powered educator support platform for African teachers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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