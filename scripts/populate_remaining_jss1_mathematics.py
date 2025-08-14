#!/usr/bin/env python3
"""
Script to populate the remaining JSS1 Mathematics curriculum data for the NERDC curriculum.

This script works with existing data:
- Nigeria (country_id = 1)
- NERDC Curriculum (curricula_id = 1)
- JSS1 (grade_level_id = 1)
- Mathematics (subject_id = 1)
- Curriculum Structure (curriculum_structure_id = 1)
- Fractions topic already exists (topic_id = 1)

It will create the remaining 24 topics with their learning objectives and content areas.

Author: AI Assistant
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the root directory
root_dir = Path(__file__).parent.parent
load_dotenv(root_dir / ".env")

# Add the backend directory to Python path
backend_dir = root_dir / "apps" / "backend"
sys.path.insert(0, str(backend_dir))

from database import engine, SessionLocal, create_tables
from models import (
    Base, Country, Curriculum, GradeLevel, Subject, CurriculumStructure,
    Topic, LearningObjective, TopicContent
)
from sqlalchemy.orm import Session

def populate_remaining_jss1_mathematics():
    """Populate the remaining JSS1 Mathematics curriculum topics."""
    
    db = SessionLocal()
    
    try:
        print("🚀 Starting population of remaining JSS1 Mathematics curriculum topics...")
        
        # Get existing entities (these should already exist)
        print("🔍 Retrieving existing entities...")
        
        nigeria = db.query(Country).filter(Country.country_id == 1).first()
        if not nigeria:
            raise Exception("Nigeria country not found with ID 1")
        print(f"✅ Found Nigeria: {nigeria.country_name}")
        
        nerdc_curriculum = db.query(Curriculum).filter(Curriculum.curricula_id == 1).first()
        if not nerdc_curriculum:
            raise Exception("NERDC Curriculum not found with ID 1")
        print(f"✅ Found NERDC Curriculum: {nerdc_curriculum.curricula_title}")
        
        jss1 = db.query(GradeLevel).filter(GradeLevel.grade_level_id == 1).first()
        if not jss1:
            raise Exception("JSS1 grade level not found with ID 1")
        print(f"✅ Found Grade Level: {jss1.name}")
        
        mathematics = db.query(Subject).filter(Subject.subject_id == 1).first()
        if not mathematics:
            raise Exception("Mathematics subject not found with ID 1")
        print(f"✅ Found Subject: {mathematics.name}")
        
        curriculum_structure = db.query(CurriculumStructure).filter(
            CurriculumStructure.curriculum_structure_id == 1
        ).first()
        if not curriculum_structure:
            raise Exception("Curriculum structure not found with ID 1")
        print(f"✅ Found Curriculum Structure: {curriculum_structure.curriculum_structure_id}")
        
        # Check existing topics
        existing_topics = db.query(Topic).filter(
            Topic.curriculum_structure_id == curriculum_structure.curriculum_structure_id
        ).all()
        print(f"✅ Found {len(existing_topics)} existing topics")
        
        existing_topic_titles = [topic.topic_title for topic in existing_topics]
        print(f"   Existing topics: {', '.join(existing_topic_titles)}")
        
        # Define all the topics that should exist (excluding Fractions which already exists)
        all_topics_data = [
            # Theme 1: Number and Numeration
            {
                "title": "Whole Numbers",
                "objectives": [
                    "Count and write in millions and billions.",
                    "Count and write in trillions.",
                    "Apply the counting, writing, and reading of large numbers in everyday life.",
                    "Solve problems in quantitative aptitude reasoning using large numbers."
                ],
                "contents": [
                    "Millions and billions.",
                    "Trillions.",
                    "Quantitative reasoning."
                ]
            },
            {
                "title": "LCM (Lowest Common Multiple)",
                "objectives": [
                    "Identify common multiples of two or more whole numbers.",
                    "Find the LCM of whole numbers."
                ],
                "contents": [
                    "LCM of whole numbers."
                ]
            },
            {
                "title": "HCF (Highest Common Factor)",
                "objectives": [
                    "Identify common factors of whole numbers.",
                    "Find the HCF of whole numbers.",
                    "Identify the difference between LCM and HCF.",
                    "Solve problems on quantitative aptitude involving LCM and HCF of whole numbers."
                ],
                "contents": [
                    "HCF of whole numbers.",
                    "LCM and HCF of given whole numbers.",
                    "Quantitative reasoning."
                ]
            },
            {
                "title": "Counting in Base 2",
                "objectives": [
                    "Students should be able to count in groups of twos."
                ],
                "contents": [
                    "Counting in groups of twos."
                ]
            },
            {
                "title": "Conversion of Base 10 Numerals to Binary Numbers",
                "objectives": [
                    "Students should be able to convert base 10 numerals to binary numbers."
                ],
                "contents": [
                    "Converting numbers 1-10 to base 2."
                ]
            },
            # Theme 2: Basic Operations
            {
                "title": "Addition and Subtraction",
                "objectives": [
                    "Add and subtract any given numbers correctly.",
                    "State the place value of each number in the sum or difference.",
                    "Draw and use number line to illustrate directed numbers.",
                    "Add and subtract positive and negative integers correctly on the number line.",
                    "Interpret and relate positive and negative numbers to everyday activities."
                ],
                "contents": [
                    "Addition and subtraction of numbers and place values.",
                    "Use of number line.",
                    "Addition and subtraction of positive and negative integers.",
                    "Everyday application of positive and negative integers."
                ]
            },
            {
                "title": "Addition and Subtraction of Fractions",
                "objectives": [
                    "Solve given problems on addition and subtraction of fractions.",
                    "Solve word problems involving addition and subtraction of fractions."
                ],
                "contents": [
                    "Addition and subtraction of fractions.",
                    "Word problems on addition and subtraction of fractions."
                ]
            },
            {
                "title": "Multiplication and Division of Fractions",
                "objectives": [
                    "Solve problems on multiplication of fractions.",
                    "Solve problems on division of fractions.",
                    "Solve word problems involving multiplication and division of fractions."
                ],
                "contents": [
                    "Multiplication of fractions.",
                    "Division of fractions.",
                    "Word problems involving multiplication and division of fractions."
                ]
            },
            {
                "title": "Estimation",
                "objectives": [
                    "Estimate the dimensions and distances within the school.",
                    "Estimate the capacity and mass of given objects.",
                    "Estimate other things in day-to-day activities.",
                    "Solve problems on quantitative reasoning in estimation."
                ],
                "contents": [
                    "Estimation of dimensions and distances.",
                    "Estimation of capacity and mass of objects.",
                    "Estimation of other things e.g., age, time.",
                    "Quantitative reasoning involving estimation."
                ]
            },
            {
                "title": "Approximation",
                "objectives": [
                    "Approximate answers to addition and subtraction problems to a given degree of accuracy.",
                    "Approximate answers to multiplication and division problems to a given degree of accuracy.",
                    "Round numbers to the nearest 10, 100, and 1000.",
                    "Apply approximation involving basic operations in everyday life activities.",
                    "Solve problems on quantitative reasoning in the above contents."
                ],
                "contents": [
                    "Approximating values of addition and subtraction.",
                    "Approximating results of multiplication and division.",
                    "Rounding off numbers to the nearest 10, 100, and 1000.",
                    "Application of approximation in everyday life.",
                    "Quantitative reasoning."
                ]
            },
            {
                "title": "Addition of Numbers in Base 2 Numerals",
                "objectives": [
                    "Students should be able to add two or three 3-digit binary numbers."
                ],
                "contents": [
                    "Addition of two or three 3-digit binary numbers."
                ]
            },
            {
                "title": "Subtraction of Numbers in Base 2 Numerals",
                "objectives": [
                    "Students should be able to subtract two 3-digit binary numbers."
                ],
                "contents": [
                    "Subtraction of two 3-digit binary numbers."
                ]
            },
            {
                "title": "Multiplication of Numbers in Base 2 Numerals",
                "objectives": [
                    "Students should be able to multiply two 2-digit binary numbers."
                ],
                "contents": [
                    "Multiplication of two 2-digit binary numbers."
                ]
            },
            # Theme 3: Algebra Processes
            {
                "title": "Use of Symbols",
                "objectives": [
                    "Solve problems expressed in open sentences.",
                    "Identify the relationship between addition and subtraction; multiplication and division.",
                    "Use letters to represent symbols or shapes in open sentences.",
                    "Solve open sentence problems involving two arithmetic operations.",
                    "Solve word problems involving use of symbols.",
                    "Solve quantitative aptitude problems on the use of symbols."
                ],
                "contents": [
                    "Open sentences.",
                    "Use of letters to represent symbols or shapes in open sentences.",
                    "Solving open sentences with two arithmetic operations.",
                    "Word problems involving use of symbols.",
                    "Quantitative aptitude."
                ]
            },
            {
                "title": "Simplification of Algebraic Expressions",
                "objectives": [
                    "Identify and collect like terms in a given expression.",
                    "Identify the coefficient of a given algebraic term.",
                    "Identify the positive and negative coefficients of a given algebraic term.",
                    "Perform basic arithmetic operations on expressions of similar terms.",
                    "Insert/remove brackets and simplify expressions.",
                    "Solve quantitative aptitude problems on the use of brackets."
                ],
                "contents": [
                    "Like and unlike terms in algebraic expressions.",
                    "Identification of coefficients of terms of algebraic expressions.",
                    "Basic arithmetic operations applied to algebraic expressions of similar terms.",
                    "Collection and simplification of like and unlike terms in algebraic expressions.",
                    "Use of brackets.",
                    "Quantitative reasoning."
                ]
            },
            {
                "title": "Simple Equations",
                "objectives": [
                    "Translate word sentences into mathematical equations.",
                    "Use mathematical equations to represent word sentences.",
                    "Solve simple equations and cross-check the answers."
                ],
                "contents": [
                    "Translation of word problems into equations and vice versa.",
                    "Solution of simple equations."
                ]
            },
            # Theme 4: Mensuration and Geometry
            {
                "title": "Plane Shapes",
                "objectives": [
                    "State similarities and differences between square, rectangle, triangle, trapezium, parallelogram, and circle.",
                    "Find the perimeter of regular polygons.",
                    "Find the area of plane shapes such as squares, rectangles, parallelograms.",
                    "Find the area of real-life plane objects."
                ],
                "contents": [
                    "Similarities and differences between square, rectangle, triangle, trapezium, parallelogram, and circle.",
                    "Perimeter of regular polygons.",
                    "Area of regular plane shapes."
                ]
            },
            {
                "title": "Three Dimensional Figures",
                "objectives": [
                    "Identify the properties of cubes and cuboids.",
                    "Identify the properties of pyramids and cones.",
                    "Identify the properties of cylinders and spheres.",
                    "Find volume of a cube and a cuboid."
                ],
                "contents": [
                    "Basic properties of cubes and cuboids.",
                    "Basic properties of pyramids and cones.",
                    "Basic properties of cylinders and spheres.",
                    "Volume of cubes and cuboids."
                ]
            },
            {
                "title": "Construction",
                "objectives": [
                    "Construct parallel and perpendicular lines.",
                    "Bisect a given line segment.",
                    "Construct angles 90 and 60 degrees."
                ],
                "contents": [
                    "Construction of parallel and perpendicular lines.",
                    "Bisection of a given line segment.",
                    "Construction of angles 90 and 60 degrees."
                ]
            },
            {
                "title": "Angles",
                "objectives": [
                    "Measure angles.",
                    "Identify vertically opposite, adjacent, alternate, and corresponding angles.",
                    "State properties of angles.",
                    "Identify angles at a point and angles on a straight line and state their properties."
                ],
                "contents": [
                    "Measurement of angles.",
                    "Identification and properties of vertically opposite, adjacent, alternate, and corresponding angles.",
                    "Identification and properties of angles at a point and angles on a straight line."
                ]
            },
            # Theme 5: Everyday Statistics
            {
                "title": "Need for Statistics",
                "objectives": [
                    "List purposes of statistics.",
                    "Recognize the usefulness of statistics for planning purposes.",
                    "Apply the occurrence of chance events/application of probabilities in everyday life.",
                    "Recognize the usefulness of statistics for prediction purposes."
                ],
                "contents": [
                    "Purposes of statistics.",
                    "Need for collecting data for planning purposes."
                ]
            },
            {
                "title": "Data Collection",
                "objectives": [
                    "Students should be able to collect data in the class."
                ],
                "contents": [
                    "Collect data in the class."
                ]
            },
            {
                "title": "Data Presentation",
                "objectives": [
                    "Students should be able to determine the median of a given set of data."
                ],
                "contents": [
                    "Median."
                ]
            }
        ]
        
        # Filter out topics that already exist
        topics_to_create = []
        for topic_data in all_topics_data:
            if topic_data["title"] not in existing_topic_titles:
                topics_to_create.append(topic_data)
            else:
                print(f"⚠️  Topic '{topic_data['title']}' already exists, skipping...")
        
        print(f"\n📝 Creating {len(topics_to_create)} new topics...")
        
        topics_created = 0
        objectives_created = 0
        contents_created = 0
        
        for topic_data in topics_to_create:
            # Create topic
            topic = Topic(
                curriculum_structure_id=curriculum_structure.curriculum_structure_id,
                topic_title=topic_data["title"]
            )
            db.add(topic)
            db.flush()
            topics_created += 1
            
            # Create learning objectives
            for objective_text in topic_data["objectives"]:
                objective = LearningObjective(
                    topic_id=topic.topic_id,
                    objective=objective_text
                )
                db.add(objective)
                objectives_created += 1
            
            # Create content areas
            for content_text in topic_data["contents"]:
                content = TopicContent(
                    topic_id=topic.topic_id,
                    content_area=content_text
                )
                db.add(content)
                contents_created += 1
            
            print(f"✅ Created topic: {topic_data['title']}")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Remaining JSS1 Mathematics curriculum topics population complete!")
        print(f"📊 Summary:")
        print(f"   - New topics created: {topics_created}")
        print(f"   - New learning objectives created: {objectives_created}")
        print(f"   - New content areas created: {contents_created}")
        print(f"   - Total topics now in curriculum: {len(existing_topics) + topics_created}")
        
        # Verify the final data
        print(f"\n🔍 Final verification:")
        final_topics = db.query(Topic).filter(
            Topic.curriculum_structure_id == curriculum_structure.curriculum_structure_id
        ).all()
        print(f"   - Total topics in database: {len(final_topics)}")
        
        # Group topics by theme for better organization
        theme1_topics = ["Whole Numbers", "LCM (Lowest Common Multiple)", "HCF (Highest Common Factor)", 
                        "Counting in Base 2", "Conversion of Base 10 Numerals to Binary Numbers", "Fractions"]
        theme2_topics = ["Addition and Subtraction", "Addition and Subtraction of Fractions", 
                        "Multiplication and Division of Fractions", "Estimation", "Approximation",
                        "Addition of Numbers in Base 2 Numerals", "Subtraction of Numbers in Base 2 Numerals",
                        "Multiplication of Numbers in Base 2 Numerals"]
        theme3_topics = ["Use of Symbols", "Simplification of Algebraic Expressions", "Simple Equations"]
        theme4_topics = ["Plane Shapes", "Three Dimensional Figures", "Construction", "Angles"]
        theme5_topics = ["Need for Statistics", "Data Collection", "Data Presentation"]
        
        print(f"\n📚 Topics by Theme:")
        print(f"   Theme 1 (Number and Numeration): {len([t for t in final_topics if t.topic_title in theme1_topics])} topics")
        print(f"   Theme 2 (Basic Operations): {len([t for t in final_topics if t.topic_title in theme2_topics])} topics")
        print(f"   Theme 3 (Algebra Processes): {len([t for t in final_topics if t.topic_title in theme3_topics])} topics")
        print(f"   Theme 4 (Mensuration and Geometry): {len([t for t in final_topics if t.topic_title in theme4_topics])} topics")
        print(f"   Theme 5 (Everyday Statistics): {len([t for t in final_topics if t.topic_title in theme5_topics])} topics")
        
        # Show sample of topics with their objectives and contents
        print(f"\n📋 Sample topic details:")
        for topic in final_topics[:3]:  # Show first 3 topics
            objectives = db.query(LearningObjective).filter(
                LearningObjective.topic_id == topic.topic_id
            ).all()
            contents = db.query(TopicContent).filter(
                TopicContent.topic_id == topic.topic_id
            ).all()
            print(f"   - {topic.topic_title}: {len(objectives)} objectives, {len(contents)} contents")
        
    except Exception as e:
        print(f"❌ Error creating curriculum: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to run the curriculum population."""
    print("🚀 JSS1 Mathematics Curriculum - Remaining Topics Population Script")
    print("==================================================================")
    
    try:
        # Ensure tables exist
        print("📋 Ensuring database tables exist...")
        create_tables()
        print("✅ Database tables ready!")
        
        # Populate the remaining curriculum
        populate_remaining_jss1_mathematics()
        
        print("\n🎉 All done! The remaining JSS1 Mathematics curriculum topics have been populated successfully.")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
