"""
Database migration script to add curriculum schema.
This migration creates the new curriculum tables for storing structured curriculum data.
"""

from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, Integer, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://awade_user:awade_password@localhost:5432/awade")
engine = create_engine(DATABASE_URL)

def run_migration():
    """Execute the curriculum database migration."""
    print("🔄 Starting curriculum database migration...")
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # 1. Create curricula table
            print("📚 Creating curricula table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS curricula (
                    id SERIAL PRIMARY KEY,
                    country VARCHAR(100) NOT NULL,
                    grade_level VARCHAR(10) NOT NULL,
                    subject VARCHAR(100) NOT NULL,
                    theme VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # 2. Create topics table
            print("📝 Creating topics table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS topics (
                    id SERIAL PRIMARY KEY,
                    curriculum_id INTEGER NOT NULL,
                    topic_code VARCHAR(50) UNIQUE NOT NULL,
                    topic_title TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (curriculum_id) REFERENCES curricula(id) ON DELETE CASCADE
                )
            """))
            
            # 3. Create learning_objectives table
            print("🎯 Creating learning_objectives table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS learning_objectives (
                    id SERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    objective TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """))
            
            # 4. Create contents table
            print("📖 Creating contents table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS contents (
                    id SERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    content_area TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """))
            
            # 5. Create teacher_activities table
            print("👨‍🏫 Creating teacher_activities table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS teacher_activities (
                    id SERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    activity TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """))
            
            # 6. Create student_activities table
            print("👨‍🎓 Creating student_activities table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS student_activities (
                    id SERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    activity TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """))
            
            # 7. Create teaching_materials table
            print("📚 Creating teaching_materials table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS teaching_materials (
                    id SERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    material TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """))
            
            # 8. Create evaluation_guides table
            print("📊 Creating evaluation_guides table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS evaluation_guides (
                    id SERIAL PRIMARY KEY,
                    topic_id INTEGER NOT NULL,
                    guide TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                )
            """))
            
            # 9. Create indexes for performance
            print("📊 Creating indexes...")
            
            # Indexes for curricula table
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_curricula_country 
                ON curricula(country)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_curricula_grade_level 
                ON curricula(grade_level)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_curricula_subject 
                ON curricula(subject)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_curricula_country_grade_subject 
                ON curricula(country, grade_level, subject)
            """))
            
            # Indexes for topics table
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_topics_curriculum_id 
                ON topics(curriculum_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_topics_code 
                ON topics(topic_code)
            """))
            
            # Indexes for related tables
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_learning_objectives_topic_id 
                ON learning_objectives(topic_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_contents_topic_id 
                ON contents(topic_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_teacher_activities_topic_id 
                ON teacher_activities(topic_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_student_activities_topic_id 
                ON student_activities(topic_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_teaching_materials_topic_id 
                ON teaching_materials(topic_id)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_evaluation_guides_topic_id 
                ON evaluation_guides(topic_id)
            """))
            
            # 10. Insert sample JSS1 Mathematics curriculum
            print("📝 Inserting sample JSS1 Mathematics curriculum...")
            
            # Check if sample curriculum already exists
            result = conn.execute(text("""
                SELECT id FROM curricula 
                WHERE country = 'Nigeria' AND grade_level = 'JSS1' AND subject = 'Mathematics'
            """))
            
            if not result.fetchone():
                # Insert curriculum
                curriculum_result = conn.execute(text("""
                    INSERT INTO curricula (country, grade_level, subject, theme) 
                    VALUES ('Nigeria', 'JSS1', 'Mathematics', 'Foundation Mathematics')
                    RETURNING id
                """))
                curriculum_id = curriculum_result.scalar()
                
                # Insert sample topic
                topic_result = conn.execute(text("""
                    INSERT INTO topics (curriculum_id, topic_code, topic_title, description) 
                    VALUES (:curriculum_id, 'JSS1_MATH_001', 'Number and Numeration', 'Introduction to numbers and basic numeration concepts')
                    RETURNING id
                """), {"curriculum_id": curriculum_id})
                topic_id = topic_result.scalar()
                
                # Insert sample learning objectives
                conn.execute(text("""
                    INSERT INTO learning_objectives (topic_id, objective) VALUES
                    (:topic_id, 'Students should be able to identify and write numbers up to 1000'),
                    (:topic_id, 'Students should be able to perform basic arithmetic operations'),
                    (:topic_id, 'Students should understand place value concepts')
                """), {"topic_id": topic_id})
                
                # Insert sample content areas
                conn.execute(text("""
                    INSERT INTO contents (topic_id, content_area) VALUES
                    (:topic_id, 'Whole numbers and their properties'),
                    (:topic_id, 'Place value and expanded form'),
                    (:topic_id, 'Basic arithmetic operations (addition, subtraction, multiplication, division)')
                """), {"topic_id": topic_id})
                
                # Insert sample teacher activities
                conn.execute(text("""
                    INSERT INTO teacher_activities (topic_id, activity) VALUES
                    (:topic_id, 'Use number charts and manipulatives to demonstrate place value'),
                    (:topic_id, 'Guide students through step-by-step problem solving'),
                    (:topic_id, 'Provide real-world examples of number usage')
                """), {"topic_id": topic_id})
                
                # Insert sample student activities
                conn.execute(text("""
                    INSERT INTO student_activities (topic_id, activity) VALUES
                    (:topic_id, 'Complete number pattern worksheets'),
                    (:topic_id, 'Practice arithmetic operations with peers'),
                    (:topic_id, 'Create number stories using real-life scenarios')
                """), {"topic_id": topic_id})
                
                # Insert sample teaching materials
                conn.execute(text("""
                    INSERT INTO teaching_materials (topic_id, material) VALUES
                    (:topic_id, 'Number charts and place value charts'),
                    (:topic_id, 'Manipulatives (counters, base-ten blocks)'),
                    (:topic_id, 'Whiteboard and markers for demonstrations')
                """), {"topic_id": topic_id})
                
                # Insert sample evaluation guides
                conn.execute(text("""
                    INSERT INTO evaluation_guides (topic_id, guide) VALUES
                    (:topic_id, 'Assess ability to write and read numbers correctly'),
                    (:topic_id, 'Evaluate accuracy in arithmetic operations'),
                    (:topic_id, 'Check understanding through word problems')
                """), {"topic_id": topic_id})
                
                print("✅ Sample JSS1 Mathematics curriculum inserted successfully!")
            else:
                print("ℹ️  Sample curriculum already exists, skipping insertion.")
            
            # Commit transaction
            trans.commit()
            print("✅ Curriculum database migration completed successfully!")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Migration failed: {e}")
            raise

def rollback_migration():
    """Rollback the curriculum migration (for development only)."""
    print("🔄 Rolling back curriculum migration...")
    
    with engine.connect() as conn:
        trans = conn.begin()
        
        try:
            # Drop tables in reverse order (respecting foreign key constraints)
            print("🗑️  Dropping curriculum tables...")
            
            conn.execute(text("DROP TABLE IF EXISTS evaluation_guides CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS teaching_materials CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS student_activities CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS teacher_activities CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS contents CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS learning_objectives CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS topics CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS curricula CASCADE"))
            
            trans.commit()
            print("✅ Curriculum migration rollback completed!")
            
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