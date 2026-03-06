import sys
import os

# Add the root directory to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(root_dir)

from apps.backend.database import SessionLocal
from apps.backend.models import User, UserRole
from apps.backend.schemas.users import UserCreate
from apps.backend.services.auth_service import AuthService
from pydantic import ValidationError

def test_signup():
    db = SessionLocal()
    try:
        service = AuthService(db)
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print("Deleted existing test user.")

        user_data = UserCreate(
            email="test@example.com",
            password="Password123!",
            full_name="Test User",
            country="US"
        )
        print(f"User data: {user_data}")
        
        try:
            auth_response, refresh_token = service.register_user(user_data)
            print("Signup successful!")
            print(f"Access Token: {auth_response.access_token[:20]}...")
        except Exception as e:
            print(f"Signup failed with error: {str(e)}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test_signup()
