#!/usr/bin/env python3
"""
Test login and check lesson resources
"""

import requests
import json

def test_login_and_resources():
    """Test login and check lesson resources"""
    base_url = "http://localhost:8000"
    
    # Test login with a user that has lesson resources
    login_data = {
        "email": "tolu3@gmail.com",  # User ID 11 has lesson resources
        "password": "password123"  # Assuming this is the password
    }
    
    try:
        # Login
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            user = data.get('user')
            print(f"Login successful for user: {user}")
            
            # Test lesson resources with token
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{base_url}/api/lesson-plans/resources", headers=headers)
            print(f"Resources response: {response.status_code}")
            
            if response.status_code == 200:
                resources = response.json()
                print(f"Found {len(resources)} lesson resources")
                if resources:
                    print(f"Sample resource: {resources[0]}")
            else:
                print(f"Resources error: {response.text}")
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login_and_resources() 