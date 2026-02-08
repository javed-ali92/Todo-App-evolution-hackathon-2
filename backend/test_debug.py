#!/usr/bin/env python3
"""
Debug script to test the exact issue in auth service
"""

from sqlmodel import Session
from src.database.database import engine
from src.models.user import User, UserCreate
from src.services.auth_service import create_user, authenticate_user, get_user_by_email
from src.auth.jwt_handler import get_password_hash

def test_user_operations():
    """Test user operations that are failing"""
    print("Testing user operations...")

    # Create a session
    with Session(engine) as session:
        print("Session created successfully")

        # Test 1: Try to get a non-existing user
        print("\n1. Testing get_user_by_email...")
        user = get_user_by_email(session, "nonexistent@example.com")
        print(f"Result: {user}")

        # Test 2: Try to create a new user
        print("\n2. Testing create_user...")
        try:
            user_create = UserCreate(
                username="testuser123",
                email="testuser123@example.com",
                password="testpassword123"
            )

            print(f"Attempting to create user: {user_create}")
            new_user = create_user(session, user_create)
            print(f"User created successfully: {new_user}")
            print(f"User ID: {new_user.id}")
            print(f"User username: {new_user.username}")
            print(f"User email: {new_user.email}")

            # Test 3: Try to authenticate the created user
            print("\n3. Testing authenticate_user...")
            authenticated_user = authenticate_user(session, "testuser123@example.com", "testpassword123")
            print(f"Authenticated user: {authenticated_user}")

            if authenticated_user:
                print("Authentication successful!")
                print(f"Authenticated user email: {authenticated_user.email}")
                print(f"Authenticated user username: {authenticated_user.username}")
            else:
                print("Authentication failed!")

        except Exception as e:
            print(f"Error during user operations: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_user_operations()