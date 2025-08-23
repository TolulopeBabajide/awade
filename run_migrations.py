#!/usr/bin/env python3
"""
Database Migration Runner for Awade

This script runs all pending database migrations to ensure the remote database
schema is up to date with the latest code changes.

Usage:
    python run_migrations.py

Environment Variables Required:
    - DATABASE_URL: PostgreSQL connection string
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

def run_migrations():
    """Run all pending database migrations."""
    try:
        # Check if DATABASE_URL is set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            print("   Please set DATABASE_URL to your PostgreSQL connection string")
            return False
        
        print("🚀 Starting database migrations...")
        print(f"📊 Database: {database_url.split('@')[1] if '@' in database_url else 'Unknown'}")
        
        # Import and run Alembic
        from alembic import command
        from alembic.config import Config
        
        # Set up Alembic configuration
        alembic_cfg = Config(str(backend_dir / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run migrations
        print("📋 Running migrations...")
        command.upgrade(alembic_cfg, "head")
        
        print("✅ Database migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
