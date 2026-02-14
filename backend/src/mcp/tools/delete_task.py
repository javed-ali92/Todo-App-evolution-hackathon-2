"""
MCP Tool: delete_task
Deletes a task permanently.
"""
from typing import Dict, Any
from sqlmodel import Session
from ...database.database import engine
from ...services.task_service import delete_task as delete_task_service
import logging

logger = logging.getLogger(__name__)


def delete_task(
    user_id: int,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a task permanently.

    Args:
        user_id: ID of the user (injected by MCP server)
        task_id: ID of the task to delete

    Returns:
        Dictionary with success status and confirmation message
    """
    try:
        with Session(engine) as session:
            # Delete task (service verifies ownership)
            success = delete_task_service(session, task_id, user_id)

            if not success:
                return {
                    "success": False,
                    "error": "Task not found"
                }

            return {
                "success": True,
                "message": "Task deleted successfully"
            }

    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to delete task: {str(e)}"
        }


# Tool schema for MCP registration
TOOL_SCHEMA = {
    "name": "delete_task",
    "description": "Delete a task permanently. Use this when the user wants to delete, remove, or get rid of a task. Always confirm before deleting.",
    "parameters": {
        "type": "object",
        "required": ["task_id"],
        "properties": {
            "task_id": {
                "type": "integer",
                "description": "ID of the task to delete",
                "minimum": 1
            }
        }
    }
}
