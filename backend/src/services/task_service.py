from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from ..models.task import Task, TaskCreate, TaskUpdate, TaskToggleComplete
from ..models.user import User

def create_task(session: Session, task: TaskCreate, user_id: int) -> Task:
    """
    Create a new task for a user
    """
    task_data = task.model_dump()
    db_task = Task(**task_data)
    db_task.user_id = user_id
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Convert datetime due_date to string for compatibility
    if db_task.due_date and hasattr(db_task.due_date, 'isoformat'):
        db_task.due_date = db_task.due_date.isoformat()

    return db_task

def get_tasks_by_user(session: Session, user_id: int) -> List[dict]:
    """
    Get all tasks for a specific user
    """
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()

    # Convert to dictionaries with datetime fields converted to strings
    result = []
    for task in tasks:
        task_dict = {
            'id': task.id,
            'user_id': task.user_id,
            'title': task.title,
            'description': task.description,
            'due_date': task.due_date.isoformat() if task.due_date and isinstance(task.due_date, datetime) else task.due_date,
            'priority': task.priority,
            'tags': task.tags,
            'recursion_pattern': task.recursion_pattern,
            'completed': task.completed,
            'created_at': task.created_at,
            'updated_at': task.updated_at
        }
        result.append(task_dict)

    return result

def get_task_by_id(session: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Get a specific task by ID for a specific user
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = session.exec(statement).first()

    # Convert datetime due_date to string for compatibility
    if task and task.due_date and hasattr(task.due_date, 'isoformat'):
        task.due_date = task.due_date.isoformat()

    return task

def update_task(session: Session, task_id: int, task_update: TaskUpdate, user_id: int) -> Optional[Task]:
    """
    Update a specific task for a user
    """
    db_task = get_task_by_id(session, task_id, user_id)
    if not db_task:
        return None

    # Update the task with provided values
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_task, field):
            setattr(db_task, field, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Convert datetime due_date to string for compatibility
    if db_task.due_date and hasattr(db_task.due_date, 'isoformat'):
        db_task.due_date = db_task.due_date.isoformat()

    return db_task

def delete_task(session: Session, task_id: int, user_id: int) -> bool:
    """
    Delete a specific task for a user
    """
    db_task = get_task_by_id(session, task_id, user_id)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()
    return True

def toggle_task_completion(session: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Toggle the completion status of a task for a user
    """
    db_task = get_task_by_id(session, task_id, user_id)
    if not db_task:
        return None

    db_task.completed = not db_task.completed
    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Convert datetime due_date to string for compatibility
    if db_task.due_date and hasattr(db_task.due_date, 'isoformat'):
        db_task.due_date = db_task.due_date.isoformat()

    return db_task