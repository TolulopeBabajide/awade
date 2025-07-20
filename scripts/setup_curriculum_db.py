#!/usr/bin/env python3
"""
Script to set up the curriculum database and test functionality.
"""

import os
import sys
import requests
import json
from datetime import datetime

# Add the backend directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, "..", "apps", "backend")
sys.path.insert(0, backend_dir)

def run_migration():
    """Run the curriculum database migration."""
    print("🔄 Running curriculum database migration...")
    
    try:
        # Run the migration using subprocess
        import subprocess
        result = subprocess.run([
            sys.executable, 
            os.path.join(backend_dir, 'migrations', '002_curriculum_schema.py')
        ], capture_output=True, text=True, cwd=backend_dir)
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def test_curriculum_api():
    """Test the curriculum API endpoints."""
    print("\n🧪 Testing curriculum API endpoints...")
    
    base_url = "http://localhost:8000/api/curriculum"
    
    # Test data for JSS1 Mathematics
    test_curriculum = {
        "country": "Nigeria",
        "grade_level": "JSS1",
        "subject": "Mathematics",
        "theme": "Foundation Mathematics"
    }
    
    test_topic = {
        "curriculum_id": 1,
        "topic_code": "JSS1_MATH_002",
        "topic_title": "Basic Operations",
        "description": "Addition, subtraction, multiplication, and division"
    }
    
    try:
        # Test 1: Create curriculum
        print("📝 Testing curriculum creation...")
        response = requests.post(f"{base_url}/", json=test_curriculum)
        if response.status_code == 200:
            print("✅ Curriculum created successfully")
            curriculum_data = response.json()
            print(f"   Curriculum ID: {curriculum_data['id']}")
        else:
            print(f"❌ Failed to create curriculum: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 2: Get curricula
        print("📖 Testing curriculum retrieval...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            curricula = response.json()
            print(f"✅ Retrieved {len(curricula)} curricula")
        else:
            print(f"❌ Failed to retrieve curricula: {response.status_code}")
            return False
        
        # Test 3: Get specific curriculum
        print("🔍 Testing specific curriculum retrieval...")
        response = requests.get(f"{base_url}/{curriculum_data['id']}")
        if response.status_code == 200:
            curriculum_detail = response.json()
            print(f"✅ Retrieved curriculum: {curriculum_detail['subject']} - {curriculum_detail['grade_level']}")
        else:
            print(f"❌ Failed to retrieve specific curriculum: {response.status_code}")
            return False
        
        # Test 4: Create topic
        print("📝 Testing topic creation...")
        test_topic["curriculum_id"] = curriculum_data["id"]
        response = requests.post(f"{base_url}/topics", json=test_topic)
        if response.status_code == 200:
            print("✅ Topic created successfully")
            topic_data = response.json()
            print(f"   Topic ID: {topic_data['id']}")
        else:
            print(f"❌ Failed to create topic: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
        # Test 5: Get topics
        print("📖 Testing topic retrieval...")
        response = requests.get(f"{base_url}/topics?curriculum_id={curriculum_data['id']}")
        if response.status_code == 200:
            topics = response.json()
            print(f"✅ Retrieved {len(topics)} topics")
        else:
            print(f"❌ Failed to retrieve topics: {response.status_code}")
            return False
        
        # Test 6: Create learning objective
        print("🎯 Testing learning objective creation...")
        objective_data = {
            "topic_id": topic_data["id"],
            "objective": "Students should be able to perform basic arithmetic operations accurately"
        }
        response = requests.post(f"{base_url}/learning-objectives", json=objective_data)
        if response.status_code == 200:
            print("✅ Learning objective created successfully")
        else:
            print(f"❌ Failed to create learning objective: {response.status_code}")
            return False
        
        # Test 7: Get learning objectives
        print("📖 Testing learning objective retrieval...")
        response = requests.get(f"{base_url}/topics/{topic_data['id']}/learning-objectives")
        if response.status_code == 200:
            objectives = response.json()
            print(f"✅ Retrieved {len(objectives)} learning objectives")
        else:
            print(f"❌ Failed to retrieve learning objectives: {response.status_code}")
            return False
        
        # Test 8: Search curricula
        print("🔍 Testing curriculum search...")
        response = requests.get(f"{base_url}/search/curriculums?search_term=Mathematics")
        if response.status_code == 200:
            search_results = response.json()
            print(f"✅ Search returned {len(search_results)} results")
        else:
            print(f"❌ Failed to search curricula: {response.status_code}")
            return False
        
        # Test 9: Get curriculum statistics
        print("📊 Testing curriculum statistics...")
        response = requests.get(f"{base_url}/{curriculum_data['id']}/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Retrieved statistics: {stats['total_topics']} topics, {stats['total_learning_objectives']} objectives")
        else:
            print(f"❌ Failed to get statistics: {response.status_code}")
            return False
        
        print("\n🎉 All API tests passed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def create_sample_data():
    """Create sample curriculum data for JSS1 Mathematics."""
    print("\n📝 Creating sample curriculum data...")
    
    base_url = "http://localhost:8000/api/curriculum"
    
    # Sample JSS1 Mathematics curriculum with multiple topics
    sample_curriculum = {
        "country": "Nigeria",
        "grade_level": "JSS1",
        "subject": "Mathematics",
        "theme": "Foundation Mathematics",
        "topics": [
            {
                "topic_code": "JSS1_MATH_001",
                "topic_title": "Number and Numeration",
                "description": "Introduction to numbers and basic numeration concepts",
                "learning_objectives": [
                    "Students should be able to identify and write numbers up to 1000",
                    "Students should be able to perform basic arithmetic operations",
                    "Students should understand place value concepts"
                ],
                "contents": [
                    "Whole numbers and their properties",
                    "Place value and expanded form",
                    "Basic arithmetic operations (addition, subtraction, multiplication, division)"
                ],
                "teacher_activities": [
                    "Use number charts and manipulatives to demonstrate place value",
                    "Guide students through step-by-step problem solving",
                    "Provide real-world examples of number usage"
                ],
                "student_activities": [
                    "Complete number pattern worksheets",
                    "Practice arithmetic operations with peers",
                    "Create number stories using real-life scenarios"
                ],
                "teaching_materials": [
                    "Number charts and place value charts",
                    "Manipulatives (counters, base-ten blocks)",
                    "Whiteboard and markers for demonstrations"
                ],
                "evaluation_guides": [
                    "Assess ability to write and read numbers correctly",
                    "Evaluate accuracy in arithmetic operations",
                    "Check understanding through word problems"
                ]
            },
            {
                "topic_code": "JSS1_MATH_002",
                "topic_title": "Fractions and Decimals",
                "description": "Understanding fractions and decimal numbers",
                "learning_objectives": [
                    "Students should be able to identify and represent fractions",
                    "Students should understand the relationship between fractions and decimals",
                    "Students should be able to perform basic operations with fractions"
                ],
                "contents": [
                    "Types of fractions (proper, improper, mixed)",
                    "Converting fractions to decimals and vice versa",
                    "Adding and subtracting fractions with like denominators"
                ],
                "teacher_activities": [
                    "Use visual models to demonstrate fractions",
                    "Show real-world applications of fractions",
                    "Guide students in fraction operations"
                ],
                "student_activities": [
                    "Create fraction models using paper folding",
                    "Solve fraction word problems",
                    "Practice converting between fractions and decimals"
                ],
                "teaching_materials": [
                    "Fraction circles and strips",
                    "Grid paper for visual representations",
                    "Calculators for decimal conversions"
                ],
                "evaluation_guides": [
                    "Assess understanding through fraction models",
                    "Evaluate problem-solving skills with fractions",
                    "Check accuracy in fraction operations"
                ]
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/bulk", json=sample_curriculum)
        if response.status_code == 200:
            print("✅ Sample curriculum data created successfully!")
            curriculum_data = response.json()
            print(f"   Curriculum ID: {curriculum_data['id']}")
            print(f"   Topics created: {len(curriculum_data['topics'])}")
            return True
        else:
            print(f"❌ Failed to create sample data: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Main function to set up and test the curriculum database."""
    print("🚀 Awade Curriculum Database Setup")
    print("=" * 50)
    
    # Step 1: Run migration
    if not run_migration():
        print("❌ Setup failed at migration step")
        return False
    
    # Step 2: Test API endpoints
    if not test_curriculum_api():
        print("❌ Setup failed at API testing step")
        return False
    
    # Step 3: Create sample data
    if not create_sample_data():
        print("❌ Setup failed at sample data creation step")
        return False
    
    print("\n🎉 Curriculum database setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. The database now contains the curriculum schema")
    print("2. Sample JSS1 Mathematics curriculum has been created")
    print("3. API endpoints are working and tested")
    print("4. You can now add more curriculum data using the API")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 