"""
Database initialization script for Awade.
Creates tables and populates with seed data.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root directory
root_dir = Path(__file__).parent.parent.parent
load_dotenv(root_dir / ".env")

# Add the backend directory to Python path
backend_dir = root_dir / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

from database import engine, SessionLocal, create_tables
from models import (
    Base, User, EducatorProfile, Tag, UserRole, LessonStatus, 
    ResourceType, QuestionType
)
from sqlalchemy.orm import Session
import hashlib
import bcrypt
import secrets
from datetime import datetime

def hash_password(password: str) -> str:
    """Secure password hashing using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_seed_data(db: Session):
    """Create initial seed data for the platform."""
    
    # Create sample tags
    tags_data = [
        {"name": "Agriculture", "description": "Lessons related to farming and agricultural practices"},
        {"name": "Traditional Craft", "description": "Indigenous crafts and traditional skills"},
        {"name": "Community Engagement", "description": "Lessons involving community participation"},
        {"name": "Indigenous Language", "description": "Local language and cultural content"},
        {"name": "Mathematics", "description": "Mathematical concepts and problem-solving"},
        {"name": "Science", "description": "Scientific principles and experiments"},
        {"name": "History", "description": "Historical events and cultural heritage"},
        {"name": "Geography", "description": "Geographic concepts and local environment"},
        {"name": "Technology", "description": "Digital literacy and technology integration"},
        {"name": "Health", "description": "Health education and wellness"},
    ]
    
    tags = []
    for tag_data in tags_data:
        tag = Tag(**tag_data)
        db.add(tag)
        tags.append(tag)
    
    # Get admin credentials from environment variables
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_email or not admin_password:
        print("⚠️  ADMIN_EMAIL and ADMIN_PASSWORD environment variables not set.")
        print("   Skipping admin user creation for security.")
    else:
        # Create admin user with environment credentials
        admin_user = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            role=UserRole.ADMIN,
            created_at=datetime.now()
        )
        db.add(admin_user)
        print(f"✅ Created admin user: {admin_email}")
    
    # Get educator credentials from environment variables
    educator_email = os.getenv("EDUCATOR_EMAIL", "grace.teacher@school.com")
    educator_password = os.getenv("EDUCATOR_PASSWORD")
    
    if not educator_password:
        # Generate a secure random password if not provided
        educator_password = secrets.token_urlsafe(12)
        print(f"⚠️  EDUCATOR_PASSWORD not set. Generated secure password: {educator_password}")
        print("   Please save this password securely!")
    
    # Create sample educator user
    educator_user = User(
        email=educator_email,
        password_hash=hash_password(educator_password),
        role=UserRole.EDUCATOR,
        created_at=datetime.now()
    )
    db.add(educator_user)
    
    # Flush to get user IDs
    db.flush()
    
    # Create educator profile
    educator_profile = EducatorProfile(
        user_id=educator_user.user_id,
        full_name="Grace Okechukwu",
        country="Nigeria",
        region="Lagos",
        school_name="Community Primary School",
        subjects=["Mathematics", "Science", "English"],
        grade_levels=["Grade 4", "Grade 5", "Grade 6"],
        languages_spoken="English, Yoruba, Igbo"
    )
    db.add(educator_profile)
    
    # Commit all changes
    db.commit()
    
    print("✅ Seed data created successfully!")
    print(f"   - Created {len(tags)} tags")
    print(f"   - Created admin user: admin@awade.org")
    print(f"   - Created educator user: grace.teacher@school.com")
    print(f"   - Created educator profile for Grace Okechukwu")

def main():
    """Main initialization function."""
    print("🚀 Initializing Awade database...")
    
    try:
        # Create tables
        print("📋 Creating database tables...")
        create_tables()
        print("✅ Tables created successfully!")
        
        # Create seed data
        print("🌱 Creating seed data...")
        db = SessionLocal()
        create_seed_data(db)
        db.close()
        
        print("\n🎉 Database initialization complete!")
        print("\n📊 Database Summary:")
        print("   - Users table: User accounts and authentication")
        print("   - Educator profiles: Detailed teacher information")
        print("   - Lesson plans: Educational content")
        print("   - Tags: Content categorization")
        print("   - Resource links: External materials")
        print("   - Quizzes: Assessment tools")
        print("   - Feedback: User ratings and comments")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 