"""
MCP Tool: list_tasks
Lists user's tasks with optional filters.
"""
from typing import Optional, Dict, Any
from sqlmodel import Session, select
from ...database.database import engine
from ...models.task import Task
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def list_tasks(
    user_id: int,
    completed: Optional[bool] = None,
    due_date: Optional[str] = None,
    due_before: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """
    List user's tasks with optional filters.

    Args:
        user_id: ID of the user (injected by MCP server)
        completed: Filter by completion status (True/False/None for all)
        due_date: Filter tasks by specific due date (YYYY-MM-DD)
        due_before: Filter tasks due before this date (YYYY-MM-DD)
        priority: Filter by priority level (Low, Medium, High)
        tags: Filter by tags (returns tasks matching any of these tags)
        limit: Maximum number of tasks to return (default: 50, max: 100)

    Returns:
        Dictionary with success status and list of tasks
    """
    try:
        # Validate limit
        if limit < 1 or limit > 100:
            return {
                "success": False,
                "error": "Limit must be between 1 and 100"
            }

        # Build query
        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            # Apply filters
            if completed is not None:
                statement = statement.where(Task.completed == completed)

            if due_date:
                statement = statement.where(Task.due_date == due_date)

            if due_before:
                statement = statement.where(Task.due_date < due_before)

            if priority:
                if priority not in ["Low", "Medium", "High"]:
                    return {
                        "success": False,
                        "error": f"Invalid priority: {priority}"
                    }
                statement = statement.where(Task.priority == priority)

            # Apply limit
            statement = statement.limit(limit)

            # Execute query
            tasks = session.exec(statement).all()

            # Filter by tags if provided (post-query filtering)
            if tags:
                filtered_tasks = []
                for task in tasks:
                    if task.tags and any(tag in task.tags for tag in tags):
                        filtered_tasks.append(task)
                tasks = filtered_tasks

            # Convert to dictionaries
            task_list = []
            for task in tasks:
                task_dict = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date.isoformat() if isinstance(task.due_date, datetime) else task.due_date,
                    "priority": task.priority,
                    "tags": task.tags,
                    "completed": task.completed
                }
                task_list.append(task_dict)

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list)
            }

    except Exception as e:
        logger.error(f"Error listing tasks: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to list tasks: {str(e)}"
        }


# Tool schema for MCP registration
TOOL_SCHEMA = {
    "name": "list_tasks",
    "description": "List user's tasks with optional filters. Use this when the user wants to see, view, or check their tasks.",
    "parameters": {
        "type": "object",
        "properties": {
            "completed": {
                "type": "boolean",
                "description": "Filter by completion status. True for completed tasks, false for incomplete, omit for all tasks."
            },
            "due_date": {
                "type": "string",
                "format": "date",
                "description": "Filter tasks by specific due date (YYYY-MM-DD)",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            },
            "due_before": {
                "type": "string",
                "format": "date",
                "description": "Filter tasks due before this date (YYYY-MM-DD)",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Filter by priority level"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by tags (returns tasks matching any of these tags)"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of tasks to return",
                "minimum": 1,
                "maximum": 100,
                "default": 50
            }
        }
    }
}
