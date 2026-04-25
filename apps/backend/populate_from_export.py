#!/usr/bin/env python3
"""
Auto-generated Curriculum Population Script

This script was generated from exported curriculum data.
It will populate the remote database with the exact same structure.

Generated: 2025-08-15T00:06:57.473412
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import (
    Country, Curriculum, Subject, GradeLevel,
    CurriculumStructure, Topic, LearningObjective, TopicContent
)

def create_session():
    """Create database session."""
    return SessionLocal()

def populate_from_export():
    """Populate database from exported curriculum data."""
    print("🚀 Populating Database from Exported Curriculum Data")
    print("=" * 60)
    
    # Load the exported data
    with open('curriculum_data_export.json', 'r', encoding='utf-8') as f:
        export_data = json.load(f)
    
    print(f"📄 Loaded export data from: 2025-08-15T00:06:57.473412")
    
    db = create_session()
    
    try:
        # Step 1: Create countries
        print("\n🌍 Creating countries...")
        country_map = {}
        for country_data in export_data['countries']:
            existing = db.query(Country).filter(Country.country_name == country_data['country_name']).first()
            if not existing:
                country = Country(**country_data)
                db.add(country)
                db.flush()
                country_map[country_data['country_name']] = country
                print(f"  ✅ Created: {country_data['country_name']}")
            else:
                country_map[country_data['country_name']] = existing
                print(f"  ⏭️  Found: {country_data['country_name']}")
        
        # Step 2: Create grade levels
        print("\n📚 Creating grade levels...")
        grade_map = {}
        for grade_data in export_data['grade_levels']:
            existing = db.query(GradeLevel).filter(GradeLevel.name == grade_data['name']).first()
            if not existing:
                grade = GradeLevel(**grade_data)
                db.add(grade)
                db.flush()
                grade_map[grade_data['name']] = grade
                print(f"  ✅ Created: {grade_data['name']}")
            else:
                grade_map[grade_data['name']] = existing
                print(f"  ⏭️  Found: {grade_data['name']}")
        
        # Step 3: Create subjects
        print("\n📖 Creating subjects...")
        subject_map = {}
        for subject_data in export_data['subjects']:
            existing = db.query(Subject).filter(Subject.name == subject_data['name']).first()
            if not existing:
                subject = Subject(**subject_data)
                db.add(subject)
                db.flush()
                subject_map[subject_data['name']] = subject
                print(f"  ✅ Created: {subject_data['name']}")
            else:
                subject_map[subject_data['name']] = existing
                print(f"  ⏭️  Found: {subject_data['name']}")
        
        # Step 4: Create curricula
        print("\n📋 Creating curricula...")
        curriculum_map = {}
        for curriculum_data in export_data['curricula']:
            if curriculum_data['country_name'] and curriculum_data['country_name'] in country_map:
                country_id = country_map[curriculum_data['country_name']].country_id
                existing = db.query(Curriculum).filter(
                    Curriculum.curricula_title == curriculum_data['curricula_title']
                ).first()
                if not existing:
                    curriculum = Curriculum(
                        curricula_title=curriculum_data['curricula_title'],
                        country_id=country_id
                    )
                    db.add(curriculum)
                    db.flush()
                    curriculum_map[curriculum_data['curricula_title']] = curriculum
                    print(f"  ✅ Created: {curriculum_data['curricula_title']}")
                else:
                    curriculum_map[curriculum_data['curricula_title']] = existing
                    print(f"  ⏭️  Found: {curriculum_data['curricula_title']}")
        
        # Step 5: Create curriculum structures
        print("\n🔗 Creating curriculum structures...")
        structure_map = {}
        for structure_data in export_data['curriculum_structures']:
            if (structure_data['curricula_title'] in curriculum_map and
                structure_data['grade_level_name'] in grade_map and
                structure_data['subject_name'] in subject_map):
                
                curriculum_id = curriculum_map[structure_data['curricula_title']].curricula_id
                grade_id = grade_map[structure_data['grade_level_name']].grade_level_id
                subject_id = subject_map[structure_data['subject_name']].subject_id
                
                existing = db.query(CurriculumStructure).filter(
                    CurriculumStructure.curricula_id == curriculum_id,
                    CurriculumStructure.grade_level_id == grade_id,
                    CurriculumStructure.subject_id == subject_id
                ).first()
                
                if not existing:
                    structure = CurriculumStructure(
                        curricula_id=curriculum_id,
                        grade_level_id=grade_id,
                        subject_id=subject_id
                    )
                    db.add(structure)
                    db.flush()
                    structure_map[f"{curriculum_id}_{grade_id}_{subject_id}"] = structure
                    print(f"  ✅ Created: {structure_data['grade_level_name']} - {structure_data['subject_name']}")
                else:
                    structure_map[f"{curriculum_id}_{grade_id}_{subject_id}"] = existing
                    print(f"  ⏭️  Found: {structure_data['grade_level_name']} - {structure_data['subject_name']}")
        
        # Step 6: Create topics with content
        print("\n📝 Creating topics with content...")
        topics_created = 0
        for topic_data in export_data['topics']:
            # Find the curriculum structure
            structure_key = None
            for structure_data in export_data['curriculum_structures']:
                if (structure_data['curricula_title'] == topic_data['curriculum_info']['curricula_title'] and
                    structure_data['grade_level_name'] == topic_data['curriculum_info']['grade_level_name'] and
                    structure_data['subject_name'] == topic_data['curriculum_info']['subject_name']):
                    
                    if structure_data['curricula_title'] in curriculum_map and structure_data['grade_level_name'] in grade_map and structure_data['subject_name'] in subject_map:
                        curriculum_id = curriculum_map[structure_data['curricula_title']].curricula_id
                        grade_id = grade_map[structure_data['grade_level_name']].grade_level_id
                        subject_id = subject_map[structure_data['subject_name']].subject_id
                        structure_key = f"{curriculum_id}_{grade_id}_{subject_id}"
                        break
            
            if structure_key and structure_key in structure_map:
                structure = structure_map[structure_key]
                
                # Check if topic exists
                existing_topic = db.query(Topic).filter(
                    Topic.curriculum_structure_id == structure.curriculum_structure_id,
                    Topic.topic_title == topic_data['topic_title']
                ).first()
                
                if not existing_topic:
                    # Create topic
                    topic = Topic(
                        curriculum_structure_id=structure.curriculum_structure_id,
                        topic_title=topic_data['topic_title']
                    )
                    db.add(topic)
                    db.flush()
                    
                    # Create learning objectives
                    for objective_text in topic_data['learning_objectives']:
                        learning_obj = LearningObjective(
                            topic_id=topic.topic_id,
                            objective=objective_text
                        )
                        db.add(learning_obj)
                    
                    # Create content areas
                    for content_area in topic_data['content_areas']:
                        topic_content = TopicContent(
                            topic_id=topic.topic_id,
                            content_area=content_area
                        )
                        db.add(topic_content)
                    
                    topics_created += 1
                    print(f"  ✅ Created topic: {topic_data['topic_title']}")
                    print(f"     - {len(topic_data['learning_objectives'])} learning objectives")
                    print(f"     - {len(topic_data['content_areas'])} content areas")
                else:
                    print(f"  ⏭️  Skipped topic: {topic_data['topic_title']} (already exists)")
        
        # Commit all changes
        db.commit()
        
        print(f"\n" + "=" * 60)
        print("🎉 Curriculum Population from Export Complete!")
        print("=" * 60)
        
        print(f"📊 Summary:")
        print(f"  🌍 Countries: {len(country_map)}")
        print(f"  📚 Grade Levels: {len(grade_map)}")
        print(f"  📖 Subjects: {len(subject_map)}")
        print(f"  📋 Curricula: {len(curriculum_map)}")
        print(f"  🔗 Curriculum Structures: {len(structure_map)}")
        print(f"  📝 Topics Created: {topics_created}")
        
        print(f"\n✅ Ready to use the curriculum in your application!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error populating from export: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function."""
    print("🚀 Curriculum Population from Export Script")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    # Check if export file exists
    if not os.path.exists('curriculum_data_export.json'):
        print("❌ curriculum_data_export.json not found!")
        print("Please run export_curriculum_data.py first to create the export file.")
        sys.exit(1)
    
    # Run population
    success = populate_from_export()
    
    if success:
        print("\n🎯 Population completed successfully!")
        print("Your remote database now contains the same curriculum structure as your local database.")
    else:
        print("\n⚠️  Population failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
