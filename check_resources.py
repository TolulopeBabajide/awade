#!/usr/bin/env python3
"""
Simple script to check lesson resources in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'apps/backend'))

from apps.backend.database import get_db
from apps.backend.models import LessonResource, User, LessonPlan

def check_resources():
    """Check if there are any lesson resources in the database"""
    db = next(get_db())
    
    try:
        # Check total lesson resources
        total_resources = db.query(LessonResource).count()
        print(f"Total lesson resources in database: {total_resources}")
        
        # Check lesson resources by user
        users_with_resources = db.query(LessonResource.user_id).distinct().all()
        print(f"Users with lesson resources: {[user[0] for user in users_with_resources]}")
        
        # Check lesson plans
        total_plans = db.query(LessonPlan).count()
        print(f"Total lesson plans in database: {total_plans}")
        
        # Check users
        total_users = db.query(User).count()
        print(f"Total users in database: {total_users}")
        
        # Show some sample data
        if total_resources > 0:
            print("\nSample lesson resources:")
            resources = db.query(LessonResource).limit(3).all()
            for resource in resources:
                print(f"  - ID: {resource.lesson_resources_id}, User: {resource.user_id}, Plan: {resource.lesson_plan_id}, Status: {resource.status}")
        
    except Exception as e:
        print(f"Error checking resources: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_resources() 