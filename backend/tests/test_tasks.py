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
def setup_test_user(client):
    """Setup a test user and return user data with token"""
    # Register a user via the API
    user_data = {
        "username": "testtaskuser",
        "email": "testtask@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    created_user = response.json()

    # Login to get a token
    login_data = {
        "email": "testtask@example.com",
        "password": "password123"
    }

    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    yield {
        "user": created_user,
        "token": f"Bearer {token}",
        "user_id": created_user["id"]
    }


def test_create_task_success(client, setup_test_user):
    """Test successful task creation"""
    user_data = setup_test_user
    task_data = {
        "title": "Test task",
        "description": "This is a test task",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=task_data,
        headers={"Authorization": user_data["token"]}
    )

    # Check that task creation was successful (201 Created)
    assert response.status_code == 201

    # Verify the response contains task data
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["completed"] == task_data["completed"]
    assert data["user_id"] == user_data["user_id"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_tasks_for_user(client, setup_test_user):
    """Test retrieving all tasks for a user"""
    user_data = setup_test_user

    # Create a task first
    task_data = {
        "title": "Get tasks test",
        "description": "Testing get tasks endpoint",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=task_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 201
    created_task = response.json()

    # Get all tasks for the user
    response = client.get(
        f"/api/{user_data['user_id']}/tasks",
        headers={"Authorization": user_data["token"]}
    )

    # Check that retrieval was successful (200 OK)
    assert response.status_code == 200

    # Verify the response contains the created task
    tasks = response.json()
    assert len(tasks) >= 1
    task_found = any(task["id"] == created_task["id"] for task in tasks)
    assert task_found


def test_get_specific_task(client, setup_test_user):
    """Test retrieving a specific task"""
    user_data = setup_test_user

    # Create a task first
    task_data = {
        "title": "Specific task",
        "description": "Testing get specific task",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=task_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 201
    created_task = response.json()

    # Get the specific task
    response = client.get(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}",
        headers={"Authorization": user_data["token"]}
    )

    # Check that retrieval was successful (200 OK)
    assert response.status_code == 200

    # Verify the response contains the correct task
    data = response.json()
    assert data["id"] == created_task["id"]
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]


def test_update_task(client, setup_test_user):
    """Test updating a task"""
    user_data = setup_test_user

    # Create a task first
    task_data = {
        "title": "Original task",
        "description": "Original description",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=task_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 201
    created_task = response.json()

    # Update the task
    update_data = {
        "title": "Updated task title",
        "description": "Updated description"
    }

    response = client.put(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}",
        json=update_data,
        headers={"Authorization": user_data["token"]}
    )

    # Check that update was successful (200 OK)
    assert response.status_code == 200

    # Verify the response contains updated data
    data = response.json()
    assert data["id"] == created_task["id"]
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["completed"] == created_task["completed"]  # Should remain unchanged


def test_delete_task(client, setup_test_user):
    """Test deleting a task"""
    user_data = setup_test_user

    # Create a task first
    task_data = {
        "title": "Task to delete",
        "description": "This task will be deleted",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=task_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 201
    created_task = response.json()

    # Verify task exists before deletion
    response = client.get(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}",
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 200

    # Delete the task
    response = client.delete(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}",
        headers={"Authorization": user_data["token"]}
    )

    # Check that deletion was successful (200 OK)
    assert response.status_code == 200

    # Verify task no longer exists
    response = client.get(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}",
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 404


def test_toggle_task_completion(client, setup_test_user):
    """Test toggling task completion status"""
    user_data = setup_test_user

    # Create a task first
    task_data = {
        "title": "Toggle completion task",
        "description": "Testing toggle completion",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=task_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 201
    created_task = response.json()

    # Verify initial completion status
    assert created_task["completed"] == False

    # Toggle task completion
    response = client.patch(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}/complete",
        headers={"Authorization": user_data["token"]}
    )

    # Check that toggle was successful (200 OK)
    assert response.status_code == 200

    # Verify the response contains updated completion status
    data = response.json()
    assert data["id"] == created_task["id"]
    assert data["completed"] == True  # Should be toggled to True

    # Toggle again to set back to False
    response = client.patch(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}/complete",
        headers={"Authorization": user_data["token"]}
    )

    # Check that toggle was successful (200 OK)
    assert response.status_code == 200

    # Verify the response contains updated completion status
    data = response.json()
    assert data["id"] == created_task["id"]
    assert data["completed"] == False  # Should be toggled back to False


def test_task_validation_required_fields(client, setup_test_user):
    """Test that required fields are validated for task creation"""
    user_data = setup_test_user

    # Try to create a task without required title
    invalid_task_data = {
        "description": "Task without title",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=invalid_task_data,
        headers={"Authorization": user_data["token"]}
    )

    # Should return 422 Unprocessable Entity due to missing required field
    assert response.status_code == 422

    # Try to create a task with empty title
    invalid_task_data_empty_title = {
        "title": "",
        "description": "Task with empty title",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=invalid_task_data_empty_title,
        headers={"Authorization": user_data["token"]}
    )

    # Should return 422 Unprocessable Entity due to validation
    assert response.status_code == 422


def test_task_data_integrity(client, setup_test_user):
    """Test that task data is properly stored and retrieved"""
    user_data = setup_test_user

    # Create a task with specific data
    original_task_data = {
        "title": "Integrity test task with special chars: !@#$%^&*()",
        "description": "This is a test task with various characters: \n\r\t\"'<>{}[]|\\/:;=?",
        "completed": False
    }

    response = client.post(
        f"/api/{user_data['user_id']}/tasks",
        json=original_task_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 201
    created_task = response.json()

    # Retrieve the task
    response = client.get(
        f"/api/{user_data['user_id']}/tasks/{created_task['id']}",
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 200
    retrieved_task = response.json()

    # Verify data integrity
    assert retrieved_task["title"] == original_task_data["title"]
    assert retrieved_task["description"] == original_task_data["description"]
    assert retrieved_task["completed"] == original_task_data["completed"]


def test_task_not_found(client, setup_test_user):
    """Test that proper error is returned when task doesn't exist"""
    user_data = setup_test_user

    # Try to get a non-existent task
    response = client.get(
        f"/api/{user_data['user_id']}/tasks/999999",
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 404

    # Try to update a non-existent task
    update_data = {"title": "Updated title"}
    response = client.put(
        f"/api/{user_data['user_id']}/tasks/999999",
        json=update_data,
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 404

    # Try to delete a non-existent task
    response = client.delete(
        f"/api/{user_data['user_id']}/tasks/999999",
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 404

    # Try to toggle completion of a non-existent task
    response = client.patch(
        f"/api/{user_data['user_id']}/tasks/999999/complete",
        headers={"Authorization": user_data["token"]}
    )
    assert response.status_code == 404