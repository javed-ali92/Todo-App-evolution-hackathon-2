"""
Immutable configuration factory for LLM providers.
Creates fresh config instances per request to prevent state mutation.
"""
import os
import logging
from typing import Optional
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig

logger = logging.getLogger(__name__)


class ImmutableConfigFactory:
    """
    Factory for creating fresh, immutable LLM configurations.

    Each call to get_config() returns a NEW instance to prevent
    state mutation across requests.
    """

    @staticmethod
    def create_gemini_config() -> Optional[RunConfig]:
        """Create fresh Gemini configuration."""
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key.startswith("sk-your"):
            return None

        # Create NEW instances each time
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

        model = OpenAIChatCompletionsModel(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            openai_client=client,
        )

        config = RunConfig(
            model=model,
            model_provider=client,
        )

        logger.debug("[CONFIG_FACTORY] Created fresh Gemini config")
        return config

    @staticmethod
    def create_groq_config() -> Optional[RunConfig]:
        """Create fresh Groq configuration."""
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key or api_key.startswith("sk-your"):
            return None

        # Create NEW instances each time
        client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1/",
        )

        model = OpenAIChatCompletionsModel(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            openai_client=client,
        )

        config = RunConfig(
            model=model,
            model_provider=client,
        )

        logger.debug("[CONFIG_FACTORY] Created fresh Groq config")
        return config

    @staticmethod
    def create_openai_config() -> Optional[RunConfig]:
        """Create fresh OpenAI configuration."""
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key or api_key.startswith("sk-your"):
            return None

        # Create NEW instances each time
        client = AsyncOpenAI(api_key=api_key)

        model = OpenAIChatCompletionsModel(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            openai_client=client,
        )

        config = RunConfig(
            model=model,
            model_provider=client,
        )

        logger.debug("[CONFIG_FACTORY] Created fresh OpenAI config")
        return config

    @classmethod
    def get_primary_config(cls) -> RunConfig:
        """
        Get primary LLM configuration (fresh instance).

        Returns:
            Fresh RunConfig instance

        Raises:
            ValueError: If no valid configuration available
        """
        primary_llm = os.getenv("PRIMARY_LLM", "gemini").lower()

        if primary_llm == "groq":
            config = cls.create_groq_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using Groq as primary")
                return config

            config = cls.create_gemini_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using Gemini as fallback")
                return config

        else:  # Default to Gemini
            config = cls.create_gemini_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using Gemini as primary")
                return config

            config = cls.create_groq_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using Groq as fallback")
                return config

        # Last resort: OpenAI
        config = cls.create_openai_config()
        if config:
            logger.info("[CONFIG_FACTORY] Using OpenAI as last resort")
            return config

        raise ValueError(
            "No AI provider configured. Please set either:\n"
            "  - GEMINI_API_KEY (recommended)\n"
            "  - GROQ_API_KEY\n"
            "  - OPENAI_API_KEY\n"
            "in your .env file with a valid API key."
        )

    @classmethod
    def get_fallback_config(cls) -> Optional[RunConfig]:
        """
        Get fallback LLM configuration (fresh instance).

        Returns:
            Fresh RunConfig instance or None if no fallback available
        """
        primary_llm = os.getenv("PRIMARY_LLM", "gemini").lower()

        if primary_llm == "groq":
            # If Groq is primary, try Gemini then OpenAI
            config = cls.create_gemini_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using Gemini as fallback")
                return config

            config = cls.create_openai_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using OpenAI as fallback")
                return config

        else:  # Gemini is primary
            # Try Groq then OpenAI
            config = cls.create_groq_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using Groq as fallback")
                return config

            config = cls.create_openai_config()
            if config:
                logger.info("[CONFIG_FACTORY] Using OpenAI as fallback")
                return config

        logger.warning("[CONFIG_FACTORY] No fallback configuration available")
        return None
