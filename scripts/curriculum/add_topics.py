#!/usr/bin/env python3
"""
Add Topics Script for Awade Platform

This script adds specific topics to existing curriculum structures with:
- Learning objectives
- Content areas
- Proper curriculum mapping

Usage:
    python add_topics.py [--grade <grade_level>] [--subject <subject_name>]
"""

import os
import sys
import argparse
from typing import Dict, List

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'apps', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import CurriculumStructure, Topic, LearningObjective, TopicContent, GradeLevel, Subject
from database import get_database_url

class TopicAdder:
    """Handles adding topics to existing curriculum structures."""
    
    def __init__(self, database_url: str):
        """Initialize with database connection."""
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_curriculum_structures(self, grade_filter: str = None, subject_filter: str = None) -> List[Dict]:
        """Get available curriculum structures with optional filtering."""
        session = self.SessionLocal()
        
        try:
            query = session.query(CurriculumStructure).join(
                GradeLevel, CurriculumStructure.grade_level_id == GradeLevel.grade_level_id
            ).join(
                Subject, CurriculumStructure.subject_id == Subject.subject_id
            )
            
            if grade_filter:
                query = query.filter(GradeLevel.name.ilike(f"%{grade_filter}%"))
            
            if subject_filter:
                query = query.filter(Subject.name.ilike(f"%{subject_filter}%"))
            
            structures = query.all()
            
            result = []
            for structure in structures:
                result.append({
                    'id': structure.curriculum_structure_id,
                    'grade': structure.grade_level.name,
                    'subject': structure.subject.name,
                    'curriculum': structure.curriculum.curricula_title
                })
            
            return result
            
        finally:
            session.close()
    
    def add_mathematics_topics(self):
        """Add comprehensive mathematics topics."""
        print("🔢 Adding Mathematics topics...")
        
        math_topics = [
            {
                "grade": "Primary 1",
                "subject": "Mathematics",
                "topics": [
                    {
                        "title": "Numbers 1-100",
                        "objectives": [
                            "Count and write numbers from 1 to 100",
                            "Identify number patterns",
                            "Understand place value (tens and ones)",
                            "Compare numbers using <, >, ="
                        ],
                        "content_areas": [
                            "Number recognition and writing",
                            "Counting forwards and backwards",
                            "Place value concepts",
                            "Number comparison and ordering"
                        ]
                    },
                    {
                        "title": "Addition and Subtraction",
                        "objectives": [
                            "Add numbers up to 20 mentally",
                            "Subtract numbers up to 20",
                            "Solve simple word problems",
                            "Use number line for calculations"
                        ],
                        "content_areas": [
                            "Mental addition strategies",
                            "Subtraction methods",
                            "Word problem solving",
                            "Number line operations"
                        ]
                    }
                ]
            },
            {
                "grade": "Primary 2",
                "subject": "Mathematics",
                "topics": [
                    {
                        "title": "Multiplication Tables",
                        "objectives": [
                            "Learn multiplication tables 2, 5, and 10",
                            "Understand multiplication as repeated addition",
                            "Solve multiplication word problems",
                            "Use arrays to represent multiplication"
                        ],
                        "content_areas": [
                            "Multiplication tables 2, 5, 10",
                            "Multiplication concepts",
                            "Word problems",
                            "Array representation"
                        ]
                    },
                    {
                        "title": "Money",
                        "objectives": [
                            "Recognize Nigerian currency notes and coins",
                            "Add and subtract money amounts",
                            "Make change from given amounts",
                            "Solve money word problems"
                        ],
                        "content_areas": [
                            "Currency recognition",
                            "Money calculations",
                            "Making change",
                            "Money word problems"
                        ]
                    }
                ]
            },
            {
                "grade": "Primary 3",
                "subject": "Mathematics",
                "topics": [
                    {
                        "title": "Fractions",
                        "objectives": [
                            "Understand fractions as parts of a whole",
                            "Identify halves, quarters, and thirds",
                            "Compare simple fractions",
                            "Add fractions with like denominators"
                        ],
                        "content_areas": [
                            "Fraction concepts",
                            "Common fractions",
                            "Fraction comparison",
                            "Fraction addition"
                        ]
                    }
                ]
            }
        ]
        
        self._add_topics_batch(math_topics)
    
    def add_science_topics(self):
        """Add comprehensive science topics."""
        print("🔬 Adding Science topics...")
        
        science_topics = [
            {
                "grade": "Primary 4",
                "subject": "Basic Science",
                "topics": [
                    {
                        "title": "Energy",
                        "objectives": [
                            "Identify different forms of energy",
                            "Understand energy transformation",
                            "Recognize renewable and non-renewable energy",
                            "Appreciate energy conservation"
                        ],
                        "content_areas": [
                            "Forms of energy (light, heat, sound, electrical)",
                            "Energy transformation",
                            "Energy sources",
                            "Energy conservation"
                        ]
                    },
                    {
                        "title": "Matter",
                        "objectives": [
                            "Understand the three states of matter",
                            "Identify properties of solids, liquids, and gases",
                            "Observe changes of state",
                            "Classify materials by their properties"
                        ],
                        "content_areas": [
                            "States of matter",
                            "Properties of matter",
                            "Changes of state",
                            "Material classification"
                        ]
                    }
                ]
            },
            {
                "grade": "Primary 5",
                "subject": "Basic Science",
                "topics": [
                    {
                        "title": "Living and Non-living Things",
                        "objectives": [
                            "Distinguish between living and non-living things",
                            "Identify characteristics of living organisms",
                            "Classify living things into plants and animals",
                            "Understand basic life processes"
                        ],
                        "content_areas": [
                            "Characteristics of living things",
                            "Classification of organisms",
                            "Life processes",
                            "Habitats and adaptation"
                        ]
                    }
                ]
            }
        ]
        
        self._add_topics_batch(science_topics)
    
    def add_english_topics(self):
        """Add comprehensive English Language topics."""
        print("📚 Adding English Language topics...")
        
        english_topics = [
            {
                "grade": "Primary 3",
                "subject": "English Language",
                "topics": [
                    {
                        "title": "Parts of Speech",
                        "objectives": [
                            "Identify nouns, verbs, and adjectives",
                            "Use parts of speech correctly in sentences",
                            "Understand basic sentence structure",
                            "Build vocabulary through word classification"
                        ],
                        "content_areas": [
                            "Nouns (common and proper)",
                            "Verbs (action words)",
                            "Adjectives (describing words)",
                            "Basic sentence structure"
                        ]
                    }
                ]
            },
            {
                "grade": "Primary 4",
                "subject": "English Language",
                "topics": [
                    {
                        "title": "Reading Comprehension",
                        "objectives": [
                            "Read and understand simple texts",
                            "Answer questions about what was read",
                            "Identify main ideas and supporting details",
                            "Make predictions about story events"
                        ],
                        "content_areas": [
                            "Reading strategies",
                            "Comprehension skills",
                            "Main idea identification",
                            "Story prediction"
                        ]
                    }
                ]
            }
        ]
        
        self._add_topics_batch(english_topics)
    
    def _add_topics_batch(self, topics_data: List[Dict]):
        """Add a batch of topics to the database."""
        session = self.SessionLocal()
        
        try:
            for grade_data in topics_data:
                grade_name = grade_data["grade"]
                subject_name = grade_data["subject"]
                
                # Find curriculum structure
                structure = session.query(CurriculumStructure).join(
                    GradeLevel, CurriculumStructure.grade_level_id == GradeLevel.grade_level_id
                ).join(
                    Subject, CurriculumStructure.subject_id == Subject.subject_id
                ).filter(
                    GradeLevel.name == grade_name,
                    Subject.name == subject_name
                ).first()
                
                if not structure:
                    print(f"   ⚠️  No curriculum structure found for {grade_name} - {subject_name}")
                    continue
                
                print(f"   📝 Adding topics for {grade_name} - {subject_name}")
                
                for topic_data in grade_data["topics"]:
                    # Check if topic already exists
                    existing_topic = session.query(Topic).filter_by(
                        curriculum_structure_id=structure.curriculum_structure_id,
                        topic_title=topic_data["title"]
                    ).first()
                    
                    if existing_topic:
                        print(f"     ⚠️  Topic '{topic_data['title']}' already exists, skipping...")
                        continue
                    
                    # Create topic
                    topic = Topic(
                        curriculum_structure_id=structure.curriculum_structure_id,
                        topic_title=topic_data["title"]
                    )
                    session.add(topic)
                    session.flush()
                    
                    print(f"     ✅ Added topic: {topic_data['title']}")
                    
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
            print("✅ Topics added successfully!")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error adding topics: {e}")
            raise
        finally:
            session.close()
    
    def list_available_structures(self):
        """List all available curriculum structures."""
        print("📋 Available Curriculum Structures:")
        print("=" * 50)
        
        structures = self.get_curriculum_structures()
        
        if not structures:
            print("No curriculum structures found.")
            return
        
        for structure in structures:
            print(f"• {structure['grade']} - {structure['subject']} ({structure['curriculum']})")
    
    def run(self, grade_filter: str = None, subject_filter: str = None):
        """Run the topic addition process."""
        print("🚀 Starting Topic Addition Process...")
        print("=" * 50)
        
        try:
            # List available structures
            self.list_available_structures()
            print()
            
            # Add topics for different subjects
            self.add_mathematics_topics()
            print()
            
            self.add_science_topics()
            print()
            
            self.add_english_topics()
            print()
            
            print("🎉 Topic addition completed successfully!")
            
        except Exception as e:
            print(f"❌ Topic addition failed: {e}")
            sys.exit(1)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Add topics to curriculum structures")
    parser.add_argument("--grade", type=str, help="Filter by grade level")
    parser.add_argument("--subject", type=str, help="Filter by subject")
    
    args = parser.parse_args()
    
    # Get database URL
    database_url = get_database_url()
    
    # Create and run topic adder
    topic_adder = TopicAdder(database_url)
    topic_adder.run(grade_filter=args.grade, subject_filter=args.subject)

if __name__ == "__main__":
    main()
