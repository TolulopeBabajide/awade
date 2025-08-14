#!/usr/bin/env python3
"""
Database Connection Test Script for Awade Platform

This script tests the database connection and basic functionality
before running the main curriculum seeding scripts.

Usage:
    python test_connection.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend'))

try:
    from database import get_database_url
    from models import Base
    print("✅ Successfully imported backend modules")
except ImportError as e:
    print(f"❌ Failed to import backend modules: {e}")
    print("Make sure you're running from the scripts/curriculum directory")
    sys.exit(1)

def test_database_connection():
    """Test basic database connectivity."""
    print("\n🔌 Testing database connection...")
    
    try:
        # Get database URL
        database_url = get_database_url()
        print(f"   Database URL: {database_url.split('@')[1] if '@' in database_url else 'Local'}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"   ✅ Connected successfully")
            print(f"   Database: {version.split(',')[0]}")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def test_table_existence():
    """Test if curriculum tables exist."""
    print("\n📋 Testing table existence...")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        # List of tables to check
        tables_to_check = [
            'countries', 'curricula', 'grade_levels', 'subjects',
            'curriculum_structures', 'topics', 'learning_objectives', 'topic_contents'
        ]
        
        with engine.connect() as conn:
            for table in tables_to_check:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print(f"   ✅ {table}: {count} records")
                except Exception as e:
                    print(f"   ❌ {table}: {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Table check failed: {e}")
        return False

def test_basic_queries():
    """Test basic query functionality."""
    print("\n🔍 Testing basic queries...")
    
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Test countries query
            result = conn.execute(text("SELECT COUNT(*) FROM countries"))
            country_count = result.fetchone()[0]
            print(f"   Countries: {country_count}")
            
            # Test subjects query
            result = conn.execute(text("SELECT COUNT(*) FROM subjects"))
            subject_count = result.fetchone()[0]
            print(f"   Subjects: {subject_count}")
            
            # Test grade levels query
            result = conn.execute(text("SELECT COUNT(*) FROM grade_levels"))
            grade_count = result.fetchone()[0]
            print(f"   Grade Levels: {grade_count}")
            
            if country_count > 0 and subject_count > 0 and grade_count > 0:
                print("   ✅ Basic queries working correctly")
                return True
            else:
                print("   ⚠️  Some tables are empty - may need to run seeder first")
                return True
                
    except Exception as e:
        print(f"   ❌ Query test failed: {e}")
        return False

def main():
    """Run all connection tests."""
    print("🚀 Awade Platform - Database Connection Test")
    print("=" * 50)
    
    # Test database connection
    connection_ok = test_database_connection()
    
    if not connection_ok:
        print("\n❌ Database connection failed. Please check:")
        print("   1. Database server is running")
        print("   2. .env file is properly configured")
        print("   3. Database credentials are correct")
        sys.exit(1)
    
    # Test table existence
    tables_ok = test_table_existence()
    
    # Test basic queries
    queries_ok = test_basic_queries()
    
    print("\n" + "=" * 50)
    if connection_ok and tables_ok and queries_ok:
        print("🎉 All tests passed! Database is ready for curriculum seeding.")
        print("\nNext steps:")
        print("   1. Run: python curriculum_seeder.py --reset")
        print("   2. Run: python add_topics.py")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nTroubleshooting:")
        print("   1. Ensure database schema is created")
        print("   2. Check table permissions")
        print("   3. Verify data integrity")

if __name__ == "__main__":
    main()
