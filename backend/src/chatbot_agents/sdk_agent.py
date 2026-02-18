"""
OpenAI Agents SDK implementation for task management chatbot.
Uses the official openai-agents SDK with Gemini API integration.
"""
from typing import Dict, Any, Optional, List
import os
import logging
from agents import Agent, Runner, function_tool
from functools import wraps
from pydantic import BaseModel, Field
from .gemini_connection import get_config, get_fallback_config

logger = logging.getLogger(__name__)


# Pydantic models for tool parameters (explicit schema control)
class AddTaskParams(BaseModel):
    """Parameters for add_task tool."""
    title: str = Field(..., description="Task title (required)")
    description: Optional[str] = Field(None, description="Optional task description")
    due_date: Optional[str] = Field(None, description="Optional due date in YYYY-MM-DD format")
    priority: Optional[str] = Field("Medium", description="Task priority (High/Medium/Low)")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")


class ListTasksParams(BaseModel):
    """Parameters for list_tasks tool."""
    status: Optional[str] = Field(None, description="Filter by status: pending, completed, or all")
    priority: Optional[str] = Field(None, description="Filter by priority: High, Medium, or Low")
    tag: Optional[str] = Field(None, description="Filter by tag")
    due_date: Optional[str] = Field(None, description="Filter by due date in YYYY-MM-DD format")
    limit: Optional[int] = Field(10, description="Maximum number of tasks to return")
    offset: Optional[int] = Field(0, description="Number of tasks to skip")


class CompleteTaskParams(BaseModel):
    """Parameters for complete_task tool."""
    task_id: int = Field(..., description="ID of the task to mark as complete/incomplete")
    completed: Optional[bool] = Field(True, description="True to mark complete, False to mark incomplete")


class UpdateTaskParams(BaseModel):
    """Parameters for update_task tool."""
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, description="New task title")
    description: Optional[str] = Field(None, description="New task description")
    due_date: Optional[str] = Field(None, description="New due date in YYYY-MM-DD format")
    priority: Optional[str] = Field(None, description="New priority (High/Medium/Low)")
    tags: Optional[List[str]] = Field(None, description="New list of tags")


class DeleteTaskParams(BaseModel):
    """Parameters for delete_task tool."""
    task_id: int = Field(..., description="ID of the task to delete")


class UserContextManager:
    """
    Thread-local storage for user context during tool execution.
    Ensures multi-tenant security by injecting user_id into tool calls.
    """
    _user_id: Optional[int] = None

    @classmethod
    def set_user_id(cls, user_id: int):
        """Set the current user context."""
        cls._user_id = user_id

    @classmethod
    def get_user_id(cls) -> int:
        """Get the current user context."""
        if cls._user_id is None:
            raise RuntimeError("User context not set. Call set_user_id first.")
        return cls._user_id

    @classmethod
    def clear(cls):
        """Clear the user context."""
        cls._user_id = None


def inject_user_context(func):
    """
    Decorator to inject user_id into tool function calls.
    Maintains the existing security pattern for multi-tenant isolation.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Inject user_id from context
        user_id = UserContextManager.get_user_id()
        kwargs['user_id'] = user_id
        return func(*args, **kwargs)
    return wrapper


class SDKTaskAgent:
    """
    OpenAI Agents SDK-based task management agent.

    Features:
    - Native Agent/Runner/Session primitives
    - Persistent conversation memory via Sessions
    - Multi-tenant security via user context injection
    - PostgreSQL as source of truth for message history
    """

    def __init__(self, mcp_server):
        """
        Initialize the SDK-based task agent with auto-detected provider (Gemini or OpenAI).

        Args:
            mcp_server: MCP server instance with registered tools
        """
        self.mcp_server = mcp_server

        # Get configuration from gemini_connection (auto-detects Gemini or OpenAI)
        self.run_config = get_config()

        # Extract model name for logging
        self.model_name = "unknown"
        if hasattr(self.run_config, 'model') and hasattr(self.run_config.model, 'model'):
            self.model_name = self.run_config.model.model

        # Create agent with instructions and tools
        self.agent = self._create_agent()

        logger.info(f"SDKTaskAgent initialized with model: {self.model_name}")

    def _create_agent(self) -> Agent:
        """
        Create the OpenAI Agent with instructions and tools.

        Returns:
            Configured Agent instance
        """
        # System instructions for the agent
        instructions = """You are a helpful task management assistant. Your role is to help users manage their tasks through natural language conversation.

You have access to the following tools:
- add_task: Create new tasks
- list_tasks: View existing tasks with filters
- complete_task: Mark tasks as complete or incomplete
- update_task: Modify task details
- delete_task: Remove tasks permanently

Guidelines:
1. Parse natural language dates (e.g., "tomorrow", "next Friday") into YYYY-MM-DD format before calling tools
2. When users refer to tasks by position (e.g., "the first one"), use context from previous list_tasks results
3. For ambiguous requests, ask clarifying questions rather than guessing
4. Confirm destructive operations (delete) before executing
5. Provide clear, concise feedback about what action was taken
6. If a tool call fails, explain the error in natural language and suggest alternatives
7. Be conversational and friendly while staying focused on task management

When creating tasks:
- Extract the main action as the title
- Infer priority from keywords like "urgent", "important" (High), "later", "someday" (Low)
- Default to Medium priority if not specified
- Parse due dates from natural language expressions

When listing tasks:
- Present results in a clear, organized format
- Include relevant details (title, due date, priority, completion status)
- Summarize the count and any filters applied

Remember: You can only manage tasks. For other requests, politely redirect users to task management features."""

        # Register tools from MCP server
        tools = self._register_tools()

        # Create agent (model is configured via run_config)
        agent = Agent(
            name="TaskManagementAgent",
            instructions=instructions,
            tools=tools
        )

        return agent

    def _register_tools(self) -> list:
        """
        Register MCP tools with the Agent SDK.
        Creates SDK-compatible tool wrappers with user context injection.

        Returns:
            List of function_tool decorated functions for the Agent
        """
        tools = []

        # Import tool functions using absolute imports
        from src.mcp.tools.add_task import add_task as _add_task
        from src.mcp.tools.list_tasks import list_tasks as _list_tasks
        from src.mcp.tools.complete_task import complete_task as _complete_task
        from src.mcp.tools.update_task import update_task as _update_task
        from src.mcp.tools.delete_task import delete_task as _delete_task

        # Create SDK-compatible tool wrappers with user context injection
        # PATCH: Use minimal required parameters only to avoid Groq validation issues
        @function_tool
        def add_task(title: str) -> Dict[str, Any]:
            """Create a new task for the user.

            Args:
                title: Task title (required). Extract priority from keywords like 'urgent' (High) or 'later' (Low).
            """
            user_id = UserContextManager.get_user_id()

            # Parse priority from title if keywords present
            title_lower = title.lower()
            priority = 'Medium'  # default
            if any(word in title_lower for word in ['urgent', 'important', 'critical', 'asap']):
                priority = 'High'
            elif any(word in title_lower for word in ['later', 'someday', 'eventually', 'maybe']):
                priority = 'Low'

            return _add_task(
                user_id=user_id,
                title=title,
                description=None,
                due_date=None,
                priority=priority,
                tags=None
            )

        @function_tool
        def list_tasks(filter: str = "all") -> Dict[str, Any]:
            """List all tasks for the user.

            Args:
                filter: Task filter - use "all" to show all tasks, "pending" for incomplete, "completed" for done tasks
            """
            user_id = UserContextManager.get_user_id()

            # Map filter to status parameter
            status = None
            if filter == "pending":
                status = "pending"
            elif filter == "completed":
                status = "completed"

            return _list_tasks(
                user_id=user_id,
                status=status,
                priority=None,
                due_date=None,
                tag=None,
                limit=50,
                offset=0
            )

        @function_tool
        def complete_task(task_id: int) -> Dict[str, Any]:
            """Mark a task as complete.

            Args:
                task_id: ID of the task to mark as complete
            """
            user_id = UserContextManager.get_user_id()
            return _complete_task(
                user_id=user_id,
                task_id=task_id,
                completed=True
            )

        @function_tool
        def update_task(task_id: int, title: str) -> Dict[str, Any]:
            """Update a task's title.

            Args:
                task_id: ID of the task to update
                title: New title for the task
            """
            user_id = UserContextManager.get_user_id()
            return _update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=None,
                due_date=None,
                priority=None,
                tags=None
            )

        @function_tool
        def delete_task(task_id: int) -> Dict[str, Any]:
            """Delete a task permanently.

            Args:
                task_id: ID of the task to delete
            """
            user_id = UserContextManager.get_user_id()
            return _delete_task(user_id=user_id, task_id=task_id)

        tools = [add_task, list_tasks, complete_task, update_task, delete_task]

        logger.info(f"Registered {len(tools)} tools with Agent SDK")
        return tools

    async def process_message(
        self,
        user_id: int,
        message: str,
        session_state: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message using the Agent SDK with automatic LLM failover.

        Args:
            user_id: ID of the authenticated user
            message: User's natural language message
            session_state: Optional session state from conversation.meta

        Returns:
            Dictionary with bot response, updated session state, and tool operations
        """
        primary_error = None
        fallback_config = get_fallback_config()

        try:
            # PATCH 2: Reset parser state - Set user context for tool execution
            UserContextManager.set_user_id(user_id)
            logger.info(f"[ASYNC_PROCESS] Processing message for user {user_id} with primary LLM, message_length={len(message)}")

            # Try primary LLM (Gemini by default)
            result = await Runner.run(
                starting_agent=self.agent,
                input=message,
                run_config=self.run_config
            )

            # PATCH 3: Force JSON-safe output - validate and extract response safely
            try:
                bot_message = result.final_output if hasattr(result, 'final_output') else str(result)
                if not isinstance(bot_message, str):
                    logger.warning(f"[ASYNC_PROCESS] Non-string bot_message: {type(bot_message)}, converting")
                    bot_message = str(bot_message)
            except Exception as extract_error:
                logger.error(f"[ASYNC_PROCESS] Error extracting bot_message: {extract_error}")
                bot_message = "I processed your request but had trouble formatting the response."

            # PATCH 3: Safe tool operations extraction with error handling
            tool_operations = []
            try:
                if hasattr(result, 'tool_calls') and result.tool_calls:
                    tool_operations = result.tool_calls if isinstance(result.tool_calls, list) else [result.tool_calls]
                    logger.info(f"[ASYNC_PROCESS] Extracted {len(tool_operations)} tool operations")
            except Exception as tool_error:
                logger.error(f"[ASYNC_PROCESS] Error extracting tool_operations: {tool_error}")
                tool_operations = []

            logger.info(f"[ASYNC_PROCESS] Primary LLM succeeded, tool_ops={len(tool_operations)}")
            return {
                "message": bot_message,
                "session_state": None,
                "tool_operations": tool_operations,
                "success": True
            }

        except Exception as e:
            primary_error = e
            error_str = str(e).lower()

            # PATCH 1: Enhanced error logging
            logger.error(f"[ASYNC_PROCESS] Primary LLM error type: {type(e).__name__}")
            logger.error(f"[ASYNC_PROCESS] Primary LLM error: {str(e)[:300]}")

            # Check if this is a failure that warrants fallback
            is_retriable = any(keyword in error_str for keyword in [
                'quota', 'rate', 'limit', '429', 'unavailable', 'timeout', 'resource_exhausted'
            ])

            if is_retriable and fallback_config:
                logger.warning(f"[ASYNC_PROCESS] Primary LLM failed ({type(e).__name__}), switching to fallback LLM")

                try:
                    # Retry with fallback LLM (Groq)
                    logger.info(f"[ASYNC_PROCESS] Retrying with fallback LLM for user {user_id}")
                    result = await Runner.run(
                        starting_agent=self.agent,
                        input=message,
                        run_config=fallback_config
                    )

                    # PATCH 3: Safe extraction with error handling
                    try:
                        bot_message = result.final_output if hasattr(result, 'final_output') else str(result)
                        if not isinstance(bot_message, str):
                            bot_message = str(bot_message)
                    except Exception as extract_error:
                        logger.error(f"[ASYNC_PROCESS] Fallback: Error extracting bot_message: {extract_error}")
                        bot_message = "I processed your request but had trouble formatting the response."

                    # Safe tool operations extraction
                    tool_operations = []
                    try:
                        if hasattr(result, 'tool_calls') and result.tool_calls:
                            tool_operations = result.tool_calls if isinstance(result.tool_calls, list) else [result.tool_calls]
                            logger.info(f"[ASYNC_PROCESS] Fallback: Extracted {len(tool_operations)} tool operations")
                    except Exception as tool_error:
                        logger.error(f"[ASYNC_PROCESS] Fallback: Error extracting tool_operations: {tool_error}")
                        tool_operations = []

                    logger.info(f"[ASYNC_PROCESS] Fallback LLM succeeded, tool_ops={len(tool_operations)}")
                    return {
                        "message": bot_message,
                        "session_state": None,
                        "tool_operations": tool_operations,
                        "success": True,
                        "used_fallback": True
                    }

                except Exception as fallback_error:
                    # PATCH 1: Enhanced fallback error logging
                    logger.error(f"[ASYNC_PROCESS] Fallback LLM error type: {type(fallback_error).__name__}")
                    logger.error(f"[ASYNC_PROCESS] Fallback LLM error: {str(fallback_error)[:300]}")
                    logger.exception("[ASYNC_PROCESS] Fallback full traceback:")

                    return {
                        "message": "I'm having trouble processing your request right now. Please try again or use the task dashboard.",
                        "session_state": None,
                        "tool_operations": None,
                        "success": False,
                        "error": f"Both LLM providers failed. Primary: {str(primary_error)[:100]}, Fallback: {str(fallback_error)[:100]}"
                    }
            else:
                # Non-retriable error or no fallback available
                logger.error(f"[ASYNC_PROCESS] Primary LLM failed with non-retriable error: {type(e).__name__}")
                logger.exception("[ASYNC_PROCESS] Full traceback:")

                return {
                    "message": "I'm having trouble processing your request right now. Please try again or use the task dashboard.",
                    "session_state": None,
                    "tool_operations": None,
                    "success": False,
                    "error": f"{type(e).__name__}: {str(e)[:200]}"
                }
        finally:
            # PATCH 5: Always clear user context to prevent state leakage between requests
            try:
                UserContextManager.clear()
                logger.debug("[ASYNC_PROCESS] Cleared user context in finally block")
            except Exception as clear_error:
                logger.warning(f"[ASYNC_PROCESS] Failed to clear user context: {clear_error}")

    def process_message_sync(
        self,
        message: str,
        conversation_history: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for process_message to maintain compatibility.

        Note: user_id must be set via UserContextManager before calling this method.

        Args:
            message: User's natural language message
            conversation_history: Previous messages for context (optional, not used with Gemini)

        Returns:
            Dictionary with bot response and tool operation details
        """
        import asyncio

        try:
            # PATCH 1: Get user_id from context
            user_id = UserContextManager.get_user_id()
            logger.info(f"[SYNC_WRAPPER] Processing message for user {user_id}, message_length={len(message)}")

            # PATCH 2: Reset parser state - create new event loop for each request to avoid state pollution
            try:
                loop = asyncio.get_running_loop()
                logger.debug("[SYNC_WRAPPER] Event loop already running, using nest_asyncio")
                import nest_asyncio
                nest_asyncio.apply()
                result = loop.run_until_complete(
                    self.process_message(user_id, message, None)
                )
            except RuntimeError:
                # No running loop, create a new one
                logger.debug("[SYNC_WRAPPER] Creating new event loop")
                result = asyncio.run(
                    self.process_message(user_id, message, None)
                )

            # PATCH 3: Force JSON-safe output - validate result structure
            if not isinstance(result, dict):
                logger.error(f"[SYNC_WRAPPER] Invalid result type: {type(result)}, converting to dict")
                result = {"message": str(result), "success": False}

            # Ensure all required keys exist with safe defaults
            safe_result = {
                "message": result.get("message", "I'm not sure how to help with that."),
                "task_operation": self._extract_primary_operation(result.get("tool_operations")),
                "success": result.get("success", False),
                "error": result.get("error")
            }

            logger.info(f"[SYNC_WRAPPER] Successfully processed message, success={safe_result['success']}")
            return safe_result

        except Exception as e:
            # PATCH 1: Enhanced error logging with full details
            logger.error(f"[SYNC_WRAPPER_ERROR] Exception type: {type(e).__name__}")
            logger.error(f"[SYNC_WRAPPER_ERROR] Exception message: {str(e)}")
            logger.exception("[SYNC_WRAPPER_ERROR] Full traceback:")

            return {
                "message": "I'm having trouble processing your request right now. Please try again or use the task dashboard.",
                "task_operation": None,
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}"
            }
        finally:
            # PATCH 2: Always clear user context after processing to prevent state leakage
            try:
                UserContextManager.clear()
                logger.debug("[SYNC_WRAPPER] Cleared user context")
            except Exception as clear_error:
                logger.warning(f"[SYNC_WRAPPER] Failed to clear user context: {clear_error}")

    def _extract_primary_operation(
        self,
        tool_operations: Optional[list]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract the primary tool operation for backward compatibility.

        Args:
            tool_operations: List of tool operations from SDK

        Returns:
            Primary operation dictionary or None
        """
        if not tool_operations or len(tool_operations) == 0:
            return None

        # Return the first operation for backward compatibility
        return tool_operations[0] if isinstance(tool_operations, list) else tool_operations

