#!/usr/bin/env python3
"""
Test script for enhanced GPT functionality with prompt tuning.
Demonstrates the improved lesson plan generation and optimization features.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.ai.gpt_service import AwadeGPTService

def test_enhanced_lesson_plan_generation():
    """Test the enhanced lesson plan generation with improved prompts."""
    print("🧪 Testing Enhanced Lesson Plan Generation")
    print("=" * 50)
    
    try:
        gpt_service = AwadeGPTService()
        
        # Test parameters
        subject = "Mathematics"
        grade = "Grade 4"
        topic = "Fractions"
        objectives = [
            "Understand basic fraction concepts",
            "Identify fractions in everyday objects",
            "Compare simple fractions"
        ]
        duration = 45
        language = "en"
        cultural_context = "African"
        local_context = "Using local fruits and objects for fraction examples"
        
        print(f"📚 Generating lesson plan for {subject} - {topic} ({grade})")
        print(f"🎯 Objectives: {objectives}")
        print(f"🌍 Cultural Context: {cultural_context}")
        print(f"📍 Local Context: {local_context}")
        print()
        
        # Generate lesson plan
        result = gpt_service.generate_lesson_plan(
            subject=subject,
            grade=grade,
            topic=topic,
            objectives=objectives,
            duration=duration,
            language=language,
            cultural_context=cultural_context,
            local_context=local_context
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            print("📋 Fallback lesson plan generated:")
            fallback = result.get("fallback", {})
            print(f"   Title: {fallback.get('title', 'N/A')}")
            print(f"   Objectives: {fallback.get('objectives', [])}")
            print(f"   Activities: {len(fallback.get('activities', []))} activities")
        else:
            print("✅ Lesson plan generated successfully!")
            print(f"📝 Title: {result.get('title', 'N/A')}")
            print(f"🎯 Objectives: {len(result.get('objectives', []))} objectives")
            print(f"📚 Learning Objectives: {result.get('learning_objectives', 'N/A')[:100]}...")
            print(f"🌍 Local Context: {result.get('local_context', 'N/A')[:100]}...")
            print(f"🎮 Activities: {result.get('activities', 'N/A')[:100]}...")
            print(f"📊 Assessment: {result.get('assessment', 'N/A')[:100]}...")
            print(f"📋 Teacher Notes: {result.get('teacher_notes', 'N/A')[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None

def test_assessment_optimization():
    """Test the assessment optimization functionality."""
    print("\n🧪 Testing Assessment Optimization")
    print("=" * 50)
    
    try:
        gpt_service = AwadeGPTService()
        
        # Sample assessment content
        assessment_content = """
        1. What is a fraction?
        2. Give an example of a fraction.
        3. Compare 1/2 and 1/4.
        4. Draw a picture of 3/4.
        """
        
        print("📊 Optimizing assessment content...")
        print(f"📝 Original assessment: {assessment_content.strip()}")
        print()
        
        result = gpt_service.optimize_assessment(
            assessment_content=assessment_content,
            subject="Mathematics",
            grade="Grade 4",
            assessment_type="mixed"
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Assessment optimized successfully!")
            print(f"📊 Status: {result.get('status', 'N/A')}")
            print(f"📝 Optimized assessment preview: {result.get('optimized_assessment', 'N/A')[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None

def test_activity_enhancement():
    """Test the activity enhancement functionality."""
    print("\n🧪 Testing Activity Enhancement")
    print("=" * 50)
    
    try:
        gpt_service = AwadeGPTService()
        
        # Sample activities content
        activities_content = """
        1. Introduction: Show different fruits and ask students to identify parts
        2. Main activity: Use paper strips to demonstrate fractions
        3. Group work: Students work in pairs to create fraction examples
        """
        
        print("🎮 Enhancing classroom activities...")
        print(f"📝 Original activities: {activities_content.strip()}")
        print()
        
        result = gpt_service.enhance_activities(
            activities_content=activities_content,
            subject="Mathematics",
            grade="Grade 4",
            duration=45,
            resources="Paper, scissors, fruits, markers",
            class_size=25
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Activities enhanced successfully!")
            print(f"🎮 Status: {result.get('status', 'N/A')}")
            print(f"📝 Enhanced activities preview: {result.get('enhanced_activities', 'N/A')[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None

def test_curriculum_alignment():
    """Test the curriculum alignment functionality."""
    print("\n🧪 Testing Curriculum Alignment")
    print("=" * 50)
    
    try:
        gpt_service = AwadeGPTService()
        
        # Sample lesson content
        lesson_content = """
        This lesson introduces students to basic fraction concepts.
        Students will learn to identify fractions in everyday objects,
        understand fraction notation, and compare simple fractions.
        Activities include hands-on exploration with local materials.
        """
        
        print("📚 Aligning lesson with curriculum standards...")
        print(f"📝 Lesson content: {lesson_content.strip()}")
        print()
        
        result = gpt_service.align_curriculum(
            lesson_content=lesson_content,
            subject="Mathematics",
            grade="Grade 4",
            country="Nigeria"
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print("✅ Curriculum alignment completed!")
            print(f"📚 Status: {result.get('status', 'N/A')}")
            print(f"📝 Alignment analysis preview: {result.get('curriculum_alignment', 'N/A')[:200]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None

def test_content_explanation():
    """Test the content explanation functionality."""
    print("\n🧪 Testing Content Explanation")
    print("=" * 50)
    
    try:
        gpt_service = AwadeGPTService()
        
        # Sample AI-generated content
        content = """
        Use local fruits like oranges and bananas to teach fractions.
        Cut fruits into equal parts and have students identify fractions.
        This approach connects abstract concepts to concrete, familiar objects.
        """
        
        context = "Mathematics lesson for Grade 4 students in rural African school"
        
        print("💡 Explaining AI-generated content...")
        print(f"📝 Content: {content.strip()}")
        print(f"📋 Context: {context}")
        print()
        
        explanation = gpt_service.explain_ai_content(
            content=content,
            context=context
        )
        
        print("✅ Content explanation generated!")
        print(f"💡 Explanation preview: {explanation[:300]}...")
        
        return explanation
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return None

def main():
    """Run all GPT enhancement tests."""
    print("🚀 Awade GPT Enhancement Testing")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables")
        print("   Some tests may fail or use fallback responses")
        print()
    
    # Run tests
    results = {}
    
    results['lesson_plan'] = test_enhanced_lesson_plan_generation()
    results['assessment'] = test_assessment_optimization()
    results['activities'] = test_activity_enhancement()
    results['curriculum'] = test_curriculum_alignment()
    results['explanation'] = test_content_explanation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(results)
    
    for test_name, result in results.items():
        if result and not isinstance(result, str) and "error" not in result:
            status = "✅ PASSED"
            successful_tests += 1
        elif isinstance(result, str):
            status = "✅ PASSED"
            successful_tests += 1
        else:
            status = "❌ FAILED"
        
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n🎯 Overall: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! GPT enhancements are working correctly.")
    elif successful_tests > 0:
        print("⚠️  Some tests passed. Check individual results for details.")
    else:
        print("❌ All tests failed. Check configuration and API key.")
    
    # Save results to file
    output_file = "logs/gpt_enhancement_test_results.json"
    os.makedirs("logs", exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": f"{(successful_tests/total_tests)*100:.1f}%"
            },
            "results": results
        }, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main() 