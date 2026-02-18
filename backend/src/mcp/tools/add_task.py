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
import json

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
    session = None
    try:
        # PATCH 1: Enhanced logging for debugging
        logger.info(f"[ADD_TASK] Creating task for user_id={user_id}, title='{title[:50]}', priority={priority}")

        # Validate required parameters
        if not title or len(title.strip()) == 0:
            logger.warning(f"[ADD_TASK] Empty title provided for user {user_id}")
            return {
                "success": False,
                "error": "Task title cannot be empty"
            }

        # Validate priority
        if priority not in ["Low", "Medium", "High"]:
            logger.warning(f"[ADD_TASK] Invalid priority '{priority}' for user {user_id}")
            return {
                "success": False,
                "error": f"Invalid priority: {priority}. Must be Low, Medium, or High"
            }

        # PATCH 3: Safe JSON conversion with error handling
        try:
            tags_str = json.dumps(tags) if isinstance(tags, list) else tags
        except Exception as json_error:
            logger.error(f"[ADD_TASK] JSON serialization error for tags: {json_error}")
            tags_str = None

        # Create task object
        task_data = TaskCreate(
            title=title.strip(),
            description=description.strip() if description else None,
            due_date=due_date,
            priority=priority,
            tags=tags_str
        )

        # PATCH 4: Database connection with proper error handling and reuse
        logger.debug(f"[ADD_TASK] Opening database session for user {user_id}")
        session = Session(engine)

        try:
            # PATCH 4: Safe DB insert with detailed error logging
            logger.debug(f"[ADD_TASK] Calling create_task service for user {user_id}")
            task = create_task(session, task_data, user_id)

            # Ensure task was created successfully
            if not task or not task.id:
                logger.error(f"[ADD_TASK] Task creation returned None or invalid task for user {user_id}")
                return {
                    "success": False,
                    "error": "Task creation failed - no task returned from database"
                }

            logger.info(f"[ADD_TASK] Successfully created task_id={task.id} for user {user_id}")

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

        except Exception as db_error:
            # PATCH 1: Enhanced DB error logging with type and details
            logger.error(f"[ADD_TASK] Database error type: {type(db_error).__name__}")
            logger.error(f"[ADD_TASK] Database error for user {user_id}: {str(db_error)}")
            logger.exception(f"[ADD_TASK] Full database error traceback:")

            # Rollback the session on error
            if session:
                try:
                    session.rollback()
                    logger.debug(f"[ADD_TASK] Session rolled back for user {user_id}")
                except Exception as rollback_error:
                    logger.error(f"[ADD_TASK] Rollback error: {rollback_error}")

            return {
                "success": False,
                "error": f"Database error: {type(db_error).__name__} - {str(db_error)[:200]}"
            }
        finally:
            # PATCH 4: Always close session to prevent connection leaks
            if session:
                try:
                    session.close()
                    logger.debug(f"[ADD_TASK] Database session closed for user {user_id}")
                except Exception as close_error:
                    logger.warning(f"[ADD_TASK] Error closing session: {close_error}")

    except Exception as e:
        # PATCH 1: Enhanced top-level error logging
        logger.error(f"[ADD_TASK] Unexpected error type: {type(e).__name__}")
        logger.error(f"[ADD_TASK] Unexpected error for user {user_id}: {str(e)}")
        logger.exception(f"[ADD_TASK] Full error traceback:")

        return {
            "success": False,
            "error": f"Failed to create task: {type(e).__name__} - {str(e)[:200]}"
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
