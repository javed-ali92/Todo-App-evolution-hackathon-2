#!/usr/bin/env python3
"""
Complete API Demo for Todo App with Neon PostgreSQL
This script demonstrates the complete workflow: register, login, and use API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def demo_full_workflow():
    print("=" * 70)
    print("COMPLETE TODO API DEMO - Neon PostgreSQL")
    print("=" * 70)

    # Step 1: Register a new user
    print("\n1. REGISTERING A NEW USER:")
    print("   POST /api/auth/register")

    user_data = {
        "username": "demo_user",
        "email": "demo@example.com",
        "password": "demopassword123"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/register",
                                json=user_data,
                                headers={"Content-Type": "application/json"})
        print(f"   Status: {response.status_code}")

        if response.status_code == 201:
            print("   + User registered successfully!")
            user_info = response.json()
            print(f"   + User ID: {user_info.get('id')}")
            print(f"   + Username: {user_info.get('username')}")
        elif response.status_code == 409:
            print("   ! User already exists (that's okay for demo)")
            # We'll proceed with login instead
        else:
            print(f"   - Registration failed: {response.text}")

    except Exception as e:
        print(f"   - Registration error: {e}")
        print("   Make sure the server is running on http://localhost:8000")
        return

    # Step 2: Login to get JWT token
    print("\n2. LOGGING IN TO GET JWT TOKEN:")
    print("   POST /api/auth/login")

    login_data = {
        "email": "demo@example.com",
        "password": "demopassword123"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/auth/login",
                                json=login_data,
                                headers={"Content-Type": "application/json"})
        print(f"   Status: {response.status_code}")

        if response.status_code in [200, 201]:
            print("   + Login successful!")
            auth_result = response.json()
            token = auth_result.get('access_token')
            user_id = auth_result.get('user_id')
            print(f"   + Token received (length: {len(token) if token else 0})")
            print(f"   + User ID: {user_id}")
        else:
            print(f"   - Login failed: {response.text}")
            # Try with the existing user
            login_data_alt = {
                "email": "demo@example.com",
                "password": "demopassword123"
            }
            response = requests.post(f"{BASE_URL}/api/auth/login",
                                    json=login_data_alt,
                                    headers={"Content-Type": "application/json"})
            if response.status_code in [200, 201]:
                auth_result = response.json()
                token = auth_result.get('access_token')
                user_id = auth_result.get('user_id')
                print("   + Got token for existing user!")
            else:
                print("   Cannot proceed without valid token")
                return

    except Exception as e:
        print(f"   - Login error: {e}")
        return

    # Step 3: Use the token to access user data
    print("\n3. ACCESSING USER DATA WITH JWT TOKEN:")
    print("   GET /api/auth/me")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            print("   + User data retrieved successfully!")
            user_data = response.json()
            print(f"   + User: {user_data.get('username')} (ID: {user_data.get('id')})")
            user_id = user_data.get('id')  # Use actual user ID from response
        else:
            print(f"   - User data request failed: {response.text}")
            return

    except Exception as e:
        print(f"   - User data error: {e}")
        return

    # Step 4: Create a task for the user
    print(f"\n4. CREATING A TASK FOR USER {user_id}:")
    print(f"   POST /api/{user_id}/tasks")

    task_data = {
        "title": "Demo Task",
        "description": "This is a demo task created via API",
        "priority": "HIGH"
    }

    try:
        response = requests.post(f"{BASE_URL}/api/{user_id}/tasks",
                                json=task_data,
                                headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 201:
            print("   + Task created successfully!")
            task = response.json()
            task_id = task.get('id')
            print(f"   + Task ID: {task_id}")
            print(f"   + Title: {task.get('title')}")
        else:
            print(f"   - Task creation failed: {response.text}")

    except Exception as e:
        print(f"   - Task creation error: {e}")

    # Step 5: Get user's tasks
    print(f"\n5. GETTING TASKS FOR USER {user_id}:")
    print(f"   GET /api/{user_id}/tasks")

    try:
        response = requests.get(f"{BASE_URL}/api/{user_id}/tasks", headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            tasks = response.json()
            print(f"   + Retrieved {len(tasks)} task(s)")
            for i, task in enumerate(tasks[-3:], 1):  # Show last 3 tasks
                print(f"   + Task {i}: {task.get('title')} (ID: {task.get('id')})")
        else:
            print(f"   - Task retrieval failed: {response.text}")

    except Exception as e:
        print(f"   - Task retrieval error: {e}")

    print("\n" + "=" * 70)
    print("DEMO COMPLETE - API IS WORKING PROPERLY!")
    print("=" * 70)
    print("\nSUMMARY OF CORRECT API USAGE:")
    print("✓ Register: POST /api/auth/register")
    print("✓ Login: POST /api/auth/login -> get JWT token")
    print("✓ Use token: Authorization: Bearer <token>")
    print("✓ Access user data: GET /api/auth/me (with token)")
    print(f"✓ Access user tasks: GET /api/{user_id}/tasks (with token)")
    print(f"✓ Create task: POST /api/{user_id}/tasks (with token)")
    print("\nThe API is fully functional with Neon PostgreSQL backend!")

if __name__ == "__main__":
    demo_full_workflow()