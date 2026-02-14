"""
OpenAI Agent configuration for task management chatbot.
Handles natural language understanding and tool execution.
"""
from typing import Dict, Any, List, Optional
import os
import logging
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import OpenAI, APIError, APITimeoutError

logger = logging.getLogger(__name__)


class TaskAgent:
    """
    OpenAI-powered agent for task management through natural language.

    The agent interprets user intent, selects appropriate tools,
    and generates natural language responses.
    """

    def __init__(self, mcp_server):
        """
        Initialize the task agent.

        Args:
            mcp_server: MCP server instance with registered tools
        """
        self.mcp_server = mcp_server
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Configure OpenAI client
        self.client = OpenAI(api_key=self.api_key)

        # System prompt for task management
        self.system_prompt = """You are a helpful task management assistant. Your role is to help users manage their tasks through natural language conversation.

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

        logger.info(f"TaskAgent initialized with model: {self.model}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((APITimeoutError, APIError)),
        reraise=True
    )
    def process_message(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a response.

        Uses circuit breaker pattern with exponential backoff for retries.

        Args:
            user_message: User's natural language message
            conversation_history: Previous messages for context (list of {role, content})

        Returns:
            Dictionary with bot response and tool operation details

        Raises:
            APITimeoutError: If request times out after retries
            APIError: If API returns an error after retries
        """
        try:
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)

            # Add current user message
            messages.append({"role": "user", "content": user_message})

            # Get tool schemas for function calling
            tools = self._build_tool_definitions()

            # Call OpenAI API with timeout
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                timeout=10  # 10 second timeout
            )

            # Extract response
            assistant_message = response.choices[0].message

            # Check if agent wants to call a tool
            if assistant_message.tool_calls:
                return self._handle_tool_calls(assistant_message, messages)

            # No tool call - return text response
            return {
                "message": assistant_message.content,
                "task_operation": None
            }

        except APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {str(e)}")
            raise
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in agent: {str(e)}")
            return {
                "message": "I'm having trouble processing your request right now. Please try again or use the task dashboard.",
                "task_operation": None,
                "error": str(e)
            }

    def _build_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Build OpenAI function calling definitions from MCP tool schemas.

        Returns:
            List of tool definitions for OpenAI API
        """
        tools = []
        for tool_name, schema in self.mcp_server.get_tool_schemas().items():
            tools.append({
                "type": "function",
                "function": {
                    "name": schema["name"],
                    "description": schema["description"],
                    "parameters": schema["parameters"]
                }
            })
        return tools

    def _handle_tool_calls(
        self,
        assistant_message: Any,
        messages: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Handle tool calls from the agent.

        Args:
            assistant_message: Assistant message with tool calls
            messages: Conversation messages

        Returns:
            Dictionary with bot response and tool operation details
        """
        tool_calls = assistant_message.tool_calls
        tool_results = []

        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = eval(tool_call.function.arguments)

            # Execute tool via MCP server
            result = self.mcp_server.execute_tool(function_name, function_args)
            tool_results.append(result)

        # For now, return the first tool result
        # In a more sophisticated implementation, we'd call OpenAI again with tool results
        if tool_results:
            first_result = tool_results[0]
            if first_result.get("success"):
                return {
                    "message": self._format_success_message(first_result),
                    "task_operation": first_result
                }
            else:
                return {
                    "message": f"I encountered an error: {first_result.get('error', 'Unknown error')}",
                    "task_operation": first_result
                }

        return {
            "message": "I processed your request.",
            "task_operation": None
        }

    def _format_success_message(self, result: Dict[str, Any]) -> str:
        """
        Format a success message from tool result.

        Args:
            result: Tool execution result

        Returns:
            Natural language success message
        """
        # Simple formatting - in production, this would be more sophisticated
        if "task" in result:
            task = result["task"]
            if "id" in task and "title" in task:
                return f"Done! I've updated the task '{task['title']}'."

        if "tasks" in result:
            count = result.get("count", 0)
            if count == 0:
                return "You don't have any tasks matching those criteria."
            elif count == 1:
                return f"You have 1 task: {result['tasks'][0]['title']}"
            else:
                return f"You have {count} tasks."

        if "message" in result:
            return result["message"]

        return "Done!"
