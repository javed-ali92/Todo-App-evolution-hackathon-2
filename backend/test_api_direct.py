#!/usr/bin/env python3
"""
Direct API test to see the actual error
"""

from fastapi.testclient import TestClient
from src.main import app

def test_api_endpoints():
    client = TestClient(app)

    print("Testing API endpoints directly...")

    # Test the root endpoint
    response = client.get("/")
    print(f"Root endpoint status: {response.status_code}")
    print(f"Root endpoint response: {response.json()}")

    # Test the auth register endpoint
    print("\nTesting registration endpoint...")
    response = client.post(
        "/api/auth/register",
        json={
            "username": "apitestuser",
            "email": "apitest@example.com",
            "password": "apitestpassword123"
        }
    )
    print(f"Registration status: {response.status_code}")
    if response.status_code != 200 and response.status_code != 201:
        print(f"Registration error response: {response.text}")
    else:
        print(f"Registration success: {response.json()}")

    # Test the auth token endpoint
    print("\nTesting login endpoint...")
    response = client.post(
        "/api/auth/token",
        json={
            "email": "apitest@example.com",
            "password": "apitestpassword123"
        }
    )
    print(f"Login status: {response.status_code}")
    if response.status_code != 200:
        print(f"Login error response: {response.text}")
    else:
        print(f"Login success: {response.json()}")

if __name__ == "__main__":
    test_api_endpoints()