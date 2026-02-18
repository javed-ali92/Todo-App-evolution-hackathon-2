"""
MCP Tool: update_task
Updates task details like title, description, due date, or priority.
"""
from typing import Optional, Dict, Any
from sqlmodel import Session
from ...database.database import engine
from ...services.task_service import get_task_by_id, update_task as update_task_service
from ...models.task import TaskUpdate
import logging

logger = logging.getLogger(__name__)


def update_task(
    user_id: int,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    priority: Optional[str] = None,
    tags: Optional[list[str]] = None
) -> Dict[str, Any]:
    """
    Update task details.

    Args:
        user_id: ID of the user (injected by MCP server)
        task_id: ID of the task to update
        title: New task title
        description: New task description
        due_date: New due date in YYYY-MM-DD format
        priority: New priority level (Low, Medium, High)
        tags: New tags (replaces existing tags)

    Returns:
        Dictionary with success status and updated task data
    """
    try:
        # Validate that at least one field is provided
        if all(v is None for v in [title, description, due_date, priority, tags]):
            return {
                "success": False,
                "error": "At least one field must be provided to update"
            }

        # Validate priority if provided
        if priority and priority not in ["Low", "Medium", "High"]:
            return {
                "success": False,
                "error": f"Invalid priority: {priority}. Must be Low, Medium, or High"
            }

        with Session(engine) as session:
            # Verify task exists and user owns it
            task = get_task_by_id(session, task_id, user_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found"
                }

            # Build update data
            update_data = {}
            if title is not None:
                update_data["title"] = title.strip()
            if description is not None:
                update_data["description"] = description.strip() if description else None
            if due_date is not None:
                update_data["due_date"] = due_date
            if priority is not None:
                update_data["priority"] = priority
            if tags is not None:
                update_data["tags"] = tags

            # Update task
            task_update = TaskUpdate(**update_data)
            updated_task = update_task_service(session, task_id, task_update, user_id)

            if not updated_task:
                return {
                    "success": False,
                    "error": "Failed to update task"
                }

            return {
                "success": True,
                "task": {
                    "id": updated_task.id,
                    "title": updated_task.title,
                    "description": updated_task.description,
                    "due_date": updated_task.due_date,
                    "priority": updated_task.priority,
                    "tags": updated_task.tags,
                    "completed": updated_task.completed
                }
            }

    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to update task: {str(e)}"
        }


# Tool schema for MCP registration
TOOL_SCHEMA = {
    "name": "update_task",
    "description": "Update task details like title, description, due date, or priority. Use this when the user wants to change, modify, or update a task.",
    "parameters": {
        "type": "object",
        "required": ["task_id"],
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "ID of the task to update",
                "minimum": 1
            },
            "title": {
                "type": "string",
                "description": "New task title",
                "minLength": 1,
                "maxLength": 200
            },
            "description": {
                "type": "string",
                "description": "New task description",
                "maxLength": 1000
            },
            "due_date": {
                "type": "string",
                "format": "date",
                "description": "New due date in YYYY-MM-DD format",
                "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
            },
            "priority": {
                "type": "string",
                "enum": ["Low", "Medium", "High"],
                "description": "New priority level"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "New tags (replaces existing tags)"
            }
        },
        "minProperties": 2
    }
}
