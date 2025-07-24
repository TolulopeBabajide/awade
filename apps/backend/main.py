from fastapi import FastAPI, HTTPException, Depends, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

import sys
import os

# Add parent directories to Python path for imports
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(parent_dir)
sys.path.extend([parent_dir, root_dir])

# Import routers
try:
    from apps.backend.routers import lesson_plans, curriculum
    from routers import auth
    from database import get_db
    from apps.backend.routers import country, grade_level, subject, curriculum_structure
except ImportError:
    # Fallback for Docker container
    from apps.backend.routers import lesson_plans, curriculum
    from apps.backend.routers import auth
    from apps.backend.database import get_db
    from apps.backend.routers import country, grade_level, subject, curriculum_structure

# Load environment variables
load_dotenv()

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

# Include routers
app.include_router(lesson_plans.router)
app.include_router(curriculum.router)
app.include_router(auth.router)
app.include_router(country.router)
app.include_router(grade_level.router)
app.include_router(subject.router)
app.include_router(curriculum_structure.router)

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