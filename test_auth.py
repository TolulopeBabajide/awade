#!/usr/bin/env python3
"""
Test authentication and check current user
"""

import requests
import json

def test_auth():
    """Test authentication and get current user"""
    base_url = "http://localhost:8000"
    
    # Test the health endpoint first
    try:
        response = requests.get(f"{base_url}/api/lesson-plans/ai/health")
        print(f"Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return
    
    # Test getting current user (this will fail without auth, but we can see the error)
    try:
        response = requests.get(f"{base_url}/api/auth/me")
        print(f"Auth check: {response.status_code}")
        if response.status_code == 200:
            print(f"Current user: {response.json()}")
        else:
            print(f"Auth error: {response.text}")
    except Exception as e:
        print(f"Auth check failed: {e}")
    
    # Test lesson resources endpoint
    try:
        response = requests.get(f"{base_url}/api/lesson-plans/resources")
        print(f"Resources check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} lesson resources")
            if data:
                print(f"Sample resource: {data[0]}")
        else:
            print(f"Resources error: {response.text}")
    except Exception as e:
        print(f"Resources check failed: {e}")

if __name__ == "__main__":
    test_auth() 