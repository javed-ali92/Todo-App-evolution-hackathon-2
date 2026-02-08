from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from ..database.database import engine
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate
from ..models.user import User
from ..services.task_service import (
    create_task, get_tasks_by_user, get_task_by_id,
    update_task, delete_task, toggle_task_completion
)
from ..auth.jwt_handler import get_current_user
from ..auth.middleware import authorize_user_access
from ..utils.logging import ValidationError, create_error_response


def get_session():
    with Session(engine) as session:
        yield session



router = APIRouter()


@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_new_task(
    user_id: int,
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Create a new task for the specified user

    Args:
        user_id: ID of the user to create task for
        task: Task creation data
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        TaskRead: Created task object

    Raises:
        HTTPException: If user is not authorized to create task for the specified user
    """
    # Verify that the user_id in the token matches the URL user_id
    token_user_id = int(current_user.get("user_id"))
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )

    task_result = create_task(session, task, user_id)
    return task_result


@router.get("/{user_id}/tasks", response_model=List[TaskRead])
def read_tasks(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[TaskRead]:
    """
    Get all tasks for the specified user

    Args:
        user_id: ID of the user whose tasks to retrieve
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        List[TaskRead]: List of tasks for the user

    Raises:
        HTTPException: If user is not authorized to access the specified user's tasks
    """
    # Verify that the user_id in the token matches the URL user_id
    token_user_id = int(current_user.get("user_id"))
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    return get_tasks_by_user(session, user_id)


@router.get("/{user_id}/tasks/{id}", response_model=TaskRead)
def read_task(
    user_id: int,
    id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Get a specific task for the specified user

    Args:
        user_id: ID of the user who owns the task
        id: ID of the task to retrieve
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        TaskRead: The requested task object

    Raises:
        HTTPException: If user is not authorized to access the task or task not found
    """
    # Verify that the user_id in the token matches the URL user_id
    token_user_id = int(current_user.get("user_id"))
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    task = get_task_by_id(session, id, user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.put("/{user_id}/tasks/{id}", response_model=TaskRead)
def update_existing_task(
    user_id: int,
    id: int,
    task_update: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Update a specific task for the specified user

    Args:
        user_id: ID of the user who owns the task
        id: ID of the task to update
        task_update: Task update data
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        TaskRead: Updated task object

    Raises:
        HTTPException: If user is not authorized to update the task or task not found
    """
    # Verify that the user_id in the token matches the URL user_id
    token_user_id = int(current_user.get("user_id"))
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    updated_task = update_task(session, id, task_update, user_id)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return updated_task


@router.delete("/{user_id}/tasks/{id}")
def delete_existing_task(
    user_id: int,
    id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> dict:
    """
    Delete a specific task for the specified user

    Args:
        user_id: ID of the user who owns the task
        id: ID of the task to delete
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        dict: Success message

    Raises:
        HTTPException: If user is not authorized to delete the task or task not found
    """
    # Verify that the user_id in the token matches the URL user_id
    token_user_id = int(current_user.get("user_id"))
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    success = delete_task(session, id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}


@router.patch("/{user_id}/tasks/{id}/complete", response_model=TaskRead)
def toggle_task_complete(
    user_id: int,
    id: int,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> TaskRead:
    """
    Toggle the completion status of a specific task for the specified user

    Args:
        user_id: ID of the user who owns the task
        id: ID of the task to toggle
        current_user: Currently authenticated user (from JWT token)
        session: Database session dependency

    Returns:
        TaskRead: Task object with updated completion status

    Raises:
        HTTPException: If user is not authorized to toggle the task or task not found
    """
    # Verify that the user_id in the token matches the URL user_id
    token_user_id = int(current_user.get("user_id"))
    if token_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's tasks"
        )

    toggled_task = toggle_task_completion(session, id, user_id)
    if not toggled_task:
        raise HTTPException(status_code=404, detail="Task not found")

    return toggled_task