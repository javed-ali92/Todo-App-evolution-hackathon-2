"""
Performance optimization utilities for production agent.

Features:
- Tool schema caching
- Lazy tool loading
- Response streaming support
- Prompt compression
"""
import logging
from typing import Dict, Any, Optional, List
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)


class ToolSchemaCache:
    """
    Cache for tool schemas to avoid regeneration on every request.

    Tool schemas are static and can be safely cached.
    """

    _cache: Dict[str, Any] = {}

    @classmethod
    def get_or_generate(cls, tool_name: str, generator_func) -> Any:
        """
        Get cached schema or generate and cache it.

        Args:
            tool_name: Name of the tool
            generator_func: Function to generate schema if not cached

        Returns:
            Tool schema
        """
        if tool_name not in cls._cache:
            logger.debug(f"[CACHE] Generating schema for {tool_name}")
            cls._cache[tool_name] = generator_func()
        else:
            logger.debug(f"[CACHE] Using cached schema for {tool_name}")

        return cls._cache[tool_name]

    @classmethod
    def clear(cls):
        """Clear all cached schemas."""
        cls._cache.clear()
        logger.info("[CACHE] Cleared tool schema cache")


class PromptCompressor:
    """
    Compress prompts by removing redundant context.

    Strategies:
    - Remove duplicate information
    - Summarize repetitive patterns
    - Strip unnecessary whitespace
    """

    @staticmethod
    def compress_conversation_history(
        messages: List[Dict[str, str]],
        max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """
        Compress conversation history by keeping only recent messages.

        Args:
            messages: Full conversation history
            max_messages: Maximum messages to keep

        Returns:
            Compressed message list
        """
        if len(messages) <= max_messages:
            return messages

        # Keep most recent messages
        compressed = messages[-max_messages:]

        logger.info(
            f"[OPTIMIZE] Compressed conversation from "
            f"{len(messages)} to {len(compressed)} messages"
        )

        return compressed

    @staticmethod
    def deduplicate_context(text: str) -> str:
        """
        Remove duplicate sentences from text.

        Args:
            text: Input text

        Returns:
            Deduplicated text
        """
        sentences = text.split('. ')
        seen = set()
        unique = []

        for sentence in sentences:
            sentence_hash = hashlib.md5(sentence.encode()).hexdigest()
            if sentence_hash not in seen:
                seen.add(sentence_hash)
                unique.append(sentence)

        result = '. '.join(unique)

        if len(unique) < len(sentences):
            logger.debug(
                f"[OPTIMIZE] Deduplicated {len(sentences) - len(unique)} "
                f"duplicate sentences"
            )

        return result


class LazyToolLoader:
    """
    Lazy loading for tool functions to reduce initialization time.

    Tools are only imported and initialized when first used.
    """

    _loaded_tools: Dict[str, Any] = {}

    @classmethod
    def load_tool(cls, tool_name: str):
        """
        Lazy load a tool function.

        Args:
            tool_name: Name of the tool to load

        Returns:
            Tool function
        """
        if tool_name in cls._loaded_tools:
            return cls._loaded_tools[tool_name]

        logger.debug(f"[LAZY_LOAD] Loading tool: {tool_name}")

        # Import on demand
        if tool_name == "add_task":
            from src.mcp.tools.add_task import add_task
            cls._loaded_tools[tool_name] = add_task
        elif tool_name == "list_tasks":
            from src.mcp.tools.list_tasks import list_tasks
            cls._loaded_tools[tool_name] = list_tasks
        elif tool_name == "complete_task":
            from src.mcp.tools.complete_task import complete_task
            cls._loaded_tools[tool_name] = complete_task
        elif tool_name == "update_task":
            from src.mcp.tools.update_task import update_task
            cls._loaded_tools[tool_name] = update_task
        elif tool_name == "delete_task":
            from src.mcp.tools.delete_task import delete_task
            cls._loaded_tools[tool_name] = delete_task
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

        return cls._loaded_tools[tool_name]


class ResponseOptimizer:
    """
    Optimize response generation and delivery.

    Features:
    - Response caching for identical queries
    - Streaming support preparation
    """

    _response_cache: Dict[str, str] = {}
    _cache_size_limit = 100

    @classmethod
    def get_cached_response(cls, query_hash: str) -> Optional[str]:
        """
        Get cached response for identical query.

        Args:
            query_hash: Hash of the query

        Returns:
            Cached response or None
        """
        return cls._response_cache.get(query_hash)

    @classmethod
    def cache_response(cls, query_hash: str, response: str):
        """
        Cache a response for future identical queries.

        Args:
            query_hash: Hash of the query
            response: Response to cache
        """
        # Implement LRU-style eviction
        if len(cls._response_cache) >= cls._cache_size_limit:
            # Remove oldest entry
            oldest_key = next(iter(cls._response_cache))
            del cls._response_cache[oldest_key]
            logger.debug("[CACHE] Evicted oldest response from cache")

        cls._response_cache[query_hash] = response
        logger.debug(f"[CACHE] Cached response for query hash {query_hash[:8]}")

    @staticmethod
    def compute_query_hash(user_id: int, message: str) -> str:
        """
        Compute hash for query caching.

        Args:
            user_id: User ID
            message: User message

        Returns:
            Query hash
        """
        query_str = f"{user_id}:{message}"
        return hashlib.sha256(query_str.encode()).hexdigest()


@lru_cache(maxsize=128)
def get_system_instructions() -> str:
    """
    Cached system instructions to avoid string recreation.

    Returns:
        System instructions string
    """
    return """You are a helpful task management assistant. Your role is to help users manage their tasks through natural language conversation.

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
