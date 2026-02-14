"""
MCP (Model Context Protocol) Server for AI Chatbot.
Provides tool registration and execution for the OpenAI agent.
"""
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class MCPServer:
    """
    MCP Server that manages tool registration and execution.

    Tools are functions that the AI agent can call to perform task operations.
    Each tool receives a user_id from the context for authorization.
    """

    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_schemas: Dict[str, Dict[str, Any]] = {}
        self._user_context: Optional[int] = None

    def register_tool(
        self,
        name: str,
        function: Callable,
        schema: Dict[str, Any]
    ) -> None:
        """
        Register a tool with the MCP server.

        Args:
            name: Tool name (e.g., "add_task")
            function: Callable function to execute
            schema: JSON schema describing parameters and return type
        """
        self.tools[name] = function
        self.tool_schemas[name] = schema
        logger.info(f"Registered MCP tool: {name}")

    def set_user_context(self, user_id: int) -> None:
        """
        Set the current user context for tool execution.

        Args:
            user_id: ID of the authenticated user
        """
        self._user_context = user_id

    def get_user_context(self) -> int:
        """
        Get the current user context.

        Returns:
            user_id: ID of the authenticated user

        Raises:
            RuntimeError: If user context is not set
        """
        if self._user_context is None:
            raise RuntimeError("User context not set. Call set_user_context first.")
        return self._user_context

    def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a registered tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters

        Returns:
            Tool execution result with structured error handling

        Raises:
            ValueError: If tool is not registered
            RuntimeError: If user context is not set
        """
        if tool_name not in self.tools:
            error_msg = f"Tool '{tool_name}' not registered"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }

        try:
            # Inject user_id into parameters
            user_id = self.get_user_context()
            parameters["user_id"] = user_id

            # Execute tool
            logger.info(f"Executing tool: {tool_name} for user: {user_id}")
            result = self.tools[tool_name](**parameters)

            # Ensure result has success field
            if "success" not in result:
                logger.warning(f"Tool {tool_name} returned result without 'success' field")
                result["success"] = True

            logger.info(f"Tool {tool_name} executed successfully")
            return result

        except TypeError as e:
            # Parameter validation error
            error_msg = f"Invalid parameters for tool {tool_name}: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": f"Validation error: {str(e)}"
            }
        except Exception as e:
            # General execution error
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(f"{error_msg} (tool: {tool_name})")
            return {
                "success": False,
                "error": error_msg
            }

    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered tool schemas for agent configuration.

        Returns:
            Dictionary of tool schemas
        """
        return self.tool_schemas

    def list_tools(self) -> list[str]:
        """
        List all registered tool names.

        Returns:
            List of tool names
        """
        return list(self.tools.keys())


# Global MCP server instance
mcp_server = MCPServer()


def initialize_mcp_tools():
    """
    Initialize and register all MCP tools with the server.
    This should be called during application startup.
    """
    from .tools.add_task import add_task, TOOL_SCHEMA as add_task_schema
    from .tools.list_tasks import list_tasks, TOOL_SCHEMA as list_tasks_schema
    from .tools.complete_task import complete_task, TOOL_SCHEMA as complete_task_schema
    from .tools.update_task import update_task, TOOL_SCHEMA as update_task_schema
    from .tools.delete_task import delete_task, TOOL_SCHEMA as delete_task_schema

    # Register all tools
    mcp_server.register_tool("add_task", add_task, add_task_schema)
    mcp_server.register_tool("list_tasks", list_tasks, list_tasks_schema)
    mcp_server.register_tool("complete_task", complete_task, complete_task_schema)
    mcp_server.register_tool("update_task", update_task, update_task_schema)
    mcp_server.register_tool("delete_task", delete_task, delete_task_schema)

    logger.info(f"MCP server initialized with {len(mcp_server.list_tools())} tools")

