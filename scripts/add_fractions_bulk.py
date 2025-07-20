#!/usr/bin/env python3
"""
Script to add the Fractions topic to the curriculum database using bulk API.
"""

import requests
import json
import sys

def add_fractions_topic_bulk():
    """Add the Fractions topic using bulk API."""
    print("📝 Adding Fractions topic using bulk API...")
    
    base_url = "http://localhost:8000/api/curriculum"
    
    # First, get the existing curriculum
    print("🔍 Finding existing JSS1 Mathematics curriculum...")
    response = requests.get(f"{base_url}/?country=Nigeria&grade_level=JSS1&subject=Mathematics")
    
    if response.status_code != 200:
        print("❌ Failed to retrieve curricula")
        return False
    
    curricula = response.json()
    if not curricula:
        print("❌ No JSS1 Mathematics curriculum found")
        return False
    
    curriculum_id = curricula[0]['id']
    print(f"✅ Found curriculum ID: {curriculum_id}")
    
    # Create bulk curriculum data with Fractions topic
    bulk_curriculum = {
        "country": "Nigeria",
        "grade_level": "JSS1", 
        "subject": "Mathematics",
        "theme": "Foundation Mathematics",
        "topics": [
            {
                "topic_code": "MTH-JSS1-FRACTIONS",
                "topic_title": "Fractions",
                "description": "Understanding fractions, equivalent fractions, and conversions between fractions, decimals, and percentages",
                "learning_objectives": [
                    "Identify equivalent fractions of any given fraction",
                    "Apply equivalent fractions in sharing of commodities", 
                    "Solve problems in quantitative aptitude using equivalent fractions",
                    "Convert between fractions, decimals, and percentages"
                ],
                "contents": [
                    "Equivalent fractions",
                    "Ordering of fractions",
                    "Conversion: fractions <-> decimals",
                    "Conversion: fractions <-> percentages"
                ],
                "teacher_activities": [
                    "Use charts and visual aids to demonstrate fraction equivalence",
                    "Guide students in converting between forms",
                    "Lead problem-solving sessions with real-life scenarios (e.g. money sharing)"
                ],
                "student_activities": [
                    "Recognize equivalent fractions (e.g. ½ = 2/4 = 4/8)",
                    "Apply fractions to food/money sharing problems",
                    "Convert given fractions to decimals and percentages",
                    "Solve real-life word problems"
                ],
                "teaching_materials": [
                    "Charts of equivalent fractions",
                    "Fraction flash cards", 
                    "Conversion charts for fractions/percentages/decimals"
                ],
                "evaluation_guides": [
                    "Solve problems on equivalent fractions",
                    "Convert between forms accurately",
                    "Apply reasoning in practical problems"
                ]
            }
        ]
    }
    
    print("📝 Creating Fractions topic using bulk API...")
    response = requests.post(f"{base_url}/bulk", json=bulk_curriculum)
    
    if response.status_code != 200:
        print(f"❌ Failed to create topic: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    curriculum_data = response.json()
    print(f"✅ Created curriculum with ID: {curriculum_data['id']}")
    
    # Find the Fractions topic
    fractions_topic = None
    for topic in curriculum_data['topics']:
        if topic['topic_code'] == 'MTH-JSS1-FRACTIONS':
            fractions_topic = topic
            break
    
    if not fractions_topic:
        print("❌ Fractions topic not found in response")
        return False
    
    print(f"✅ Fractions topic created successfully!")
    print(f"📋 Topic ID: {fractions_topic['id']}")
    print(f"📋 Topic Code: {fractions_topic['topic_code']}")
    print(f"📋 Topic Title: {fractions_topic['topic_title']}")
    print(f"📋 Learning objectives: {len(fractions_topic['learning_objectives'])}")
    print(f"📋 Content areas: {len(fractions_topic['contents'])}")
    print(f"📋 Teacher activities: {len(fractions_topic['teacher_activities'])}")
    print(f"📋 Student activities: {len(fractions_topic['student_activities'])}")
    print(f"📋 Teaching materials: {len(fractions_topic['teaching_materials'])}")
    print(f"📋 Evaluation guides: {len(fractions_topic['evaluation_guides'])}")
    
    return True

def main():
    """Main function."""
    print("🚀 Adding Fractions Topic to Curriculum (Bulk Method)")
    print("=" * 60)
    
    try:
        success = add_fractions_topic_bulk()
        if success:
            print("\n✅ Fractions topic addition completed successfully!")
            return True
        else:
            print("\n❌ Failed to add Fractions topic")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 