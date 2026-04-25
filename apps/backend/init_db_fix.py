#!/usr/bin/env python3
"""
Database Fix Script for Awade

This script manually adds the missing columns that should have been created
by the Alembic migrations. This is a temporary fix until the migration
system is working properly.

Usage:
    python init_db_fix.py
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def fix_database():
    """Add missing columns to the users table."""
    try:
        from database import get_db, engine
        from sqlalchemy import text
        
        print("🔧 Fixing database schema...")
        
        # SQL statements to add missing columns
        sql_statements = [
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS profile_image_url VARCHAR(500)
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS profile_image_data TEXT
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS profile_image_type VARCHAR(50)
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS phone VARCHAR(20)
            """,
            """
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS bio TEXT
            """
        ]
        
        # Execute each SQL statement
        with engine.connect() as conn:
            for i, sql in enumerate(sql_statements, 1):
                print(f"  {i}/5: Adding column...")
                conn.execute(text(sql))
                conn.commit()
        
        print("✅ Database schema fixed successfully!")
        print("   Added columns: profile_image_url, profile_image_data, profile_image_type, phone, bio")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    success = fix_database()
    sys.exit(0 if success else 1)
