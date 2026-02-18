"""
AI Agent configuration for task management chatbot.
Handles natural language understanding and tool execution using OpenAI or Gemini.
Automatically detects and uses available provider.
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
    AI-powered agent for task management through natural language.

    The agent interprets user intent, selects appropriate tools,
    and generates natural language responses.

    Supports both OpenAI and Gemini providers with automatic detection.
    """

    def __init__(self, mcp_server):
        """
        Initialize the task agent with available AI provider.

        Args:
            mcp_server: MCP server instance with registered tools

        Raises:
            ValueError: If no valid API key is configured
        """
        self.mcp_server = mcp_server

        # Detect and configure provider
        self.provider, self.api_key, self.model = self._detect_provider()

        if not self.provider:
            raise ValueError(
                "No AI provider configured. Please set either:\n"
                "  - GEMINI_API_KEY (recommended)\n"
                "  - OPENAI_API_KEY\n"
                "in your .env file with a valid API key."
            )

        # Configure client based on provider
        if self.provider == "gemini":
            # Configure OpenAI client with Gemini's OpenAI-compatible endpoint
            # Reference: https://ai.google.dev/gemini-api/docs/openai
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
        else:  # openai
            self.client = OpenAI(api_key=self.api_key)

        logger.info(f"✓ TaskAgent initialized with provider: {self.provider.upper()}, model: {self.model}")

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

    def _detect_provider(self) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Detect which AI provider is available based on environment variables.

        Priority order:
        1. Gemini (GEMINI_API_KEY) - recommended, more cost-effective
        2. OpenAI (OPENAI_API_KEY) - fallback

        Returns:
            Tuple of (provider_name, api_key, model_name) or (None, None, None)
        """
        # Check Gemini first (preferred)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key != "sk-your-openai-api-key-here" and not gemini_key.startswith("sk-your"):
            model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            logger.info(f"✓ Detected Gemini API key, using model: {model}")
            return ("gemini", gemini_key, model)

        # Check OpenAI as fallback
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "sk-your-openai-api-key-here" and not openai_key.startswith("sk-your"):
            model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
            logger.info(f"✓ Detected OpenAI API key, using model: {model}")
            return ("openai", openai_key, model)

        # No valid provider found
        logger.error("✗ No valid AI provider API key found")
        logger.error("  Checked: GEMINI_API_KEY, OPENAI_API_KEY")
        logger.error("  Please configure at least one provider in .env file")
        return (None, None, None)

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
            logger.info(f"[AGENT_START] Processing message, length={len(user_message)}, history_count={len(conversation_history) if conversation_history else 0}")

            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]

            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history)
                logger.debug(f"[AGENT] Added {len(conversation_history)} history messages")

            # Add current user message
            messages.append({"role": "user", "content": user_message})
            logger.debug(f"[AGENT] Total messages for API: {len(messages)}")

            # Get tool schemas for function calling
            tools = self._build_tool_definitions()
            logger.debug(f"[AGENT] Built {len(tools)} tool definitions")

            # Call AI provider API with timeout
            logger.info(f"[AGENT] Calling {self.provider.upper()} API (model={self.model})")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                timeout=10  # 10 second timeout
            )
            logger.info(f"[AGENT] Received response from {self.provider.upper()} API")

            # Extract response
            assistant_message = response.choices[0].message
            logger.debug(f"[AGENT] Assistant message has_tool_calls={assistant_message.tool_calls is not None}")

            # Check if agent wants to call a tool
            if assistant_message.tool_calls:
                logger.info(f"[AGENT] Processing {len(assistant_message.tool_calls)} tool calls")
                return self._handle_tool_calls(assistant_message, messages)

            # No tool call - return text response
            logger.info(f"[AGENT_SUCCESS] Returning text response, length={len(assistant_message.content) if assistant_message.content else 0}")
            return {
                "message": assistant_message.content,
                "task_operation": None
            }

        except APITimeoutError as e:
            logger.error(f"[AGENT_ERROR] OpenAI API timeout: {str(e)}")
            logger.exception(f"[AGENT_ERROR] Timeout traceback:")
            raise
        except APIError as e:
            logger.error(f"[AGENT_ERROR] OpenAI API error: {type(e).__name__}: {str(e)}")
            logger.error(f"[AGENT_ERROR] Error details: status_code={getattr(e, 'status_code', 'N/A')}, response={getattr(e, 'response', 'N/A')}")
            logger.exception(f"[AGENT_ERROR] API error traceback:")
            raise
        except Exception as e:
            logger.error(f"[AGENT_ERROR] Unexpected error in agent: {type(e).__name__}: {str(e)}")
            logger.exception(f"[AGENT_ERROR] Full traceback:")
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

            # Parse function arguments safely using json.loads instead of eval
            try:
                function_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                logger.error(f"[AGENT_ERROR] Failed to parse tool arguments: {str(e)}")
                return {
                    "message": "I had trouble understanding the parameters for that action.",
                    "task_operation": {
                        "success": False,
                        "error": f"Invalid tool arguments: {str(e)}"
                    }
                }

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
