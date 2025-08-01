#!/usr/bin/env python3
"""
Check users in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps/backend'))

from apps.backend.database import get_db
from apps.backend.models import User

def check_users():
    """Check users in the database"""
    db = next(get_db())
    
    try:
        users = db.query(User).all()
        print(f"Total users in database: {len(users)}")
        
        for user in users:
            print(f"  - ID: {user.user_id}, Name: {user.full_name}, Email: {user.email}, Role: {user.role}")
        
    except Exception as e:
        print(f"Error checking users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_users() 