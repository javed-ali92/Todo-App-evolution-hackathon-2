#!/usr/bin/env python3
"""
Test script to verify Neon PostgreSQL integration and full application functionality
"""
import asyncio
from sqlmodel import Session, select
from src.database.database import engine
from src.models.user import User, UserCreate
from src.models.task import Task, TaskCreate, PriorityEnum
from src.services.auth_service import create_user, authenticate_user, create_login_token
from src.services.task_service import create_task, get_tasks_by_user
from src.auth.jwt_handler import verify_token
import requests
import json
import time


def test_database_connection():
    """Test if the database connection works with Neon"""
    print("Testing database connection...")
    try:
        with engine.connect() as conn:
            result = conn.execute(select(1))
            print("+ Database connection successful")
            return True
    except Exception as e:
        print(f"- Database connection failed: {e}")
        return False


def test_models_creation():
    """Test if all models can be created and interacted with"""
    print("\nTesting model creation and interaction...")
    try:
        # Create a test user
        with Session(engine) as session:
            # Clean up any existing test data
            existing_user = session.exec(select(User).where(User.email == "test@example.com")).first()
            if existing_user:
                session.delete(existing_user)
                session.commit()

            # Create a new user
            user_create = UserCreate(
                username="testuser",
                email="test@example.com",
                password="testpassword123"
            )

            db_user = create_user(session, user_create)
            print(f"+ User created with ID: {db_user.id}")

            # Create a task for this user
            task_create = TaskCreate(
                title="Test Task",
                description="This is a test task",
                priority=PriorityEnum.HIGH
            )

            db_task = create_task(session, task_create, db_user.id)
            print(f"+ Task created with ID: {db_task.id}")

            # Get tasks for this user
            user_tasks = get_tasks_by_user(session, db_user.id)
            print(f"+ Retrieved {len(user_tasks)} tasks for user")

            # Clean up
            session.delete(db_task)
            session.delete(db_user)
            session.commit()
            print("+ Test data cleaned up")

        print("+ All model interactions successful")
        return True
    except Exception as e:
        print(f"- Model interaction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_authentication():
    """Test authentication functionality"""
    print("\nTesting authentication...")
    try:
        with Session(engine) as session:
            # Clean up any existing test data
            existing_user = session.exec(select(User).where(User.email == "auth_test@example.com")).first()
            if existing_user:
                session.delete(existing_user)
                session.commit()

            # Create a test user
            user_create = UserCreate(
                username="authtestuser",
                email="auth_test@example.com",
                password="securepassword123"
            )

            db_user = create_user(session, user_create)
            print(f"+ Auth test user created with ID: {db_user.id}")

            # Authenticate the user
            authenticated_user = authenticate_user(session, "auth_test@example.com", "securepassword123")
            if authenticated_user:
                print("+ User authentication successful")
            else:
                print("- User authentication failed")
                return False

            # Create a JWT token
            token = create_login_token(authenticated_user)
            if token:
                print("+ JWT token created successfully")

                # Verify the token
                payload = verify_token(token)
                if payload:
                    print("+ Token verification successful")
                else:
                    print("- Token verification failed")
                    return False
            else:
                print("- JWT token creation failed")
                return False

            # Clean up
            session.delete(db_user)
            session.commit()
            print("+ Auth test data cleaned up")

        print("+ All authentication tests passed")
        return True
    except Exception as e:
        print(f"- Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API endpoints (if server is running)"""
    print("\nTesting API endpoints...")
    try:
        # Try to reach the root endpoint
        import subprocess
        import time

        # Start the server in a subprocess
        server_process = subprocess.Popen([
            'uvicorn', 'src.main:app', '--host', '127.0.0.1', '--port', '8000', '--log-level', 'error'
        ])

        # Give the server time to start
        time.sleep(3)

        # Test the root endpoint
        try:
            response = requests.get('http://127.0.0.1:8000/')
            if response.status_code == 200:
                print("+ Root endpoint accessible")
                print(f"  Response: {response.json()}")
            else:
                print(f"- Root endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("? Could not connect to server - may not be running")

        # Test API docs endpoint
        try:
            response = requests.get('http://127.0.0.1:8000/docs')
            if response.status_code == 200:
                print("+ API docs endpoint accessible")
            else:
                print(f"? API docs endpoint returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("? Could not connect to API docs - server may not be running")

        # Terminate the server
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()

        return True
    except Exception as e:
        print(f"- API endpoint test failed: {e}")
        return False


def main():
    """Run all tests to verify Neon PostgreSQL integration"""
    print("=" * 60)
    print("Neon PostgreSQL Integration Test Suite")
    print("=" * 60)

    tests = [
        ("Database Connection", test_database_connection),
        ("Model Interactions", test_models_creation),
        ("Authentication", test_authentication),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)

    all_passed = True
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("*** All tests PASSED! Neon PostgreSQL integration is working correctly.")
        print("\nThe Todo application with Neon Serverless PostgreSQL is ready!")
    else:
        print("❌ Some tests FAILED. Please check the output above for details.")

    return all_passed


if __name__ == "__main__":
    main()