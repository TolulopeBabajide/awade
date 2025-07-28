#!/usr/bin/env python3
"""
Create Admin User Script

This script creates an admin user for testing the authentication and authorization system.
It should be run after the database migrations have been applied.

Environment Variables:
- ADMIN_EMAIL: Admin user email (default: admin@awade.com)
- ADMIN_PASSWORD: Admin user password (default: admin123)
- EDUCATOR_EMAIL: Educator user email (default: educator@awade.com)
- EDUCATOR_PASSWORD: Educator user password (default: educator123)

Usage:
    python scripts/create_admin_user.py

Author: Tolulope Babajide
"""

import sys
import os
import bcrypt
from datetime import datetime

# Add the backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, '..', 'apps', 'backend')
sys.path.insert(0, backend_dir)

from database import get_db, engine
from models import User, UserRole

def get_env_or_default(key: str, default: str) -> str:
    """Get environment variable or return default value."""
    return os.getenv(key, default)

def create_admin_user():
    """Create an admin user for testing."""
    db = next(get_db())
    
    try:
        admin_email = get_env_or_default("ADMIN_EMAIL", "admin@awade.com")
        admin_password = get_env_or_default("ADMIN_PASSWORD", "admin123")
        
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if admin_user:
            print(f"Admin user already exists: {admin_email}")
            return
        
        # Validate password length
        min_length = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        if len(admin_password) < min_length:
            print(f"Warning: Admin password is shorter than minimum length ({min_length} characters)")
        
        # Create admin user
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), salt).decode('utf-8')
        
        admin_user = User(
            email=admin_email,
            password_hash=password_hash,
            full_name="Admin User",
            role=UserRole.ADMIN,
            country="Nigeria",
            region="Lagos",
            school_name="Awade Platform",
            subjects=["Mathematics", "Science"],
            grade_levels=["Grade 4", "Grade 5", "Grade 6"],
            languages_spoken="English, Yoruba",
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        
        print("Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("Please change the password after first login!")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.rollback()
    finally:
        db.close()

def create_educator_user():
    """Create an educator user for testing."""
    db = next(get_db())
    
    try:
        educator_email = get_env_or_default("EDUCATOR_EMAIL", "educator@awade.com")
        educator_password = get_env_or_default("EDUCATOR_PASSWORD", "educator123")
        
        # Check if educator user already exists
        educator_user = db.query(User).filter(User.email == educator_email).first()
        if educator_user:
            print(f"Educator user already exists: {educator_email}")
            return
        
        # Validate password length
        min_length = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        if len(educator_password) < min_length:
            print(f"Warning: Educator password is shorter than minimum length ({min_length} characters)")
        
        # Create educator user
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(educator_password.encode('utf-8'), salt).decode('utf-8')
        
        educator_user = User(
            email=educator_email,
            password_hash=password_hash,
            full_name="Test Educator",
            role=UserRole.EDUCATOR,
            country="Nigeria",
            region="Lagos",
            school_name="Test School",
            subjects=["Mathematics"],
            grade_levels=["Grade 4"],
            languages_spoken="English",
            created_at=datetime.utcnow()
        )
        
        db.add(educator_user)
        db.commit()
        
        print("Educator user created successfully!")
        print(f"Email: {educator_email}")
        print(f"Password: {educator_password}")
        
    except Exception as e:
        print(f"Error creating educator user: {str(e)}")
        db.rollback()
    finally:
        db.close()

def check_environment():
    """Check if required environment variables are set."""
    print("Environment Configuration:")
    print(f"ADMIN_EMAIL: {get_env_or_default('ADMIN_EMAIL', 'admin@awade.com')}")
    print(f"ADMIN_PASSWORD: {'*' * len(get_env_or_default('ADMIN_PASSWORD', 'admin123'))}")
    print(f"EDUCATOR_EMAIL: {get_env_or_default('EDUCATOR_EMAIL', 'educator@awade.com')}")
    print(f"EDUCATOR_PASSWORD: {'*' * len(get_env_or_default('EDUCATOR_PASSWORD', 'educator123'))}")
    print(f"PASSWORD_MIN_LENGTH: {os.getenv('PASSWORD_MIN_LENGTH', '8')}")
    print(f"JWT_SECRET_KEY: {'*' * len(os.getenv('JWT_SECRET_KEY', 'dev-secret'))}")
    print()

if __name__ == "__main__":
    print("Creating test users...")
    check_environment()
    create_admin_user()
    create_educator_user()
    print("Done!") 