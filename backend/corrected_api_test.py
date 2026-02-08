#!/usr/bin/env python3
"""
Corrected test to use proper API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing API endpoints with correct methods...")

# Test root
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"ROOT: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"ROOT ERROR: {e}")

# Test registration
print("\nTesting registration...")
user_data = {
    "username": "apitestuser",
    "email": "api@test.com",
    "password": "apitestpassword123"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
    print(f"REGISTER: {response.status_code}")
    if response.status_code == 201 or response.status_code == 200:
        print("Registration successful")
        user = response.json()
        print(f"User ID: {user.get('id')}, Email: {user.get('email')}")
    elif response.status_code == 409:
        print("User already exists (OK for testing)")
        # Continue with login
    else:
        print(f"Registration failed: {response.text}")
except Exception as e:
    print(f"REGISTER ERROR: {e}")

# Test login using form data (as required by the API spec)
print("\nTesting login with FORM DATA...")
login_data = {
    "email": "api@test.com",
    "password": "apitestpassword123"
}

try:
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)  # Using data= for form data
    print(f"LOGIN (form): {response.status_code}")
    if response.status_code == 200:
        auth_data = response.json()
        token = auth_data.get('access_token')
        user_id = auth_data.get('user_id')
        print(f"Login successful, Token length: {len(token) if token else 0}")
        print(f"User ID: {user_id}")

        # Test accessing protected endpoint
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            print(f"USER INFO: {response.status_code}")
            if response.status_code == 200:
                user_info = response.json()
                print(f"User info retrieved: {user_info.get('email')} (ID: {user_info.get('id')})")

                # Test creating a task
                task_data = {
                    "title": "API Test Task",
                    "description": "Task created via API test",
                    "completed": False
                }
                user_id = user_info.get('id')
                response = requests.post(f"{BASE_URL}/api/{user_id}/tasks",
                                       json=task_data,
                                       headers=headers)
                print(f"CREATE TASK: {response.status_code}")
                if response.status_code == 200:  # According to spec, it returns 200 not 201
                    task = response.json()
                    print(f"Task created: {task.get('title')} (ID: {task.get('id')})")

                    # Test getting the task
                    task_id = task.get('id')
                    response = requests.get(f"{BASE_URL}/api/{user_id}/tasks/{task_id}", headers=headers)
                    print(f"GET TASK: {response.status_code}")
                    if response.status_code == 200:
                        retrieved_task = response.json()
                        print(f"Task retrieved: {retrieved_task.get('title')}")

    else:
        print(f"Login failed: {response.text}")
        # Try with existing user
        login_data_alt = {"email": "api@test.com", "password": "apitestpassword123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data_alt)
        if response.status_code == 200:
            print("Login successful with existing user!")
        else:
            print(f"Even existing user login failed: {response.text}")

except Exception as e:
    print(f"LOGIN ERROR: {e}")

print("\nCorrected API test completed!")
print("\nKEY POINTS:")
print("- Login endpoint expects FORM DATA (not JSON)")
print("- Use 'data=' parameter in requests.post() for login")
print("- All task endpoints require valid JWT token in Authorization header")
print("- User ID in URL path must match the authenticated user ID")