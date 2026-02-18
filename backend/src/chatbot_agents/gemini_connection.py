"""
Gemini LLM connection configuration using OpenAI Agents SDK.
Provides async client and model configuration for Gemini API.
"""
from dotenv import load_dotenv
import os
import logging

# Now we can import from the installed 'agents' package without shadowing
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig

load_dotenv()
logger = logging.getLogger(__name__)

# Get Gemini API key from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present
if not gemini_api_key or gemini_api_key.startswith("sk-your"):
    logger.warning("GEMINI_API_KEY is not properly configured")
    gemini_client = None
    gemini_model = None
    gemini_config = None
else:
    # Reference: https://ai.google.dev/gemini-api/docs/openai
    gemini_client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    gemini_model = OpenAIChatCompletionsModel(
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        openai_client=gemini_client,
    )

    gemini_config = RunConfig(
        model=gemini_model,
        model_provider=gemini_client,
    )

    logger.info(f"Gemini connection configured with model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}")


# Groq fallback configuration
groq_api_key = os.getenv("GROQ_API_KEY")

if groq_api_key and not groq_api_key.startswith("sk-your"):
    groq_client = AsyncOpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1/",
    )

    groq_model = OpenAIChatCompletionsModel(
        model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        openai_client=groq_client,
    )

    groq_config = RunConfig(
        model=groq_model,
        model_provider=groq_client,
    )

    logger.info(f"Groq connection configured with model: {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')}")
else:
    groq_client = None
    groq_model = None
    groq_config = None


# OpenAI fallback configuration
openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key and not openai_api_key.startswith("sk-your"):
    openai_client = AsyncOpenAI(api_key=openai_api_key)

    openai_model = OpenAIChatCompletionsModel(
        model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
        openai_client=openai_client,
    )

    openai_config = RunConfig(
        model=openai_model,
        model_provider=openai_client,
    )

    logger.info(f"OpenAI connection configured with model: {os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')}")
else:
    openai_client = None
    openai_model = None
    openai_config = None


def get_config():
    """
    Get the best available RunConfig (Gemini preferred, Groq fallback).

    Returns:
        RunConfig: Configuration for the AI model

    Raises:
        ValueError: If no valid configuration is available
    """
    primary_llm = os.getenv("PRIMARY_LLM", "gemini").lower()

    if primary_llm == "groq":
        # Groq as primary
        if groq_config:
            logger.info("Using Groq configuration (primary)")
            return groq_config
        elif gemini_config:
            logger.info("Using Gemini configuration (fallback)")
            return gemini_config
    else:
        # Gemini as primary (default)
        if gemini_config:
            logger.info("Using Gemini configuration (primary)")
            return gemini_config
        elif groq_config:
            logger.info("Using Groq configuration (fallback)")
            return groq_config

    # Last resort: OpenAI
    if openai_config:
        logger.info("Using OpenAI configuration (last resort)")
        return openai_config

    raise ValueError(
        "No AI provider configured. Please set either:\n"
        "  - GEMINI_API_KEY (recommended)\n"
        "  - GROQ_API_KEY\n"
        "  - OPENAI_API_KEY\n"
        "in your .env file with a valid API key."
    )


def get_fallback_config():
    """
    Get the fallback RunConfig for automatic retry.

    Returns:
        RunConfig or None: Fallback configuration if available
    """
    primary_llm = os.getenv("PRIMARY_LLM", "gemini").lower()

    if primary_llm == "groq":
        # If Groq is primary, Gemini is fallback
        return gemini_config if gemini_config else openai_config
    else:
        # If Gemini is primary, Groq is fallback
        return groq_config if groq_config else openai_config
