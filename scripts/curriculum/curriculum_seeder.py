#!/usr/bin/env python3
"""
Curriculum Seeder Script for Awade Platform

This script populates the database with comprehensive curriculum data including:
- Countries and regions
- Curriculum frameworks
- Grade levels
- Subjects
- Topics with learning objectives and content areas

Usage:
    python curriculum_seeder.py [--reset] [--country <country_name>]

Examples:
    python curriculum_seeder.py                    # Seed all curriculum data
    python curriculum_seeder.py --reset           # Reset and reseed all data
    python curriculum_seeder.py --country Nigeria # Seed only Nigeria curriculum
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base, Country, Curriculum, GradeLevel, Subject, CurriculumStructure, Topic, LearningObjective, TopicContent
from database import get_database_url

class CurriculumSeeder:
    """Handles seeding of curriculum data into the database."""
    
    def __init__(self, database_url: str):
        """Initialize the seeder with database connection."""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def reset_database(self):
        """Reset all curriculum-related tables."""
        print("🗑️  Resetting curriculum tables...")
        
        with self.engine.connect() as conn:
            # Drop tables in reverse dependency order
            tables_to_drop = [
                'learning_objectives', 'topic_contents', 'lesson_plans', 
                'topics', 'curriculum_structures', 'curricula', 
                'grade_levels', 'subjects', 'countries'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"   Dropped table: {table}")
                except Exception as e:
                    print(f"   Warning: Could not drop {table}: {e}")
            
            conn.commit()
        
        # Recreate tables
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database reset complete")
    
    def seed_countries(self) -> Dict[str, int]:
        """Seed countries and return mapping of country names to IDs."""
        print("🌍 Seeding countries...")
        
        countries_data = [
            {"name": "Nigeria", "iso_code": "NG", "region": "West Africa"},
            {"name": "Ghana", "iso_code": "GH", "region": "West Africa"},
            {"name": "Kenya", "iso_code": "KE", "region": "East Africa"},
            {"name": "South Africa", "iso_code": "ZA", "region": "Southern Africa"},
            {"name": "Uganda", "iso_code": "UG", "region": "East Africa"},
            {"name": "Tanzania", "iso_code": "TZ", "region": "East Africa"},
            {"name": "Ethiopia", "iso_code": "ET", "region": "East Africa"},
            {"name": "Rwanda", "iso_code": "RW", "region": "East Africa"},
            {"name": "Senegal", "iso_code": "SN", "region": "West Africa"},
            {"name": "Morocco", "iso_code": "MA", "region": "North Africa"},
        ]
        
        session = self.SessionLocal()
        country_mapping = {}
        
        try:
            for country_data in countries_data:
                country = Country(
                    country_name=country_data["name"],
                    iso_code=country_data["iso_code"],
                    region=country_data["region"]
                )
                session.add(country)
                session.flush()  # Get the ID
                country_mapping[country_data["name"]] = country.country_id
                print(f"   Added: {country_data['name']} ({country_data['iso_code']})")
            
            session.commit()
            print(f"✅ Added {len(countries_data)} countries")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding countries: {e}")
            raise
        finally:
            session.close()
        
        return country_mapping
    
    def seed_grade_levels(self) -> Dict[str, int]:
        """Seed grade levels and return mapping of names to IDs."""
        print("📚 Seeding grade levels...")
        
        grade_levels_data = [
            "Pre-Primary", "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6",
            "JSS 1", "JSS 2", "JSS 3", "SSS 1", "SSS 2", "SSS 3"
        ]
        
        session = self.SessionLocal()
        grade_mapping = {}
        
        try:
            for grade_name in grade_levels_data:
                grade = GradeLevel(name=grade_name)
                session.add(grade)
                session.flush()
                grade_mapping[grade_name] = grade.grade_level_id
                print(f"   Added: {grade_name}")
            
            session.commit()
            print(f"✅ Added {len(grade_levels_data)} grade levels")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding grade levels: {e}")
            raise
        finally:
            session.close()
        
        return grade_mapping
    
    def seed_subjects(self) -> Dict[str, int]:
        """Seed subjects and return mapping of names to IDs."""
        print("📖 Seeding subjects...")
        
        subjects_data = [
            "Mathematics", "English Language", "Basic Science", "Social Studies", 
            "Agricultural Science", "Home Economics", "Physical Education", "Creative Arts",
            "Computer Studies", "Religious Studies", "Civic Education", "French",
            "Literature in English", "Economics", "Government", "Geography", "History",
            "Biology", "Chemistry", "Physics", "Further Mathematics"
        ]
        
        session = self.SessionLocal()
        subject_mapping = {}
        
        try:
            for subject_name in subjects_data:
                subject = Subject(name=subject_name)
                session.add(subject)
                session.flush()
                subject_mapping[subject_name] = subject.subject_id
                print(f"   Added: {subject_name}")
            
            session.commit()
            print(f"✅ Added {len(subjects_data)} subjects")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding subjects: {e}")
            raise
        finally:
            session.close()
        
        return subject_mapping
    
    def seed_nigeria_curriculum(self, country_id: int, grade_mapping: Dict[str, int], subject_mapping: Dict[str, int]):
        """Seed Nigeria's curriculum structure."""
        print("🇳🇬 Seeding Nigeria curriculum...")
        
        # Nigeria curriculum data
        nigeria_curriculum = {
            "title": "Nigeria National Curriculum",
            "structures": [
                # Primary School
                {"grade": "Primary 1", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies"]},
                {"grade": "Primary 2", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies"]},
                {"grade": "Primary 3", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies"]},
                {"grade": "Primary 4", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies"]},
                {"grade": "Primary 5", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies"]},
                {"grade": "Primary 6", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies"]},
                
                # Junior Secondary School
                {"grade": "JSS 1", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies", "Agricultural Science", "Home Economics"]},
                {"grade": "JSS 2", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies", "Agricultural Science", "Home Economics"]},
                {"grade": "JSS 3", "subjects": ["Mathematics", "English Language", "Basic Science", "Social Studies", "Agricultural Science", "Home Economics"]},
                
                # Senior Secondary School
                {"grade": "SSS 1", "subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Economics", "Government", "Geography"]},
                {"grade": "SSS 2", "subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Economics", "Government", "Geography"]},
                {"grade": "SSS 3", "subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Economics", "Government", "Geography"]},
            ]
        }
        
        self._seed_curriculum_structure(country_id, nigeria_curriculum, grade_mapping, subject_mapping)
    
    def seed_ghana_curriculum(self, country_id: int, grade_mapping: Dict[str, int], subject_mapping: Dict[str, int]):
        """Seed Ghana's curriculum structure."""
        print("🇬🇭 Seeding Ghana curriculum...")
        
        ghana_curriculum = {
            "title": "Ghana National Curriculum",
            "structures": [
                # Primary School
                {"grade": "Primary 1", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies"]},
                {"grade": "Primary 2", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies"]},
                {"grade": "Primary 3", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies"]},
                {"grade": "Primary 4", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies"]},
                {"grade": "Primary 5", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies"]},
                {"grade": "Primary 6", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies"]},
                
                # Junior High School
                {"grade": "JSS 1", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies", "Agricultural Science"]},
                {"grade": "JSS 2", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies", "Agricultural Science"]},
                {"grade": "JSS 3", "subjects": ["Mathematics", "English Language", "Integrated Science", "Social Studies", "Agricultural Science"]},
            ]
        }
        
        self._seed_curriculum_structure(country_id, ghana_curriculum, grade_mapping, subject_mapping)
    
    def _seed_curriculum_structure(self, country_id: int, curriculum_data: Dict, grade_mapping: Dict[str, int], subject_mapping: Dict[str, int]):
        """Helper method to seed curriculum structure."""
        session = self.SessionLocal()
        
        try:
            # Create curriculum
            curriculum = Curriculum(
                curricula_title=curriculum_data["title"],
                country_id=country_id
            )
            session.add(curriculum)
            session.flush()
            
            print(f"   Created curriculum: {curriculum.curricula_title}")
            
            # Create curriculum structures
            for structure in curriculum_data["structures"]:
                grade_id = grade_mapping[structure["grade"]]
                
                for subject_name in structure["subjects"]:
                    subject_id = subject_mapping[subject_name]
                    
                    # Check if structure already exists
                    existing = session.query(CurriculumStructure).filter_by(
                        curricula_id=curriculum.curricula_id,
                        grade_level_id=grade_id,
                        subject_id=subject_id
                    ).first()
                    
                    if not existing:
                        curriculum_structure = CurriculumStructure(
                            curricula_id=curriculum.curricula_id,
                            grade_level_id=grade_id,
                            subject_id=subject_id
                        )
                        session.add(curriculum_structure)
                        print(f"     Added: {structure['grade']} - {subject_name}")
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding curriculum structure: {e}")
            raise
        finally:
            session.close()
    
    def seed_sample_topics(self, grade_mapping: Dict[str, int], subject_mapping: Dict[str, int]):
        """Seed sample topics with learning objectives and content areas."""
        print("📝 Seeding sample topics...")
        
        # Sample topics data
        sample_topics = [
            {
                "grade": "Primary 5",
                "subject": "Mathematics",
                "topic": "Fractions",
                "objectives": [
                    "Understand the concept of fractions as parts of a whole",
                    "Identify and write fractions in different forms",
                    "Compare and order fractions",
                    "Add and subtract fractions with like denominators"
                ],
                "content_areas": [
                    "Introduction to fractions",
                    "Types of fractions (proper, improper, mixed)",
                    "Equivalent fractions",
                    "Fraction operations"
                ]
            },
            {
                "grade": "Primary 6",
                "subject": "Basic Science",
                "topic": "Living and Non-living Things",
                "objectives": [
                    "Distinguish between living and non-living things",
                    "Identify characteristics of living organisms",
                    "Classify living things into plants and animals",
                    "Understand basic life processes"
                ],
                "content_areas": [
                    "Characteristics of living things",
                    "Classification of organisms",
                    "Life processes (respiration, nutrition, reproduction)",
                    "Habitats and adaptation"
                ]
            },
            {
                "grade": "JSS 1",
                "subject": "English Language",
                "topic": "Parts of Speech",
                "objectives": [
                    "Identify and define the eight parts of speech",
                    "Use parts of speech correctly in sentences",
                    "Understand the function of each part of speech",
                    "Apply knowledge in writing and speaking"
                ],
                "content_areas": [
                    "Nouns (common, proper, abstract, concrete)",
                    "Pronouns (personal, possessive, reflexive)",
                    "Verbs (action, linking, helping)",
                    "Adjectives, adverbs, prepositions, conjunctions, interjections"
                ]
            }
        ]
        
        session = self.SessionLocal()
        
        try:
            for topic_data in sample_topics:
                # Find curriculum structure
                structure = session.query(CurriculumStructure).join(
                    GradeLevel, CurriculumStructure.grade_level_id == GradeLevel.grade_level_id
                ).join(
                    Subject, CurriculumStructure.subject_id == Subject.subject_id
                ).filter(
                    GradeLevel.name == topic_data["grade"],
                    Subject.name == topic_data["subject"]
                ).first()
                
                if structure:
                    # Create topic
                    topic = Topic(
                        curriculum_structure_id=structure.curriculum_structure_id,
                        topic_title=topic_data["topic"]
                    )
                    session.add(topic)
                    session.flush()
                    
                    print(f"   Added topic: {topic_data['grade']} - {topic_data['subject']} - {topic_data['topic']}")
                    
                    # Create learning objectives
                    for objective in topic_data["objectives"]:
                        learning_obj = LearningObjective(
                            topic_id=topic.topic_id,
                            objective=objective
                        )
                        session.add(learning_obj)
                    
                    # Create content areas
                    for content in topic_data["content_areas"]:
                        topic_content = TopicContent(
                            topic_id=topic.topic_id,
                            content_area=content
                        )
                        session.add(topic_content)
                
            session.commit()
            print("✅ Sample topics seeded successfully")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error seeding topics: {e}")
            raise
        finally:
            session.close()
    
    def run(self, reset: bool = False, country_filter: Optional[str] = None):
        """Run the complete seeding process."""
        print("🚀 Starting Curriculum Seeder...")
        print("=" * 50)
        
        try:
            if reset:
                self.reset_database()
                print()
            
            # Seed basic data
            country_mapping = self.seed_countries()
            print()
            
            grade_mapping = self.seed_grade_levels()
            print()
            
            subject_mapping = self.seed_subjects()
            print()
            
            # Seed curriculum structures
            if country_filter:
                if country_filter in country_mapping:
                    country_id = country_mapping[country_filter]
                    if country_filter == "Nigeria":
                        self.seed_nigeria_curriculum(country_id, grade_mapping, subject_mapping)
                    elif country_filter == "Ghana":
                        self.seed_ghana_curriculum(country_id, grade_mapping, subject_mapping)
                    else:
                        print(f"⚠️  No specific curriculum data for {country_filter}")
                else:
                    print(f"❌ Country '{country_filter}' not found")
            else:
                # Seed all curricula
                nigeria_id = country_mapping["Nigeria"]
                ghana_id = country_mapping["Ghana"]
                
                self.seed_nigeria_curriculum(nigeria_id, grade_mapping, subject_mapping)
                print()
                self.seed_ghana_curriculum(ghana_id, grade_mapping, subject_mapping)
            
            print()
            
            # Seed sample topics
            self.seed_sample_topics(grade_mapping, subject_mapping)
            
            print()
            print("🎉 Curriculum seeding completed successfully!")
            
        except Exception as e:
            print(f"❌ Seeding failed: {e}")
            sys.exit(1)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Seed curriculum data for Awade platform")
    parser.add_argument("--reset", action="store_true", help="Reset database before seeding")
    parser.add_argument("--country", type=str, help="Seed only specific country curriculum")
    
    args = parser.parse_args()
    
    # Get database URL
    database_url = get_database_url()
    
    # Create and run seeder
    seeder = CurriculumSeeder(database_url)
    seeder.run(reset=args.reset, country_filter=args.country)

if __name__ == "__main__":
    main()
