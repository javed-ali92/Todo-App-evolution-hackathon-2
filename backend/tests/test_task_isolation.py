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
from src.services.auth_service import create_user, get_password_hash
from src.auth.jwt_handler import create_user_token


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


@pytest.fixture(scope="function")
def setup_test_data(client):
    """Setup test users and tasks"""
    # Create first user
    user1_data = {
        "username": "testuser1",
        "email": "test1@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/register", json=user1_data)
    assert response.status_code == 201
    user1 = response.json()

    # Create second user
    user2_data = {
        "username": "testuser2",
        "email": "test2@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/register", json=user2_data)
    assert response.status_code == 201
    user2 = response.json()

    # Login as both users to get tokens
    login1_data = {"email": "test1@example.com", "password": "password123"}
    response = client.post("/api/auth/login", json=login1_data)
    assert response.status_code == 200
    token1 = f"Bearer {response.json()['access_token']}"

    login2_data = {"email": "test2@example.com", "password": "password123"}
    response = client.post("/api/auth/login", json=login2_data)
    assert response.status_code == 200
    token2 = f"Bearer {response.json()['access_token']}"

    yield {
        "user1": user1,
        "user2": user2,
        "token1": token1,
        "token2": token2
    }


def test_user_cannot_access_other_users_tasks(client, setup_test_data):
    """Test that users can only access their own tasks"""
    data = setup_test_data

    # User 1 creates a task
    task_data = {
        "title": "User 1 task",
        "description": "This is user 1's task"
    }

    response = client.post(
        f"/api/{data['user1']['id']}/tasks",
        json=task_data,
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 201
    task1 = response.json()

    # User 2 tries to access user 1's task - should fail
    response = client.get(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token2']}  # Different user's token
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to update user 1's task - should fail
    update_data = {"title": "Modified by user 2"}
    response = client.put(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        json=update_data,
        headers={"Authorization": data['token2']}
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to delete user 1's task - should fail
    response = client.delete(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token2']}
    )
    assert response.status_code == 403  # Forbidden

    # User 2 tries to toggle user 1's task - should fail
    response = client.patch(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}/complete",
        headers={"Authorization": data['token2']}
    )
    assert response.status_code == 403  # Forbidden

    # Clean up: delete user 1's task using correct user
    response = client.delete(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200


def test_user_can_access_own_tasks(client, setup_test_data):
    """Test that users can access their own tasks"""
    data = setup_test_data

    # User 1 creates a task
    task_data = {
        "title": "User 1 task",
        "description": "This is user 1's task"
    }

    response = client.post(
        f"/api/{data['user1']['id']}/tasks",
        json=task_data,
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 201
    task1 = response.json()

    # User 1 can access their own task
    response = client.get(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200
    assert response.json()["id"] == task1["id"]

    # User 1 can update their own task
    update_data = {"title": "Updated user 1 task"}
    response = client.put(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        json=update_data,
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated user 1 task"

    # User 1 can toggle their own task
    response = client.patch(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}/complete",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200
    assert response.json()["completed"] != task1["completed"]  # Should be flipped

    # User 1 can delete their own task
    response = client.delete(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200

    # Verify task is deleted
    response = client.get(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 404


def test_user_separate_task_lists(client, setup_test_data):
    """Test that users have separate task lists"""
    data = setup_test_data

    # User 1 creates a task
    task1_data = {
        "title": "User 1 task",
        "description": "This belongs to user 1"
    }

    response = client.post(
        f"/api/{data['user1']['id']}/tasks",
        json=task1_data,
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 201
    task1 = response.json()

    # User 2 creates a task
    task2_data = {
        "title": "User 2 task",
        "description": "This belongs to user 2"
    }

    response = client.post(
        f"/api/{data['user2']['id']}/tasks",
        json=task2_data,
        headers={"Authorization": data['token2']}
    )
    assert response.status_code == 201
    task2 = response.json()

    # User 1 should only see their own task
    response = client.get(
        f"/api/{data['user1']['id']}/tasks",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200
    user1_tasks = response.json()
    assert len(user1_tasks) == 1
    assert user1_tasks[0]["id"] == task1["id"]
    assert user1_tasks[0]["title"] == "User 1 task"

    # User 2 should only see their own task
    response = client.get(
        f"/api/{data['user2']['id']}/tasks",
        headers={"Authorization": data['token2']}
    )
    assert response.status_code == 200
    user2_tasks = response.json()
    assert len(user2_tasks) == 1
    assert user2_tasks[0]["id"] == task2["id"]
    assert user2_tasks[0]["title"] == "User 2 task"

    # User 1 should not see user 2's task in their list
    user1_task_ids = [t["id"] for t in user1_tasks]
    assert task2["id"] not in user1_task_ids

    # User 2 should not see user 1's task in their list
    user2_task_ids = [t["id"] for t in user2_tasks]
    assert task1["id"] not in user2_task_ids

    # Clean up: delete both tasks
    response = client.delete(
        f"/api/{data['user1']['id']}/tasks/{task1['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200

    response = client.delete(
        f"/api/{data['user2']['id']}/tasks/{task2['id']}",
        headers={"Authorization": data['token2']}
    )
    assert response.status_code == 200


def test_cross_user_modification_attempts(client, setup_test_data):
    """Test various attempts to modify another user's data"""
    data = setup_test_data

    # User 1 creates a task
    task_data = {
        "title": "Original task",
        "description": "Description for original task"
    }

    response = client.post(
        f"/api/{data['user1']['id']}/tasks",
        json=task_data,
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 201
    original_task = response.json()

    # Attempt to update with wrong user ID in URL but correct token - should fail
    update_data = {"title": "Hacked task"}
    response = client.put(
        f"/api/{data['user2']['id']}/tasks/{original_task['id']}",  # Wrong user ID
        json=update_data,
        headers={"Authorization": data['token1']}  # Correct token for user1
    )
    assert response.status_code == 403  # Forbidden - user ID mismatch

    # Attempt to update with correct user ID in URL but wrong token - should fail
    response = client.put(
        f"/api/{data['user1']['id']}/tasks/{original_task['id']}",  # Correct user ID
        json=update_data,
        headers={"Authorization": data['token2']}  # Wrong token for user2
    )
    assert response.status_code == 403  # Forbidden - wrong token

    # Verify original task remains unchanged
    response = client.get(
        f"/api/{data['user1']['id']}/tasks/{original_task['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200
    retrieved_task = response.json()
    assert retrieved_task["title"] == "Original task"  # Should not be changed

    # Clean up: delete the task
    response = client.delete(
        f"/api/{data['user1']['id']}/tasks/{original_task['id']}",
        headers={"Authorization": data['token1']}
    )
    assert response.status_code == 200