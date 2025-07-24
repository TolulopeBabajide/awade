#!/usr/bin/env python3
"""
Script to create the new simplified database schema.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from apps.backend.database import DATABASE_URL
from apps.backend.models import Base

def create_schema():
    """Create all tables in the database."""
    print("Creating new database schema...")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    try:
        # Create all tables
        Base.metadata.create_all(engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        print(f"\n📋 Created tables ({len(tables)}):")
        for table in sorted(tables):
            print(f"  - {table}")
            
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = create_schema()
    if success:
        print("\n🎉 Database schema setup complete!")
    else:
        print("\n💥 Schema setup failed!")
        sys.exit(1) 