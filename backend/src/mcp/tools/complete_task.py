"""
MCP Tool: complete_task
Marks a task as complete or incomplete.
"""
from typing import Dict, Any
from sqlmodel import Session
from ...database.database import engine
from ...services.task_service import get_task_by_id
import logging

logger = logging.getLogger(__name__)


def complete_task(
    user_id: int,
    task_id: int,
    completed: bool = True
) -> Dict[str, Any]:
    """
    Mark a task as complete or incomplete.

    Args:
        user_id: ID of the user (injected by MCP server)
        task_id: ID of the task to mark as complete/incomplete
        completed: Completion status (True to mark complete, False to mark incomplete)

    Returns:
        Dictionary with success status and updated task data
    """
    try:
        with Session(engine) as session:
            # Get task and verify ownership
            task = get_task_by_id(session, task_id, user_id)

            if not task:
                return {
                    "success": False,
                    "error": "Task not found"
                }

            # Update completion status
            task.completed = completed
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed
                }
            }

    except Exception as e:
        logger.error(f"Error completing task: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to complete task: {str(e)}"
        }


# Tool schema for MCP registration
TOOL_SCHEMA = {
    "name": "complete_task",
    "description": "Mark a task as complete or incomplete. Use this when the user wants to mark, complete, finish, or check off a task.",
    "parameters": {
        "type": "object",
        "required": ["task_id"],
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "ID of the task to mark as complete/incomplete",
                "minimum": 1
            },
            "completed": {
                "type": "boolean",
                "description": "Completion status. True to mark complete, false to mark incomplete. Default is true.",
                "default": True
            }
        }
    }
}
