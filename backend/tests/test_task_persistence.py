"""
Test suite for User Story 3: Task Data Persistence

Validates that:
1. Task creation persists to Neon PostgreSQL
2. Task retrieval reads from Neon PostgreSQL
3. Task update persists to Neon PostgreSQL
4. Task deletion removes from Neon PostgreSQL
5. Task completion toggle persists to Neon PostgreSQL
6. Task data survives application restart
7. Foreign key constraint is enforced
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from src.main import app
from src.database.database import engine
from src.models.user import User
from src.models.task import Task
from src.services.auth_service import get_password_hash
import time


client = TestClient(app)


@pytest.fixture
def test_user_with_token():
    """Create a test user and return user_id and auth token"""
    timestamp = int(time.time())
    test_user = {
        "username": f"taskuser_{timestamp}",
        "email": f"taskuser_{timestamp}@example.com",
        "password": "SecurePass123!"
    }

    # Register user
    response = client.post("/api/auth/register", json=test_user)
    assert response.status_code == 201
    user_data = response.json()
    user_id = user_data["id"]

    # Login to get token
    login_response = client.post("/api/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    yield user_id, token, test_user["email"]

    # Cleanup
    with Session(engine) as session:
        db_user = session.get(User, user_id)
        if db_user:
            # Delete all tasks first (foreign key constraint)
            statement = select(Task).where(Task.user_id == user_id)
            tasks = session.exec(statement).all()
            for task in tasks:
                session.delete(task)
            session.delete(db_user)
            session.commit()


class TestTaskCreationPersistence:
    """Test task creation persists to Neon (Task T050)"""

    def test_task_creation_persists_to_neon(self, test_user_with_token):
        """Task T050: Test task creation persists to Neon"""
        user_id, token, _ = test_user_with_token

        # Create a task via API
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "High",
            "completed": False
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers=headers
        )
        assert response.status_code == 201, f"Task creation failed: {response.json()}"

        task_response = response.json()
        task_id = task_response["id"]
        assert task_response["title"] == task_data["title"]
        assert task_response["user_id"] == user_id

        # Verify task exists in Neon database by querying directly
        with Session(engine) as session:
            statement = select(Task).where(Task.id == task_id)
            db_task = session.exec(statement).first()

            assert db_task is not None, "Task not found in Neon database"
            assert db_task.title == task_data["title"]
            assert db_task.description == task_data["description"]
            assert db_task.priority == task_data["priority"]
            assert db_task.user_id == user_id


class TestTaskRetrievalPersistence:
    """Test task retrieval reads from Neon (Task T051)"""

    def test_task_retrieval_reads_from_neon(self, test_user_with_token):
        """Task T051: Test task retrieval reads from Neon"""
        user_id, token, _ = test_user_with_token

        # Create a task directly in Neon database
        with Session(engine) as session:
            db_task = Task(
                title="Direct DB Task",
                description="Created directly in database",
                priority="Medium",
                user_id=user_id,
                completed=False
            )
            session.add(db_task)
            session.commit()
            session.refresh(db_task)
            task_id = db_task.id

        # Retrieve task via API
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Task retrieval failed: {response.json()}"

        task_data = response.json()
        assert task_data["id"] == task_id
        assert task_data["title"] == "Direct DB Task"
        assert task_data["description"] == "Created directly in database"


class TestTaskUpdatePersistence:
    """Test task update persists to Neon (Task T052)"""

    def test_task_update_persists_to_neon(self, test_user_with_token):
        """Task T052: Test task update persists to Neon"""
        user_id, token, _ = test_user_with_token

        # Create a task
        task_data = {
            "title": "Original Title",
            "description": "Original Description",
            "priority": "Low",
            "completed": False
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers=headers
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Update the task
        update_data = {
            "title": "Updated Title",
            "description": "Updated Description",
            "priority": "High"
        }

        response = client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers=headers
        )
        assert response.status_code == 200, f"Task update failed: {response.json()}"

        # Verify update persisted to Neon
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task is not None
            assert db_task.title == "Updated Title"
            assert db_task.description == "Updated Description"
            assert db_task.priority == "High"


class TestTaskDeletionPersistence:
    """Test task deletion removes from Neon (Task T053)"""

    def test_task_deletion_removes_from_neon(self, test_user_with_token):
        """Task T053: Test task deletion removes from Neon"""
        user_id, token, _ = test_user_with_token

        # Create a task
        task_data = {
            "title": "Task to Delete",
            "description": "This task will be deleted",
            "priority": "Medium",
            "completed": False
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers=headers
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Delete the task
        response = client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Task deletion failed: {response.json()}"

        # Verify task is removed from Neon
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task is None, "Task should be deleted from Neon database"


class TestTaskCompletionTogglePersistence:
    """Test task completion toggle persists to Neon (Task T054)"""

    def test_task_completion_toggle_persists_to_neon(self, test_user_with_token):
        """Task T054: Test task completion toggle persists to Neon"""
        user_id, token, _ = test_user_with_token

        # Create a task
        task_data = {
            "title": "Task to Complete",
            "description": "This task will be toggled",
            "priority": "High",
            "completed": False
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers=headers
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Toggle completion to True
        response = client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers=headers
        )
        assert response.status_code == 200, f"Task toggle failed: {response.json()}"
        assert response.json()["completed"] is True

        # Verify toggle persisted to Neon
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task is not None
            assert db_task.completed is True

        # Toggle back to False
        response = client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers=headers
        )
        assert response.status_code == 200
        assert response.json()["completed"] is False

        # Verify second toggle persisted to Neon
        with Session(engine) as session:
            db_task = session.get(Task, task_id)
            assert db_task is not None
            assert db_task.completed is False


class TestTaskDataSurvivesRestart:
    """Test task data survives application restart (Task T055)"""

    def test_task_data_survives_application_restart(self, test_user_with_token):
        """Task T055: Test task data survives application restart"""
        user_id, token, _ = test_user_with_token

        # Create a task
        task_data = {
            "title": "Persistent Task",
            "description": "This task should survive restart",
            "priority": "High",
            "completed": False
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers=headers
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Simulate application restart by creating a new database session
        with Session(engine) as new_session:
            # Query task from fresh session (simulates restart)
            statement = select(Task).where(Task.id == task_id)
            db_task = new_session.exec(statement).first()

            assert db_task is not None, "Task data did not survive restart"
            assert db_task.title == task_data["title"]
            assert db_task.description == task_data["description"]
            assert db_task.user_id == user_id

        # Verify task is still accessible via API after "restart"
        response = client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 200, "Task not accessible after restart"


class TestDirectNeonQuery:
    """Query Neon directly to verify task record exists (Task T056)"""

    def test_query_neon_directly_to_verify_task_record(self, test_user_with_token):
        """Task T056: Query Neon directly to verify task record exists"""
        user_id, token, _ = test_user_with_token

        # Create a task
        task_data = {
            "title": "Direct Query Task",
            "description": "Verify with direct SQL",
            "priority": "Medium",
            "completed": False
        }

        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers=headers
        )
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Query Neon directly using raw SQL
        with Session(engine) as session:
            from sqlalchemy import text

            result = session.exec(
                text("SELECT id, title, description, user_id, priority, completed FROM task WHERE id = :task_id"),
                {"task_id": task_id}
            ).first()

            assert result is not None, "Task not found in Neon via direct SQL query"
            assert result[0] == task_id
            assert result[1] == task_data["title"]
            assert result[2] == task_data["description"]
            assert result[3] == user_id
            assert result[4] == task_data["priority"]
            assert result[5] == task_data["completed"]


class TestForeignKeyConstraint:
    """Test task foreign key constraint is enforced (Task T057)"""

    def test_task_foreign_key_constraint_is_enforced(self):
        """Task T057: Test task foreign key constraint is enforced"""
        # Try to create a task with non-existent user_id
        with Session(engine) as session:
            from sqlalchemy.exc import IntegrityError

            # Use a user_id that doesn't exist
            invalid_user_id = 999999

            db_task = Task(
                title="Invalid Task",
                description="This should fail",
                priority="Low",
                user_id=invalid_user_id,
                completed=False
            )

            session.add(db_task)

            # Should raise IntegrityError due to foreign key constraint
            with pytest.raises(IntegrityError) as exc_info:
                session.commit()

            assert "foreign key constraint" in str(exc_info.value).lower() or \
                   "violates foreign key" in str(exc_info.value).lower() or \
                   "fk_task_user_id_user" in str(exc_info.value).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
