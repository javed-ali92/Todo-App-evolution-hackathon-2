"""
Test suite for User Story 2: User Data Persistence

Validates that:
1. User registration persists to Neon PostgreSQL
2. User login reads from Neon PostgreSQL
3. User data survives application restart
4. Duplicate email/username rejection works via Neon constraints
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.main import app
from src.database.database import engine
from src.models.user import User
from src.services.auth_service import get_password_hash
import time


client = TestClient(app)


class TestUserRegistrationPersistence:
    """Test user registration persists to Neon (Task T037)"""

    def test_user_registration_persists_to_neon(self):
        """Task T037: Test user registration persists to Neon"""
        # Create a unique user
        timestamp = int(time.time())
        test_user = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "SecurePass123!"
        }

        # Register user via API
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 201, f"Registration failed: {response.json()}"

        user_data = response.json()
        assert user_data["username"] == test_user["username"]
        assert user_data["email"] == test_user["email"]
        assert "id" in user_data

        # Verify user exists in Neon database by querying directly
        with Session(engine) as session:
            statement = select(User).where(User.email == test_user["email"])
            db_user = session.exec(statement).first()

            assert db_user is not None, "User not found in Neon database"
            assert db_user.username == test_user["username"]
            assert db_user.email == test_user["email"]
            assert db_user.hashed_password is not None
            assert db_user.hashed_password != test_user["password"]  # Should be hashed

        # Cleanup
        with Session(engine) as session:
            statement = select(User).where(User.email == test_user["email"])
            db_user = session.exec(statement).first()
            if db_user:
                session.delete(db_user)
                session.commit()


class TestUserLoginPersistence:
    """Test user login reads from Neon (Task T038)"""

    def test_user_login_reads_from_neon(self):
        """Task T038: Test user login reads from Neon"""
        # Create a test user directly in Neon database
        timestamp = int(time.time())
        test_email = f"logintest_{timestamp}@example.com"
        test_username = f"loginuser_{timestamp}"
        test_password = "SecurePass123!"

        with Session(engine) as session:
            hashed_password = get_password_hash(test_password)
            db_user = User(
                username=test_username,
                email=test_email,
                hashed_password=hashed_password
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            user_id = db_user.id

        # Login via API
        login_data = {
            "email": test_email,
            "password": test_password
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, f"Login failed: {response.json()}"

        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["user_id"] == str(user_id)

        # Cleanup
        with Session(engine) as session:
            db_user = session.get(User, user_id)
            if db_user:
                session.delete(db_user)
                session.commit()


class TestUserDataSurvivesRestart:
    """Test user data survives application restart (Task T039)"""

    def test_user_data_survives_application_restart(self):
        """Task T039: Test user data survives application restart"""
        # Create a test user
        timestamp = int(time.time())
        test_user = {
            "username": f"persistuser_{timestamp}",
            "email": f"persist_{timestamp}@example.com",
            "password": "SecurePass123!"
        }

        # Register user
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Simulate application restart by creating a new database session
        # (In real scenario, this would be a full app restart)
        with Session(engine) as new_session:
            # Query user from fresh session (simulates restart)
            statement = select(User).where(User.id == user_id)
            db_user = new_session.exec(statement).first()

            assert db_user is not None, "User data did not survive restart"
            assert db_user.username == test_user["username"]
            assert db_user.email == test_user["email"]

        # Verify login still works after "restart"
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        response = client.post("/api/auth/login", json=login_data)
        assert response.status_code == 200, "Login failed after restart"

        # Cleanup
        with Session(engine) as session:
            db_user = session.get(User, user_id)
            if db_user:
                session.delete(db_user)
                session.commit()


class TestDuplicateEmailRejection:
    """Test duplicate email rejection from Neon (Task T040)"""

    def test_duplicate_email_rejection_from_neon(self):
        """Task T040: Test duplicate email rejection from Neon"""
        # Create first user
        timestamp = int(time.time())
        test_email = f"duplicate_{timestamp}@example.com"

        user1 = {
            "username": f"user1_{timestamp}",
            "email": test_email,
            "password": "SecurePass123!"
        }

        response = client.post("/api/auth/register", json=user1)
        assert response.status_code == 201
        user1_id = response.json()["id"]

        # Try to create second user with same email
        user2 = {
            "username": f"user2_{timestamp}",
            "email": test_email,  # Same email
            "password": "DifferentPass456!"
        }

        response = client.post("/api/auth/register", json=user2)
        assert response.status_code == 409, "Should reject duplicate email"
        assert "email" in response.json()["detail"].lower()

        # Verify only one user exists in Neon
        with Session(engine) as session:
            statement = select(User).where(User.email == test_email)
            users = session.exec(statement).all()
            assert len(users) == 1, "Should only have one user with this email"

        # Cleanup
        with Session(engine) as session:
            db_user = session.get(User, user1_id)
            if db_user:
                session.delete(db_user)
                session.commit()


class TestDuplicateUsernameRejection:
    """Test duplicate username rejection from Neon (Task T041)"""

    def test_duplicate_username_rejection_from_neon(self):
        """Task T041: Test duplicate username rejection from Neon"""
        # Create first user
        timestamp = int(time.time())
        test_username = f"uniqueuser_{timestamp}"

        user1 = {
            "username": test_username,
            "email": f"user1_{timestamp}@example.com",
            "password": "SecurePass123!"
        }

        response = client.post("/api/auth/register", json=user1)
        assert response.status_code == 201
        user1_id = response.json()["id"]

        # Try to create second user with same username
        user2 = {
            "username": test_username,  # Same username
            "email": f"user2_{timestamp}@example.com",
            "password": "DifferentPass456!"
        }

        response = client.post("/api/auth/register", json=user2)
        assert response.status_code == 409, "Should reject duplicate username"
        assert "username" in response.json()["detail"].lower()

        # Verify only one user exists in Neon with this username
        with Session(engine) as session:
            statement = select(User).where(User.username == test_username)
            users = session.exec(statement).all()
            assert len(users) == 1, "Should only have one user with this username"

        # Cleanup
        with Session(engine) as session:
            db_user = session.get(User, user1_id)
            if db_user:
                session.delete(db_user)
                session.commit()


class TestDirectNeonQuery:
    """Query Neon directly to verify user record exists (Task T042)"""

    def test_query_neon_directly_to_verify_user_record(self):
        """Task T042: Query Neon directly to verify user record exists"""
        # Create a test user
        timestamp = int(time.time())
        test_user = {
            "username": f"directquery_{timestamp}",
            "email": f"directquery_{timestamp}@example.com",
            "password": "SecurePass123!"
        }

        # Register user via API
        response = client.post("/api/auth/register", json=test_user)
        assert response.status_code == 201
        user_id = response.json()["id"]

        # Query Neon directly using raw SQL to verify persistence
        with Session(engine) as session:
            from sqlalchemy import text

            # Direct SQL query to Neon
            result = session.exec(
                text("SELECT id, username, email, hashed_password FROM \"user\" WHERE id = :user_id"),
                {"user_id": user_id}
            ).first()

            assert result is not None, "User not found in Neon via direct SQL query"
            assert result[0] == user_id
            assert result[1] == test_user["username"]
            assert result[2] == test_user["email"]
            assert result[3] is not None  # hashed_password exists
            assert len(result[3]) > 0  # hashed_password is not empty

        # Cleanup
        with Session(engine) as session:
            db_user = session.get(User, user_id)
            if db_user:
                session.delete(db_user)
                session.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
