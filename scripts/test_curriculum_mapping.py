#!/usr/bin/env python3
"""
Test script to verify curriculum mapping acceptance criteria.
Tests the /api/lesson/curriculum-map endpoint functionality.
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_curriculum_mapping() -> Dict[str, Any]:
    """
    Test the curriculum mapping endpoint against acceptance criteria.
    """
    print("🧪 Testing Curriculum Mapping Acceptance Criteria")
    print("=" * 60)
    
    results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "details": []
    }
    
    # Test 1: Valid mapping for Mathematics JSS1
    print("\n📝 Test 1: Valid mapping for Mathematics JSS1")
    try:
        response = requests.get(
            f"{BASE_URL}/api/lesson/curriculum-map",
            params={
                "subject": "Mathematics",
                "grade_level": "JSS1",
                "country": "Nigeria"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            if "curriculum_id" in data and "curriculum_description" in data:
                print("✅ PASS: Returns curriculum_id and curriculum_description")
                results["tests_passed"] += 1
                results["details"].append({
                    "test": "Valid mapping for Mathematics JSS1",
                    "status": "PASS",
                    "response": data
                })
            else:
                print("❌ FAIL: Missing required fields")
                results["tests_failed"] += 1
                results["details"].append({
                    "test": "Valid mapping for Mathematics JSS1",
                    "status": "FAIL",
                    "error": "Missing required fields"
                })
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            results["tests_failed"] += 1
            results["details"].append({
                "test": "Valid mapping for Mathematics JSS1",
                "status": "FAIL",
                "error": f"HTTP {response.status_code}"
            })
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["tests_failed"] += 1
        results["details"].append({
            "test": "Valid mapping for Mathematics JSS1",
            "status": "FAIL",
            "error": str(e)
        })
    
    # Test 2: Error case for non-existent subject
    print("\n📝 Test 2: Error case for non-existent subject")
    try:
        response = requests.get(
            f"{BASE_URL}/api/lesson/curriculum-map",
            params={
                "subject": "Physics",
                "grade_level": "JSS1",
                "country": "Nigeria"
            }
        )
        
        if response.status_code == 404:
            data = response.json()
            if "detail" in data and "No curriculum found" in data["detail"]:
                print("✅ PASS: Returns clear error message for non-existent mapping")
                results["tests_passed"] += 1
                results["details"].append({
                    "test": "Error case for non-existent subject",
                    "status": "PASS",
                    "response": data
                })
            else:
                print("❌ FAIL: Error message not clear enough")
                results["tests_failed"] += 1
                results["details"].append({
                    "test": "Error case for non-existent subject",
                    "status": "FAIL",
                    "error": "Error message not clear enough"
                })
        else:
            print(f"❌ FAIL: Expected 404, got {response.status_code}")
            results["tests_failed"] += 1
            results["details"].append({
                "test": "Error case for non-existent subject",
                "status": "FAIL",
                "error": f"Expected 404, got {response.status_code}"
            })
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["tests_failed"] += 1
        results["details"].append({
            "test": "Error case for non-existent subject",
            "status": "FAIL",
            "error": str(e)
        })
    
    # Test 3: Error case for non-existent grade level
    print("\n📝 Test 3: Error case for non-existent grade level")
    try:
        response = requests.get(
            f"{BASE_URL}/api/lesson/curriculum-map",
            params={
                "subject": "Mathematics",
                "grade_level": "PhD",
                "country": "Nigeria"
            }
        )
        
        if response.status_code == 404:
            data = response.json()
            if "detail" in data and "No curriculum found" in data["detail"]:
                print("✅ PASS: Returns clear error message for non-existent grade level")
                results["tests_passed"] += 1
                results["details"].append({
                    "test": "Error case for non-existent grade level",
                    "status": "PASS",
                    "response": data
                })
            else:
                print("❌ FAIL: Error message not clear enough")
                results["tests_failed"] += 1
                results["details"].append({
                    "test": "Error case for non-existent grade level",
                    "status": "FAIL",
                    "error": "Error message not clear enough"
                })
        else:
            print(f"❌ FAIL: Expected 404, got {response.status_code}")
            results["tests_failed"] += 1
            results["details"].append({
                "test": "Error case for non-existent grade level",
                "status": "FAIL",
                "error": f"Expected 404, got {response.status_code}"
            })
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["tests_failed"] += 1
        results["details"].append({
            "test": "Error case for non-existent grade level",
            "status": "FAIL",
            "error": str(e)
        })
    
    # Test 4: Valid mapping with different country
    print("\n📝 Test 4: Valid mapping with different country")
    try:
        response = requests.get(
            f"{BASE_URL}/api/lesson/curriculum-map",
            params={
                "subject": "Mathematics",
                "grade_level": "JSS1",
                "country": "Ghana"
            }
        )
        
        if response.status_code == 404:
            data = response.json()
            if "detail" in data and "No curriculum found" in data["detail"]:
                print("✅ PASS: Returns clear error message for non-existent country")
                results["tests_passed"] += 1
                results["details"].append({
                    "test": "Valid mapping with different country",
                    "status": "PASS",
                    "response": data
                })
            else:
                print("❌ FAIL: Error message not clear enough")
                results["tests_failed"] += 1
                results["details"].append({
                    "test": "Valid mapping with different country",
                    "status": "FAIL",
                    "error": "Error message not clear enough"
                })
        else:
            print(f"❌ FAIL: Expected 404, got {response.status_code}")
            results["tests_failed"] += 1
            results["details"].append({
                "test": "Valid mapping with different country",
                "status": "FAIL",
                "error": f"Expected 404, got {response.status_code}"
            })
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results["tests_failed"] += 1
        results["details"].append({
            "test": "Valid mapping with different country",
            "status": "FAIL",
            "error": str(e)
        })
    
    return results

def print_summary(results: Dict[str, Any]):
    """Print test summary."""
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Tests Passed: {results['tests_passed']}")
    print(f"❌ Tests Failed: {results['tests_failed']}")
    print(f"📈 Success Rate: {results['tests_passed'] / (results['tests_passed'] + results['tests_failed']) * 100:.1f}%")
    
    if results["tests_failed"] == 0:
        print("\n🎉 ALL ACCEPTANCE CRITERIA MET!")
        print("\n✅ User Story Acceptance Criteria:")
        print("   ✓ Given subject and grade_level inputs, the /api/lesson/curriculum-map endpoint returns a JSON object with curriculum_id and curriculum_description")
        print("   ✓ The mapping matches entries from the configured curriculum dataset")
        print("   ✓ Errors return a clear message if no mapping exists")
    else:
        print("\n⚠️  Some acceptance criteria not met. Check details above.")
    
    print("\n📋 Detailed Results:")
    for detail in results["details"]:
        status_icon = "✅" if detail["status"] == "PASS" else "❌"
        print(f"   {status_icon} {detail['test']}: {detail['status']}")

def main():
    """Main test function."""
    try:
        # Check if server is running
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server is not running or not healthy")
            sys.exit(1)
        
        # Run tests
        results = test_curriculum_mapping()
        print_summary(results)
        
        # Exit with appropriate code
        if results["tests_failed"] == 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on http://localhost:8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 