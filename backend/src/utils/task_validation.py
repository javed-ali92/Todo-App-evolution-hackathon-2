from typing import Optional
from sqlmodel import Session, select
from ..models.task import Task
from ..models.user import User


def validate_task_ownership(session: Session, task_id: int, user_id: int) -> bool:
    """
    Validate that a specific user owns a specific task.

    Args:
        session: Database session
        task_id: ID of the task to validate ownership for
        user_id: ID of the user to validate ownership against

    Returns:
        bool: True if the user owns the task, False otherwise
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()
    return task is not None


def validate_user_exists(session: Session, user_id: int) -> bool:
    """
    Validate that a user exists in the database.

    Args:
        session: Database session
        user_id: ID of the user to validate

    Returns:
        bool: True if the user exists, False otherwise
    """
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user is not None


def validate_task_title_length(title: str) -> bool:
    """
    Validate that a task title meets length requirements.

    Args:
        title: Task title to validate

    Returns:
        bool: True if the title meets requirements, False otherwise
    """
    return 1 <= len(title) <= 200


def validate_task_description_length(description: Optional[str]) -> bool:
    """
    Validate that a task description meets length requirements.

    Args:
        description: Task description to validate (can be None)

    Returns:
        bool: True if the description meets requirements or is None, False otherwise
    """
    if description is None:
        return True

    return len(description) <= 1000


def validate_task_priority(priority: Optional[str]) -> bool:
    """
    Validate that a task priority is one of the allowed values.

    Args:
        priority: Task priority to validate

    Returns:
        bool: True if the priority is valid, False otherwise
    """
    if priority is None:
        return True

    valid_priorities = ["low", "medium", "high"]
    return priority.lower() in valid_priorities


def validate_task_status(status: Optional[str]) -> bool:
    """
    Validate that a task status is one of the allowed values.

    Args:
        status: Task status to validate

    Returns:
        bool: True if the status is valid, False otherwise
    """
    if status is None:
        return True

    valid_statuses = ["todo", "in_progress", "completed"]
    return status.lower() in valid_statuses


def validate_task_category(category: Optional[str]) -> bool:
    """
    Validate that a task category meets length requirements.

    Args:
        category: Task category to validate

    Returns:
        bool: True if the category meets requirements or is None, False otherwise
    """
    if category is None:
        return True

    return 1 <= len(category) <= 50


def is_task_completed(task: Task) -> bool:
    """
    Check if a task is marked as completed.

    Args:
        task: Task object to check

    Returns:
        bool: True if the task is completed, False otherwise
    """
    return task.completed


def can_modify_task(task: Task, requesting_user_id: int) -> bool:
    """
    Determine if a user can modify a specific task.

    Args:
        task: Task object to check
        requesting_user_id: ID of the user attempting to modify the task

    Returns:
        bool: True if the user can modify the task, False otherwise
    """
    return task.user_id == requesting_user_id


def validate_task_for_creation(title: str, description: Optional[str] = None,
                             priority: Optional[str] = None, category: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Validate all fields of a task before creation.

    Args:
        title: Task title
        description: Task description (optional)
        priority: Task priority (optional)
        category: Task category (optional)

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message if not valid)
    """
    if not validate_task_title_length(title):
        return False, "Task title must be between 1 and 200 characters"

    if not validate_task_description_length(description):
        return False, "Task description must not exceed 1000 characters"

    if not validate_task_priority(priority):
        return False, "Task priority must be one of: low, medium, high"

    if not validate_task_category(category):
        return False, "Task category must be between 1 and 50 characters"

    return True, None


def validate_task_for_update(title: Optional[str] = None, description: Optional[str] = None,
                           priority: Optional[str] = None, category: Optional[str] = None) -> tuple[bool, Optional[str]]:
    """
    Validate fields of a task before updating (only validates provided fields).

    Args:
        title: Task title (if being updated)
        description: Task description (if being updated)
        priority: Task priority (if being updated)
        category: Task category (if being updated)

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message if not valid)
    """
    if title is not None and not validate_task_title_length(title):
        return False, "Task title must be between 1 and 200 characters"

    if description is not None and not validate_task_description_length(description):
        return False, "Task description must not exceed 1000 characters"

    if priority is not None and not validate_task_priority(priority):
        return False, "Task priority must be one of: low, medium, high"

    if category is not None and not validate_task_category(category):
        return False, "Task category must be between 1 and 50 characters"

    return True, None