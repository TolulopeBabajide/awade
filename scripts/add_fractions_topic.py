#!/usr/bin/env python3
"""
Script to add the Fractions topic to the curriculum database.
"""

import requests
import json
import sys

def add_fractions_topic():
    """Add the Fractions topic to the curriculum database."""
    print("📝 Adding Fractions topic to curriculum database...")
    
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
    
    # Create the Fractions topic
    fractions_topic = {
        "curriculum_id": curriculum_id,
        "topic_code": "MTH-JSS1-FRACTIONS",
        "topic_title": "Fractions",
        "description": "Understanding fractions, equivalent fractions, and conversions between fractions, decimals, and percentages"
    }
    
    print("📝 Creating Fractions topic...")
    response = requests.post(f"{base_url}/topics", json=fractions_topic)
    
    if response.status_code != 200:
        print(f"❌ Failed to create topic: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    topic_data = response.json()
    topic_id = topic_data['id']
    print(f"✅ Created topic ID: {topic_id}")
    
    # Add learning objectives
    performance_objectives = [
        "Identify equivalent fractions of any given fraction",
        "Apply equivalent fractions in sharing of commodities",
        "Solve problems in quantitative aptitude using equivalent fractions",
        "Convert between fractions, decimals, and percentages"
    ]
    
    print("🎯 Adding learning objectives...")
    for objective in performance_objectives:
        objective_data = {
            "topic_id": topic_id,
            "objective": objective
        }
        response = requests.post(f"{base_url}/learning-objectives", json=objective_data)
        if response.status_code != 200:
            print(f"❌ Failed to add objective: {objective}")
            return False
    
    print(f"✅ Added {len(performance_objectives)} learning objectives")
    
    # Add content areas
    contents = [
        "Equivalent fractions",
        "Ordering of fractions",
        "Conversion: fractions <-> decimals",
        "Conversion: fractions <-> percentages"
    ]
    
    print("📖 Adding content areas...")
    for content in contents:
        content_data = {
            "topic_id": topic_id,
            "content_area": content
        }
        response = requests.post(f"{base_url}/contents", json=content_data)
        if response.status_code != 200:
            print(f"❌ Failed to add content: {content}")
            return False
    
    print(f"✅ Added {len(contents)} content areas")
    
    # Add teacher activities
    teacher_activities = [
        "Use charts and visual aids to demonstrate fraction equivalence",
        "Guide students in converting between forms",
        "Lead problem-solving sessions with real-life scenarios (e.g. money sharing)"
    ]
    
    print("👨‍🏫 Adding teacher activities...")
    for activity in teacher_activities:
        activity_data = {
            "topic_id": topic_id,
            "activity": activity
        }
        response = requests.post(f"{base_url}/teacher-activities", json=activity_data)
        if response.status_code != 200:
            print(f"❌ Failed to add teacher activity: {activity}")
            return False
    
    print(f"✅ Added {len(teacher_activities)} teacher activities")
    
    # Add student activities
    student_activities = [
        "Recognize equivalent fractions (e.g. ½ = 2/4 = 4/8)",
        "Apply fractions to food/money sharing problems",
        "Convert given fractions to decimals and percentages",
        "Solve real-life word problems"
    ]
    
    print("👨‍🎓 Adding student activities...")
    for activity in student_activities:
        activity_data = {
            "topic_id": topic_id,
            "activity": activity
        }
        response = requests.post(f"{base_url}/student-activities", json=activity_data)
        if response.status_code != 200:
            print(f"❌ Failed to add student activity: {activity}")
            return False
    
    print(f"✅ Added {len(student_activities)} student activities")
    
    # Add teaching materials
    teaching_materials = [
        "Charts of equivalent fractions",
        "Fraction flash cards",
        "Conversion charts for fractions/percentages/decimals"
    ]
    
    print("📚 Adding teaching materials...")
    for material in teaching_materials:
        material_data = {
            "topic_id": topic_id,
            "material": material
        }
        response = requests.post(f"{base_url}/teaching-materials", json=material_data)
        if response.status_code != 200:
            print(f"❌ Failed to add teaching material: {material}")
            return False
    
    print(f"✅ Added {len(teaching_materials)} teaching materials")
    
    # Add evaluation guides
    evaluation_guides = [
        "Solve problems on equivalent fractions",
        "Convert between forms accurately",
        "Apply reasoning in practical problems"
    ]
    
    print("📊 Adding evaluation guides...")
    for guide in evaluation_guides:
        guide_data = {
            "topic_id": topic_id,
            "guide": guide
        }
        response = requests.post(f"{base_url}/evaluation-guides", json=guide_data)
        if response.status_code != 200:
            print(f"❌ Failed to add evaluation guide: {guide}")
            return False
    
    print(f"✅ Added {len(evaluation_guides)} evaluation guides")
    
    # Verify the topic was created successfully
    print("🔍 Verifying topic creation...")
    response = requests.get(f"{base_url}/topics/{topic_id}")
    if response.status_code == 200:
        topic_detail = response.json()
        print(f"✅ Topic verified: {topic_detail['topic_title']}")
        print(f"   Learning objectives: {len(topic_detail['learning_objectives'])}")
        print(f"   Content areas: {len(topic_detail['contents'])}")
        print(f"   Teacher activities: {len(topic_detail['teacher_activities'])}")
        print(f"   Student activities: {len(topic_detail['student_activities'])}")
        print(f"   Teaching materials: {len(topic_detail['teaching_materials'])}")
        print(f"   Evaluation guides: {len(topic_detail['evaluation_guides'])}")
    else:
        print("❌ Failed to verify topic")
        return False
    
    print("\n🎉 Fractions topic added successfully!")
    print(f"📋 Topic ID: {topic_id}")
    print(f"📋 Topic Code: {topic_data['topic_code']}")
    print(f"📋 Topic Title: {topic_data['topic_title']}")
    
    return True

def main():
    """Main function."""
    print("🚀 Adding Fractions Topic to Curriculum")
    print("=" * 50)
    
    try:
        success = add_fractions_topic()
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