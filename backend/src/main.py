from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.database import engine, DATABASE_URL
from .database.validation import test_connection, validate_schema
from .models import user, task, session
# Import new chatbot models
from .models import conversation, message, rate_limit
from .api.auth import router as auth_router
from .api.tasks import router as tasks_router
from .api.chat import router as chat_router
from .api.chat_sdk import router as chat_sdk_router
from sqlmodel import SQLModel
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
def create_db_and_tables():
    """Create database tables and validate connection."""
    try:
        # Step 1: Test database connection (Task T020)
        logger.info("Testing database connection to Neon PostgreSQL...")
        test_connection(engine)

        # Step 2: Log sanitized connection details (Task T021)
        # Extract database name and host without exposing credentials
        if DATABASE_URL:
            # Parse connection string safely
            if "postgresql://" in DATABASE_URL or "postgres://" in DATABASE_URL:
                # Extract host and database name without password
                parts = DATABASE_URL.split("@")
                if len(parts) > 1:
                    host_db = parts[1].split("/")
                    host = host_db[0].split(":")[0] if host_db else "unknown"
                    db_name = host_db[1].split("?")[0] if len(host_db) > 1 else "unknown"
                    logger.info(f"Connected to Neon PostgreSQL - Host: {host}, Database: {db_name}")
                else:
                    logger.info("Connected to Neon PostgreSQL")

        # Step 3: Create tables
        logger.info("Creating database tables...")
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully!")

        # Step 4: Validate schema (Task T019)
        logger.info("Validating database schema...")
        validate_schema(engine)
        logger.info("Database schema validation passed!")

    except Exception as e:
        # Task T022: Error handling for connection failures
        logger.error(f"Database initialization failed: {str(e)}")
        logger.error("Application cannot start without valid Neon PostgreSQL connection.")
        logger.error("Please verify:")
        logger.error("  1. DATABASE_URL environment variable is set correctly")
        logger.error("  2. Neon database is accessible")
        logger.error("  3. Network connectivity is available")
        raise RuntimeError(f"Database initialization failed: {str(e)}") from e

# Initialize FastAPI app
app = FastAPI(
    title="Todo API",
    description="API for managing todos with authentication",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    # Additional options for preflight requests
    # allow_origin_regex=r"https?://.*",
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Include routers
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])
app.include_router(chat_router, tags=["chat"])
app.include_router(chat_sdk_router, tags=["chat-sdk"])

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    # Initialize MCP tools
    from .mcp.server import initialize_mcp_tools
    initialize_mcp_tools()
    logger.info("MCP tools initialized")

    # Validate AI provider configuration
    validate_ai_provider()


def validate_ai_provider():
    """
    Validate that at least one AI provider is configured.

    Checks for valid API keys and logs which provider will be used.
    Raises RuntimeError if no valid provider is found.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    # Check if keys are set and not placeholder values
    has_gemini = gemini_key and gemini_key != "sk-your-openai-api-key-here" and not gemini_key.startswith("sk-your")
    has_openai = openai_key and openai_key != "sk-your-openai-api-key-here" and not openai_key.startswith("sk-your")

    if has_gemini:
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        logger.info(f"AI Provider: Gemini (model: {model})")
        return

    if has_openai:
        model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        logger.info(f"AI Provider: OpenAI (model: {model})")
        return

    # No valid provider found
    logger.error("AI Provider Configuration Error")
    logger.error("  No valid API key found for AI chatbot")
    logger.error("  Please set one of the following in .env:")
    logger.error("    - GEMINI_API_KEY (recommended)")
    logger.error("    - OPENAI_API_KEY")
    logger.error("  Chatbot features will not work until configured")
    raise RuntimeError(
        "AI provider not configured. Set GEMINI_API_KEY or OPENAI_API_KEY in .env file."
    )

@app.get("/")
def read_root():
    return {"message": "Welcome to the Todo API"}

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable with fallback to 7860 for Hugging Face Spaces
    port = int(os.getenv("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)