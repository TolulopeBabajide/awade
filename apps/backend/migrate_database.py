#!/usr/bin/env python3
"""
Database Migration Script for Awade

This script handles database schema migrations and updates.
"""

import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
from models import Base

def migrate_database():
    """Run database migrations."""
    print("🔄 Running database migrations...")
    
    try:
        # Create all tables based on current models
        print("📋 Creating/updating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/updated successfully!")
        
        # Verify tables exist
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def reset_database():
    """Reset database (drop all tables and recreate)."""
    print("⚠️  WARNING: This will delete ALL data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Operation cancelled.")
        return False
    
    try:
        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped.")
        
        print("🏗️  Recreating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables recreated successfully!")
        
        return True
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return False

def show_migration_status():
    """Show current migration status."""
    print("📊 Database Migration Status:")
    
    try:
        with engine.connect() as connection:
            # Check if tables exist
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"  - {table}")
            else:
                print("❌ No tables found. Run migration first.")
                
    except Exception as e:
        print(f"❌ Error checking migration status: {e}")

def main():
    """Main function."""
    load_dotenv()
    
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "migrate":
            migrate_database()
        elif command == "reset":
            reset_database()
        elif command == "status":
            show_migration_status()
        else:
            print(f"❌ Unknown command: {command}")
            print("Available commands: migrate, reset, status")
    else:
        # Default: show status
        show_migration_status()

if __name__ == "__main__":
    main()
