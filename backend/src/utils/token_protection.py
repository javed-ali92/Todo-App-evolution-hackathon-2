"""
Token overflow protection for LLM context management.
Prevents prompt length from exceeding model limits.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class TokenLimitConfig:
    """Token limits for different models."""
    GEMINI_2_0_FLASH = 1_000_000  # 1M context window
    LLAMA_3_1_8B = 128_000  # 128K context window
    GPT_4_TURBO = 128_000  # 128K context window

    # Safety margins (use 80% of limit)
    SAFETY_MARGIN = 0.8


class TokenCounter:
    """
    Approximate token counter for prompt management.

    Uses character-based estimation: ~4 chars per token for English.
    """

    CHARS_PER_TOKEN = 4

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """Estimate token count from text."""
        return len(text) // cls.CHARS_PER_TOKEN

    @classmethod
    def estimate_messages_tokens(cls, messages: List[Dict[str, str]]) -> int:
        """Estimate total tokens in message list."""
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            # Add overhead for message structure
            total += cls.estimate_tokens(content) + cls.estimate_tokens(role) + 4
        return total


class TokenOverflowProtection:
    """
    Protects against token overflow by managing conversation history.

    Strategies:
    1. Truncate old messages
    2. Summarize conversation
    3. Keep only recent context
    """

    def __init__(self, max_tokens: int, model_name: str = "gemini-2.0-flash"):
        self.max_tokens = int(max_tokens * TokenLimitConfig.SAFETY_MARGIN)
        self.model_name = model_name
        logger.info(
            f"[TOKEN_PROTECTION] Initialized for {model_name} "
            f"with limit {self.max_tokens} tokens"
        )

    def check_and_compress(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        current_message: str
    ) -> tuple[str, List[Dict[str, str]], bool]:
        """
        Check token count and compress if needed.

        Args:
            system_prompt: System instructions
            conversation_history: Previous messages
            current_message: Current user message

        Returns:
            Tuple of (system_prompt, compressed_history, was_compressed)
        """
        # Estimate current token usage
        system_tokens = TokenCounter.estimate_tokens(system_prompt)
        history_tokens = TokenCounter.estimate_messages_tokens(conversation_history)
        current_tokens = TokenCounter.estimate_tokens(current_message)

        total_tokens = system_tokens + history_tokens + current_tokens

        logger.debug(
            f"[TOKEN_PROTECTION] Estimated tokens: "
            f"system={system_tokens} history={history_tokens} "
            f"current={current_tokens} total={total_tokens} "
            f"limit={self.max_tokens}"
        )

        if total_tokens <= self.max_tokens:
            logger.debug("[TOKEN_PROTECTION] Within limit, no compression needed")
            return system_prompt, conversation_history, False

        logger.warning(
            f"[TOKEN_PROTECTION] Token limit exceeded "
            f"({total_tokens} > {self.max_tokens}), compressing"
        )

        # Strategy: Keep recent messages, drop old ones
        compressed_history = self._truncate_history(
            conversation_history,
            target_tokens=self.max_tokens - system_tokens - current_tokens - 1000  # Reserve 1K buffer
        )

        compressed_tokens = TokenCounter.estimate_messages_tokens(compressed_history)
        logger.info(
            f"[TOKEN_PROTECTION] Compressed history from "
            f"{history_tokens} to {compressed_tokens} tokens "
            f"(kept {len(compressed_history)}/{len(conversation_history)} messages)"
        )

        return system_prompt, compressed_history, True

    def _truncate_history(
        self,
        history: List[Dict[str, str]],
        target_tokens: int
    ) -> List[Dict[str, str]]:
        """
        Truncate history to fit within target token count.

        Keeps most recent messages, drops oldest first.
        """
        if not history:
            return []

        # Start from most recent and work backwards
        compressed = []
        current_tokens = 0

        for msg in reversed(history):
            msg_tokens = TokenCounter.estimate_tokens(msg.get("content", ""))

            if current_tokens + msg_tokens > target_tokens:
                # Would exceed limit, stop here
                break

            compressed.insert(0, msg)
            current_tokens += msg_tokens

        if len(compressed) < len(history):
            # Add a system message indicating truncation
            compressed.insert(0, {
                "role": "system",
                "content": f"[Previous conversation truncated - showing last {len(compressed)} messages]"
            })

        return compressed

    def validate_prompt_length(self, prompt: str) -> bool:
        """
        Validate that a single prompt is within limits.

        Returns:
            True if valid, False if too long
        """
        tokens = TokenCounter.estimate_tokens(prompt)

        if tokens > self.max_tokens:
            logger.error(
                f"[TOKEN_PROTECTION] Single prompt exceeds limit "
                f"({tokens} > {self.max_tokens} tokens)"
            )
            return False

        return True


def get_token_protector(model_name: str) -> TokenOverflowProtection:
    """
    Factory function to create token protector for specific model.

    Args:
        model_name: Name of the LLM model

    Returns:
        Configured TokenOverflowProtection instance
    """
    model_lower = model_name.lower()

    if "gemini" in model_lower:
        max_tokens = TokenLimitConfig.GEMINI_2_0_FLASH
    elif "llama" in model_lower or "groq" in model_lower:
        max_tokens = TokenLimitConfig.LLAMA_3_1_8B
    elif "gpt" in model_lower:
        max_tokens = TokenLimitConfig.GPT_4_TURBO
    else:
        # Default to conservative limit
        max_tokens = 100_000
        logger.warning(
            f"[TOKEN_PROTECTION] Unknown model {model_name}, "
            f"using default limit {max_tokens}"
        )

    return TokenOverflowProtection(max_tokens, model_name)
