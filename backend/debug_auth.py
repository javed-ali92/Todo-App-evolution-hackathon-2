#!/usr/bin/env python3
"""
Debug script to test the auth endpoint and see the exact error
"""

import sys
import traceback
from fastapi.testclient import TestClient
from src.main import app

def test_auth_endpoint():
    client = TestClient(app)

    print("Testing /api/auth/token endpoint...")

    try:
        response = client.post(
            "/api/auth/token",
            json={"email": "test@test.com", "password": "test123"}
        )
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")

        if response.status_code == 500:
            print("\nFull error traceback:")
            # Let's try to reproduce the issue by calling the endpoint function directly
            from src.api.auth import login_json
            from sqlmodel import Session
            from src.database.database import engine

            # Try to call the function directly to see the error
            with Session(engine) as session:
                from src.models.user import UserLogin
                login_data = UserLogin(email="test@test.com", password="test123")

                try:
                    result = login_json(login_data, session)
                    print(f"Direct function call result: {result}")
                except Exception as e:
                    print(f"Direct function call error: {e}")
                    traceback.print_exc()

    except Exception as e:
        print(f"Error testing endpoint: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_auth_endpoint()