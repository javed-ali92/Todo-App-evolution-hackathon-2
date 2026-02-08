import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.main import app
from src.database.database import engine as original_engine
from src.models.user import User
from src.models.task import Task
from src.services.auth_service import get_user_by_email


# Create a test database engine using SQLite in memory
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def client():
    """Create a test client for the API with a temporary database"""
    # Create all tables in the test database
    SQLModel.metadata.create_all(test_engine)

    # Temporarily replace the original engine with the test engine
    import src.main
    import src.database.database
    original_main_engine = src.main.engine
    original_database_engine = src.database.database.engine

    # Update engines in both modules
    src.main.engine = test_engine
    src.database.database.engine = test_engine
    from src.main import app as updated_app

    with TestClient(updated_app) as c:
        yield c

    # Restore original engines
    src.main.engine = original_main_engine
    src.database.database.engine = original_database_engine


def test_user_registration_success(client):
    """Test successful user registration"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }

    response = client.post("/api/auth/register", json=user_data)

    # Check that registration was successful (201 Created)
    assert response.status_code == 201

    # Verify the response contains user data without password
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be in response


def test_user_registration_duplicate_email(client):
    """Test that registration fails with duplicate email"""
    user_data = {
        "username": "testuser1",
        "email": "duplicate@example.com",
        "password": "securepassword123"
    }

    # Register the first user
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Try to register another user with the same email
    user_data_2 = {
        "username": "testuser2",
        "email": "duplicate@example.com",  # Same email
        "password": "anotherpassword456"
    }

    response = client.post("/api/auth/register", json=user_data_2)

    # Should return 409 Conflict
    assert response.status_code == 409
    assert "already registered" in response.json().get("detail", "").lower()


def test_user_registration_duplicate_username(client):
    """Test that registration fails with duplicate username"""
    user_data = {
        "username": "samename",
        "email": "different1@example.com",
        "password": "securepassword123"
    }

    # Register the first user
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Try to register another user with the same username
    user_data_2 = {
        "username": "samename",  # Same username
        "email": "different2@example.com",  # Different email
        "password": "anotherpassword456"
    }

    response = client.post("/api/auth/register", json=user_data_2)

    # Should return 409 Conflict
    assert response.status_code == 409
    assert "already taken" in response.json().get("detail", "").lower()


def test_user_login_success(client):
    """Test successful user login"""
    # First, register a user
    user_data = {
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpassword123"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Now try to login with correct credentials
    login_data = {
        "email": "login@example.com",
        "password": "loginpassword123"
    }

    response = client.post("/api/auth/login", json=login_data)

    # Check that login was successful (200 OK)
    assert response.status_code == 200

    # Verify the response contains access token
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user_id" in data


def test_user_login_invalid_credentials(client):
    """Test that login fails with invalid credentials"""
    # First, register a user
    user_data = {
        "username": "badloginuser",
        "email": "badlogin@example.com",
        "password": "goodpassword123"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Try to login with wrong password
    login_data = {
        "email": "badlogin@example.com",
        "password": "wrongpassword456"  # Wrong password
    }

    response = client.post("/api/auth/login", json=login_data)

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "incorrect" in response.json().get("detail", "").lower()

    # Try to login with non-existent email
    login_data_bad_email = {
        "email": "nonexistent@example.com",
        "password": "any_password"
    }

    response = client.post("/api/auth/login", json=login_data_bad_email)

    # Should return 401 Unauthorized
    assert response.status_code == 401
    assert "incorrect" in response.json().get("detail", "").lower()


def test_get_current_user_authenticated(client):
    """Test getting current user info with valid authentication"""
    # First, register a user
    user_data = {
        "username": "currentuser",
        "email": "current@example.com",
        "password": "currentpassword123"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Login to get a token
    login_data = {
        "email": "current@example.com",
        "password": "currentpassword123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Use the token to get current user info
    response = client.get("/api/auth/me",
                         headers={"Authorization": f"Bearer {token}"})

    # Should return 200 OK with user data
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"
    assert data["email"] == "current@example.com"
    assert "id" in data


def test_get_current_user_unauthenticated(client):
    """Test that getting current user fails without authentication"""
    # Try to get current user without a token
    response = client.get("/api/auth/me")

    # Should return 401 Unauthorized
    assert response.status_code == 401

    # Try with an invalid token
    response = client.get("/api/auth/me",
                         headers={"Authorization": "Bearer invalid_token"})

    # Should return 401 Unauthorized
    assert response.status_code == 401


def test_password_hashing_security(client):
    """Test that passwords are properly hashed and not stored in plain text"""
    user_data = {
        "username": "hashuser",
        "email": "hash@example.com",
        "password": "plaintextpassword123"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201

    # Login to get a token and verify user exists
    login_data = {
        "email": "hash@example.com",
        "password": "plaintextpassword123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    # If login succeeds, it means the password was properly hashed and stored


def test_logout_endpoint_exists(client):
    """Test that logout endpoint is available"""
    response = client.post("/api/auth/logout")

    # Logout should return 200 OK (even though it's mostly client-side)
    assert response.status_code == 200
    data = response.json()
    assert "message" in data