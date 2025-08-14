#!/usr/bin/env python3
"""
Database Testing and Migration Script for Awade Test Environment

This script helps you:
1. Test database connection
2. Create/migrate database tables
3. Validate schema
4. Test basic operations
5. Clean up test data

Usage:
    python test_database.py --test-connection
    python test_database.py --create-tables
    python test_database.py --validate-schema
    python test_database.py --test-operations
    python test_database.py --cleanup
    python test_database.py --full-test
"""

import os
import sys
import argparse
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, SessionLocal
from models import Base, User, UserRole, Country, Curriculum, Subject, GradeLevel

def test_connection():
    """Test database connection."""
    print("🔌 Testing database connection...")
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Database connected successfully!")
            print(f"📊 Database version: {version}")
            return True
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_tables():
    """Create all database tables."""
    print("🏗️  Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    except SQLAlchemyError as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def validate_schema():
    """Validate database schema and show table information."""
    print("🔍 Validating database schema...")
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            print("❌ No tables found in database")
            return False
        
        print(f"✅ Found {len(tables)} tables:")
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            print(f"  📋 {table_name} ({len(columns)} columns)")
            
            # Show column details
            for column in columns:
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                print(f"    - {column['name']}: {column['type']} {nullable}")
            
            # Show indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                print(f"    📊 Indexes: {len(indexes)}")
                for idx in indexes:
                    print(f"      - {idx['name']}: {idx['column_names']}")
            
            print()
        
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def test_basic_operations():
    """Test basic database operations."""
    print("🧪 Testing basic database operations...")
    
    try:
        db = SessionLocal()
        
        # Test 1: Create a test country
        print("  📝 Testing country creation...")
        test_country = Country(
            country_name="Test Country",
            iso_code="TC",
            region="Test Region"
        )
        db.add(test_country)
        db.commit()
        db.refresh(test_country)
        print(f"    ✅ Created country: {test_country.country_name} (ID: {test_country.country_id})")
        
        # Test 2: Create a test curriculum
        print("  📚 Testing curriculum creation...")
        test_curriculum = Curriculum(
            curricula_title="Test Curriculum",
            country_id=test_country.country_id
        )
        db.add(test_curriculum)
        db.commit()
        db.refresh(test_curriculum)
        print(f"    ✅ Created curriculum: {test_curriculum.curricula_title} (ID: {test_curriculum.curricula_id})")
        
        # Test 3: Query operations
        print("  🔍 Testing query operations...")
        countries = db.query(Country).all()
        print(f"    ✅ Found {len(countries)} countries")
        
        curricula = db.query(Curriculum).all()
        print(f"    ✅ Found {len(curricula)} curricula")
        
        # Test 4: Relationship queries
        print("  🔗 Testing relationship queries...")
        country_with_curricula = db.query(Country).filter(Country.country_id == test_country.country_id).first()
        if country_with_curricula and country_with_curricula.curricula:
            print(f"    ✅ Country has {len(country_with_curricula.curricula)} curricula")
        
        db.close()
        print("  ✅ All basic operations passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Basic operations failed: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def cleanup_test_data():
    """Clean up test data."""
    print("🧹 Cleaning up test data...")
    
    try:
        db = SessionLocal()
        
        # Delete test data in reverse order (respecting foreign keys)
        deleted_count = 0
        
        # Delete test curricula
        test_curricula = db.query(Curriculum).filter(Curriculum.curricula_title.like("Test%")).all()
        for curriculum in test_curricula:
            db.delete(curriculum)
            deleted_count += 1
        
        # Delete test countries
        test_countries = db.query(Country).filter(Country.country_name.like("Test%")).all()
        for country in test_countries:
            db.delete(country)
            deleted_count += 1
        
        db.commit()
        print(f"✅ Cleaned up {deleted_count} test records")
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        return False

def show_database_info():
    """Show database information."""
    print("📊 Database Information:")
    print(f"  🔌 Connection: {engine.url}")
    print(f"  🗄️  Database: {engine.url.database}")
    print(f"  👤 User: {engine.url.username}")
    print(f"  🖥️  Host: {engine.url.host}")
    print(f"  🚪 Port: {engine.url.port}")
    print()

def run_full_test():
    """Run all tests in sequence."""
    print("🚀 Running full database test suite...")
    print("=" * 50)
    
    show_database_info()
    
    tests = [
        ("Connection Test", test_connection),
        ("Table Creation", create_tables),
        ("Schema Validation", validate_schema),
        ("Basic Operations", test_basic_operations),
        ("Cleanup", cleanup_test_data)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
        print()
    
    # Summary
    print("📋 Test Results Summary:")
    print("=" * 50)
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Database is ready for use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(description="Database Testing and Migration Script")
    parser.add_argument("--test-connection", action="store_true", help="Test database connection")
    parser.add_argument("--create-tables", action="store_true", help="Create database tables")
    parser.add_argument("--validate-schema", action="store_true", help="Validate database schema")
    parser.add_argument("--test-operations", action="store_true", help="Test basic database operations")
    parser.add_argument("--cleanup", action="store_true", help="Clean up test data")
    parser.add_argument("--full-test", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    if args.test_connection:
        test_connection()
    elif args.create_tables:
        create_tables()
    elif args.validate_schema:
        validate_schema()
    elif args.test_operations:
        test_basic_operations() # Corrected function name
    elif args.cleanup:
        cleanup_test_data()
    elif args.full_test:
        run_full_test()
    else:
        # Default: run full test
        run_full_test()

if __name__ == "__main__":
    main()
