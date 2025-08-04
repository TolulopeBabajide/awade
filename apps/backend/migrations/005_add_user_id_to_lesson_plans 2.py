"""
Migration: Add user_id to lesson_plans table

This migration adds a user_id foreign key to the lesson_plans table
to properly map lesson plans to their creators.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migration():
    """Run the migration to add user_id to lesson_plans table."""
    
    # Get database URL from environment
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://awade_user:awade_password@localhost:5432/awade")
    
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        # Check if user_id column already exists
        result = connection.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'lesson_plans' 
            AND column_name = 'user_id'
        """))
        
        if result.fetchone():
            print("user_id column already exists in lesson_plans table")
            return
        
        # Add user_id column
        connection.execute(text("""
            ALTER TABLE lesson_plans 
            ADD COLUMN user_id INTEGER REFERENCES users(user_id)
        """))
        
        # Update existing lesson plans to have a default user_id (user_id = 1)
        # This assumes there's at least one user in the system
        connection.execute(text("""
            UPDATE lesson_plans 
            SET user_id = 1 
            WHERE user_id IS NULL
        """))
        
        # Make user_id NOT NULL after setting default values
        connection.execute(text("""
            ALTER TABLE lesson_plans 
            ALTER COLUMN user_id SET NOT NULL
        """))
        
        connection.commit()
        print("Successfully added user_id column to lesson_plans table")

if __name__ == "__main__":
    run_migration() 