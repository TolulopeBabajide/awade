"""
Database migration script to update Awade schema.
This migration addresses all discrepancies between documentation and implementation.
"""

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
import enum
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://awade_user:awade_password@localhost:5432/awade")
engine = create_engine(DATABASE_URL)

def run_migration():
    """Execute the database migration."""
    print("🔄 Starting database migration...")
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # 1. Update lesson_plans table
            print("📝 Updating lesson_plans table...")
            
            # Add new columns for 6-section structure
            conn.execute(text("""
                ALTER TABLE lesson_plans 
                ADD COLUMN IF NOT EXISTS topic VARCHAR(255),
                ADD COLUMN IF NOT EXISTS learning_objectives TEXT,
                ADD COLUMN IF NOT EXISTS local_context_section TEXT,
                ADD COLUMN IF NOT EXISTS core_content TEXT,
                ADD COLUMN IF NOT EXISTS activities TEXT,
                ADD COLUMN IF NOT EXISTS quiz TEXT,
                ADD COLUMN IF NOT EXISTS related_projects TEXT
            """))
            
            # Remove old context_description column if it exists
            conn.execute(text("""
                ALTER TABLE lesson_plans 
                DROP COLUMN IF EXISTS context_description
            """))
            
            # 2. Update lesson plan status enum
            print("🔄 Updating lesson plan status enum...")
            
            # Check if lesson_status enum exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_type 
                    WHERE typname = 'lesson_status'
                )
            """))
            enum_exists = result.scalar()
            
            if enum_exists:
                # Ensure 'published' is present in the enum so we can update those rows
                conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_enum 
                            WHERE enumlabel = 'published' AND enumtypid = (
                                SELECT oid FROM pg_type WHERE typname = 'lesson_status')
                        ) THEN
                            ALTER TYPE lesson_status ADD VALUE 'published';
                        END IF;
                    END$$;
                """))
                # Commit after adding new enum value
                trans.commit()
                # Start a new transaction for the update and rest of migration
                trans = conn.begin()

                # Update 'published' to 'exported' while still using the old enum type
                conn.execute(text("""
                    UPDATE lesson_plans 
                    SET status = 'exported'
                    WHERE status = 'published'
                """))

                # Create new enum type
                conn.execute(text("""
                    CREATE TYPE lesson_status_new AS ENUM (
                        'draft', 'generated', 'edited', 'reviewed', 
                        'exported', 'used_offline', 'archived'
                    )
                """))

                # Change the column type to the new enum
                conn.execute(text("""
                    ALTER TABLE lesson_plans 
                    ALTER COLUMN status TYPE lesson_status_new 
                    USING status::text::lesson_status_new
                """))

                # Drop old enum and rename new one
                conn.execute(text("DROP TYPE lesson_status"))
                conn.execute(text("ALTER TYPE lesson_status_new RENAME TO lesson_status"))
            else:
                # Create enum for the first time
                conn.execute(text("""
                    CREATE TYPE lesson_status AS ENUM (
                        'draft', 'generated', 'edited', 'reviewed', 
                        'exported', 'used_offline', 'archived'
                    )
                """))
                
                # Update the column type
                conn.execute(text("""
                    ALTER TABLE lesson_plans 
                    ALTER COLUMN status TYPE lesson_status 
                    USING status::text::lesson_status
                """))
            
            # 3. Consolidate user profile
            print("👤 Consolidating user profile...")
            
            # Add new columns to users table
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS full_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS country VARCHAR(100),
                ADD COLUMN IF NOT EXISTS region VARCHAR(100),
                ADD COLUMN IF NOT EXISTS school_name VARCHAR(255),
                ADD COLUMN IF NOT EXISTS subjects JSON,
                ADD COLUMN IF NOT EXISTS grade_levels JSON,
                ADD COLUMN IF NOT EXISTS languages_spoken TEXT
            """))
            
            # Check if educator_profiles table exists before trying to migrate data
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'educator_profiles'
                )
            """))
            educator_profiles_exists = result.scalar()
            
            if educator_profiles_exists:
                # Migrate data from educator_profiles
                conn.execute(text("""
                    UPDATE users 
                    SET 
                        full_name = ep.full_name,
                        country = ep.country,
                        region = ep.region,
                        school_name = ep.school_name,
                        subjects = ep.subjects,
                        grade_levels = ep.grade_levels,
                        languages_spoken = ep.languages_spoken
                    FROM educator_profiles ep 
                    WHERE users.user_id = ep.user_id
                """))
                
                # Drop educator_profiles table
                conn.execute(text("DROP TABLE educator_profiles CASCADE"))
            
            # 4. Update curriculum mapping table
            print("📚 Updating curriculum mapping...")
            
            # Check if curriculum_map table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'curriculum_map'
                )
            """))
            curriculum_map_exists = result.scalar()
            
            if curriculum_map_exists:
                # Rename table
                conn.execute(text("""
                    ALTER TABLE curriculum_map 
                    RENAME TO curriculum_maps
                """))
            else:
                # Create curriculum_maps table if it doesn't exist
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS curriculum_maps (
                        curriculum_id SERIAL PRIMARY KEY,
                        subject VARCHAR(100) NOT NULL,
                        grade_level VARCHAR(50) NOT NULL,
                        topic VARCHAR(255) NOT NULL,
                        standard_code VARCHAR(255) NOT NULL,
                        standard_description TEXT NOT NULL,
                        country VARCHAR(100),
                        lesson_plan_id INTEGER,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    )
                """))
            
            # Add new columns
            conn.execute(text("""
                ALTER TABLE curriculum_maps 
                ADD COLUMN IF NOT EXISTS topic VARCHAR(255),
                ADD COLUMN IF NOT EXISTS standard_code VARCHAR(255),
                ADD COLUMN IF NOT EXISTS standard_description TEXT,
                ADD COLUMN IF NOT EXISTS lesson_plan_id INTEGER,
                ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW()
            """))
            
            # Check if old columns exist before renaming
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'curriculum_maps' 
                AND column_name IN ('curriculum_standard', 'description')
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            if 'curriculum_standard' in existing_columns:
                # Rename old columns
                conn.execute(text("""
                    ALTER TABLE curriculum_maps 
                    RENAME COLUMN curriculum_standard TO standard_code_old
                """))
                
                # Update data
                conn.execute(text("""
                    UPDATE curriculum_maps 
                    SET standard_code = standard_code_old
                    WHERE standard_code IS NULL
                """))
                
                # Drop old column
                conn.execute(text("""
                    ALTER TABLE curriculum_maps 
                    DROP COLUMN standard_code_old
                """))
            
            if 'description' in existing_columns:
                # Rename old columns
                conn.execute(text("""
                    ALTER TABLE curriculum_maps 
                    RENAME COLUMN description TO standard_description_old
                """))
                
                # Update data
                conn.execute(text("""
                    UPDATE curriculum_maps 
                    SET standard_description = standard_description_old
                    WHERE standard_description IS NULL
                """))
                
                # Drop old column
                conn.execute(text("""
                    ALTER TABLE curriculum_maps 
                    DROP COLUMN standard_description_old
                """))
            
            # Add foreign key constraint
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'fk_curriculum_lesson_plan'
                    ) THEN
                        ALTER TABLE curriculum_maps 
                        ADD CONSTRAINT fk_curriculum_lesson_plan 
                        FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(lesson_id) ON DELETE SET NULL;
                    END IF;
                END $$;
            """))
            
            # 5. Update lesson context table name
            print("🔗 Updating lesson context table...")
            
            # Check if lesson_context table exists
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = 'lesson_context'
                )
            """))
            lesson_context_exists = result.scalar()
            
            if lesson_context_exists:
                conn.execute(text("""
                    ALTER TABLE lesson_context 
                    RENAME TO lesson_contexts
                """))
            else:
                # Create lesson_contexts table if it doesn't exist
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS lesson_contexts (
                        context_id SERIAL PRIMARY KEY,
                        lesson_id INTEGER NOT NULL,
                        context_key VARCHAR(100) NOT NULL,
                        context_value TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """))
                
                # Add foreign key constraint
                conn.execute(text("""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'fk_context_lesson_plan'
                        ) THEN
                            ALTER TABLE lesson_contexts 
                            ADD CONSTRAINT fk_context_lesson_plan 
                            FOREIGN KEY (lesson_id) REFERENCES lesson_plans(lesson_id) ON DELETE CASCADE;
                        END IF;
                    END $$;
                """))
            
            # 6. Update indexes
            print("📊 Updating indexes...")
            
            # Drop old indexes if they exist
            conn.execute(text("DROP INDEX IF EXISTS idx_curriculum_subject_grade"))
            conn.execute(text("DROP INDEX IF EXISTS idx_context_lesson_key"))
            
            # Create new indexes
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_curriculum_subject_grade 
                ON curriculum_maps(subject, grade_level)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_context_lesson_key 
                ON lesson_contexts(lesson_id, context_key)
            """))
            
            # Commit transaction
            trans.commit()
            print("✅ Database migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Migration failed: {e}")
            raise

def rollback_migration():
    """Rollback the migration (for development only)."""
    print("🔄 Rolling back migration...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            # This is a simplified rollback - in production, you'd want more detailed rollback logic
            print("⚠️  Rollback functionality not implemented for this migration")
            print("💡 To rollback, restore from backup or manually reverse changes")
            
            trans.commit()
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Rollback failed: {e}")
            raise

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        run_migration() 