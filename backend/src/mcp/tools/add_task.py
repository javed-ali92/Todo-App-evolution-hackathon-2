"""
MCP Tool: add_task
Creates a new task for the user.
"""
from typing import Optional, Dict, Any
from sqlmodel import Session
from ...database.database import engine
from ...services.task_service import create_task
from ...models.task import TaskCreate
import logging

logger = logging.getLogger(__name__)


def add_task(
    user_id: int,
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: str = "Medium",
    tags: Optional[list[str]] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: ID of the user (injected by MCP server)
        title: Task title (required)
        description: Optional task description
        due_date: Optional due date in YYYY-MM-DD format
        priority: Task priority (Low, Medium, High)
        tags: Optional list of tags

    Returns:
        Dictionary with success status and task data
    """
    try:
        # Validate required parameters
        if not title or len(title.strip()) == 0:
            return {
                "success": False,
                "error": "Task title cannot be empty"
            }

        # Validate priority
        if priority not in ["Low", "Medium", "High"]:
            return {
                "success": False,
                "error": f"Invalid priority: {priority}. Must be Low, Medium, or High"
            }

        # Create task object
        task_data = TaskCreate(
            title=title.strip(),
            description=description.strip() if description else None,
            due_date=due_date,
            priority=priority,
            tags=tags or []
        )

        # Create task in database
        with Session(engine) as session:
            task = create_task(session, task_data, user_id)

            return {
                "success": True,
                "task_id": task.id,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "due_date": task.due_date,
                    "priority": task.priority,
                    "tags": task.tags,
                    "completed": task.completed
                }
            }

    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to create task: {str(e)}"
        }


# Tool schema for MCP registration
TOOL_SCHEMA = {
    "name": "add_task",
    "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
    "parameters": {
        "type": "object",
        "required": ["title"],
        "properties": {
            "title": {
                "type": "string",
                "description": "Task title or main action to be done",
                "minLength": 1,
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "Optional detailed description or notes about the task",
                "maxLength": 1000
            },
            "due_date": {
                "type": "string",
                "format": "date",
                "description": "Optional due date in YYYY-MM-DD format. Parse natural language dates before calling this tool.",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "Task priority level. Default to Medium if not specified.",
                "default": "Medium"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional tags or categories for the task",
                "maxItems": 10
            }
        }
    }
}
