#!/usr/bin/env python3
"""
Curriculum Data Export Script

This script extracts existing curriculum data from the local database:
- Countries
- Curricula
- Subjects
- Grade Levels
- Curriculum Structures
- Topics
- Learning Objectives
- Topic Contents

Excludes:
- Users
- Lesson Plans
- Lesson Resources
- Any other user-generated content

Usage:
    python export_curriculum_data.py
"""

import os
import re
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

def export_countries(db):
    """Export countries data."""
    print("🌍 Exporting countries...")
    countries = db.query(Country).all()
    
    countries_data = []
    for country in countries:
        countries_data.append({
            "country_name": country.country_name,
            "iso_code": country.iso_code,
            "region": country.region
        })
    
    print(f"  ✅ Exported {len(countries_data)} countries")
    return countries_data

def export_grade_levels(db):
    """Export grade levels data."""
    print("📚 Exporting grade levels...")
    grade_levels = db.query(GradeLevel).all()
    
    grade_levels_data = []
    for grade in grade_levels:
        grade_levels_data.append({
            "name": grade.name
        })
    
    print(f"  ✅ Exported {len(grade_levels_data)} grade levels")
    return grade_levels_data

def export_subjects(db):
    """Export subjects data."""
    print("📖 Exporting subjects...")
    subjects = db.query(Subject).all()
    
    subjects_data = []
    for subject in subjects:
        subjects_data.append({
            "name": subject.name
        })
    
    print(f"  ✅ Exported {len(subjects_data)} subjects")
    return subjects_data

def export_curricula(db):
    """Export curricula data."""
    print("📋 Exporting curricula...")
    curricula = db.query(Curriculum).all()
    
    curricula_data = []
    for curriculum in curricula:
        curricula_data.append({
            "curriculum_title": curriculum.curriculum_title,
            "country_name": curriculum.country.country_name if curriculum.country else None
        })
    
    print(f"  ✅ Exported {len(curricula_data)} curricula")
    return curricula_data

def export_curriculum_structures(db):
    """Export curriculum structures data."""
    print("🔗 Exporting curriculum structures...")
    structures = db.query(CurriculumStructure).all()
    
    structures_data = []
    for structure in structures:
        structures_data.append({
            "curriculum_title": structure.curriculum.curriculum_title if structure.curriculum else None,
            "grade_level_name": structure.grade_level.name if structure.grade_level else None,
            "subject_name": structure.subject.name if structure.subject else None
        })
    
    print(f"  ✅ Exported {len(structures_data)} curriculum structures")
    return structures_data

def export_topics_with_content(db):
    """Export topics with learning objectives and content areas."""
    print("📝 Exporting topics with content...")
    topics = db.query(Topic).all()
    
    topics_data = []
    for topic in topics:
        # Get curriculum structure info
        structure = topic.curriculum_structure
        curriculum_info = {
            "curriculum_title": structure.curriculum.curriculum_title if structure and structure.curriculum else None,
            "grade_level_name": structure.grade_level.name if structure and structure.grade_level else None,
            "subject_name": structure.subject.name if structure and structure.subject else None
        }
        
        # Get learning objectives
        objectives = []
        for obj in topic.learning_objectives:
            objectives.append(obj.objective)
        
        # Get content areas
        content_areas = []
        for content in topic.topic_contents:
            content_areas.append(content.content_area)
        
        topics_data.append({
            "topic_title": topic.topic_title,
            "curriculum_info": curriculum_info,
            "learning_objectives": objectives,
            "content_areas": content_areas
        })
    
    print(f"  ✅ Exported {len(topics_data)} topics")
    return topics_data

def export_all_curriculum_data():
    """Export all curriculum data from the database."""
    print("🚀 Exporting Curriculum Data from Local Database")
    print("=" * 60)
    
    db = create_session()
    
    try:
        # Export all curriculum-related data
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "export_description": "Curriculum data export excluding users and lesson data",
            "countries": export_countries(db),
            "grade_levels": export_grade_levels(db),
            "subjects": export_subjects(db),
            "curricula": export_curricula(db),
            "curriculum_structures": export_curriculum_structures(db),
            "topics": export_topics_with_content(db)
        }
        
        # Save to JSON file
        output_file = "curriculum_data_export.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Export saved to: {output_file}")
        
        # Print summary
        print(f"\n📊 Export Summary:")
        print(f"  🌍 Countries: {len(export_data['countries'])}")
        print(f"  📚 Grade Levels: {len(export_data['grade_levels'])}")
        print(f"  📖 Subjects: {len(export_data['subjects'])}")
        print(f"  📋 Curricula: {len(export_data['curricula'])}")
        print(f"  🔗 Curriculum Structures: {len(export_data['curriculum_structures'])}")
        print(f"  📝 Topics: {len(export_data['topics'])}")
        
        # Show sample of what was exported
        print(f"\n🔍 Sample Data Preview:")
        if export_data['topics']:
            sample_topic = export_data['topics'][0]
            print(f"  Sample Topic: {sample_topic['topic_title']}")
            print(f"    Curriculum: {sample_topic['curriculum_info']['curriculum_title']}")
            print(f"    Grade: {sample_topic['curriculum_info']['grade_level_name']}")
            print(f"    Subject: {sample_topic['curriculum_info']['subject_name']}")
            print(f"    Objectives: {len(sample_topic['learning_objectives'])}")
            print(f"    Content Areas: {len(sample_topic['content_areas'])}")
        
        print(f"\n✅ Export completed successfully!")
        print(f"📄 File: {output_file}")
        print(f"💡 Use this file to populate your remote database")
        
        return export_data
        
    except Exception as e:
        print(f"❌ Error exporting curriculum data: {e}")
        return None
    finally:
        db.close()

def create_population_script(export_data):
    """Create a population script from the exported data."""
    print(f"\n🔧 Creating population script from exported data...")

    canonical = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'populate_from_export.py')
    with open(canonical, 'r', encoding='utf-8') as f:
        script_content = f.read()

    script_content = re.sub(
        r'(Generated:\s*)[\d\-T:.]+',
        rf'\g<1>{export_data["export_timestamp"]}',
        script_content,
        count=1,
    )

    script_file = "populate_from_export.py"
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"  ✅ Created population script: {script_file}")
    return script_file

def main():
    """Main function."""
    print("🚀 Curriculum Data Export Script")
    print("=" * 60)
    print("This script exports curriculum data from your local database")
    print("Excludes: Users, Lesson Plans, Lesson Resources")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable not set!")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)
    
    # Export the data
    export_data = export_all_curriculum_data()
    
    if export_data:
        # Create the population script
        script_file = create_population_script(export_data)
        
        print(f"\n🎯 Export and Script Creation Complete!")
        print(f"📄 Export file: curriculum_data_export.json")
        print(f"🔧 Population script: {script_file}")
        print(f"\n💡 Next steps:")
        print(f"  1. Review the exported data in curriculum_data_export.json")
        print(f"  2. Use {script_file} to populate your remote database")
        print(f"  3. Verify the data in your remote application")
    else:
        print("❌ Export failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
