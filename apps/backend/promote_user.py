import sys
import os

# Add the root directory to sys.path to allow imports from apps
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(root_dir)

from apps.backend.database import SessionLocal
from apps.backend.models import User, UserRole

def promote_to_super_admin(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"Error: User with email {email} not found.")
            return
        
        user.role = UserRole.SUPER_ADMIN
        db.commit()
        print(f"Success: User {email} has been promoted to SUPER_ADMIN.")
        print("You can now log in and access the Admin Panel at /admin.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_user.py <user_email>")
        sys.exit(1)
        
    email_to_promote = sys.argv[1]
    promote_to_super_admin(email_to_promote)
