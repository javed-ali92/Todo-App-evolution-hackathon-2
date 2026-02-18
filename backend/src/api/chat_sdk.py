"""
Chat API endpoints using OpenAI Agents SDK.
This is a new endpoint for gradual migration - can run alongside existing chat.py
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session
from typing import Optional
from pydantic import BaseModel, Field
import uuid
import logging
from ..database.database import engine
from ..services.chat_service_sdk import ChatServiceSDK
from ..services.rate_limit_service import RateLimitService
from ..auth.jwt_handler import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models (same as original)
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: str
    message: str
    task_operation: Optional[dict] = None


def get_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session


def verify_user_access(user_id: int, token_user_id: int) -> None:
    """
    Verify that the authenticated user matches the user_id in the URL.

    Args:
        user_id: User ID from URL path
        token_user_id: User ID from JWT token

    Raises:
        HTTPException: If user IDs don't match
    """
    if user_id != token_user_id:
        logger.warning(f"User {token_user_id} attempted to access user {user_id}'s chat")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own conversations"
        )


@router.post(
    "/api/{user_id}/chat/sdk",
    response_model=ChatResponse,
    summary="Send chat message to AI assistant (SDK version)",
    description="""
    Send a natural language message to the AI task management assistant.
    This endpoint uses the OpenAI Agents SDK for improved conversation management.

    The assistant can help you:
    - Create tasks: "remind me to buy groceries tomorrow"
    - List tasks: "show me my tasks" or "what's due today"
    - Complete tasks: "mark 'buy groceries' as done"
    - Update tasks: "change the due date to next Monday"
    - Delete tasks: "delete task 'old reminder'"

    Features:
    - Persistent conversation memory via SDK Sessions
    - Improved context understanding across messages
    - Better error handling and retry logic
    """,
    responses={
        200: {
            "description": "Successful response with bot message and task operation details",
            "content": {
                "application/json": {
                    "example": {
                        "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
                        "message": "I've created a task to buy groceries for tomorrow.",
                        "task_operation": {
                            "success": True,
                            "task": {
                                "id": 1,
                                "title": "buy groceries",
                                "due_date": "2026-02-15",
                                "priority": "Medium",
                                "completed": False
                            }
                        }
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User can only access their own conversations"},
        429: {"description": "Rate limit exceeded - Maximum 100 messages per day"},
        500: {"description": "Internal server error"}
    },
    tags=["Chat SDK"]
)
async def send_chat_message_sdk(
    user_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    """
    Send a chat message and get AI response using OpenAI Agents SDK.

    Requires JWT authentication. User can only access their own conversations.

    Args:
        user_id: ID of the user (from URL path)
        request: Chat request with message and optional conversation_id
        session: Database session
        authorization: JWT token from Authorization header

    Returns:
        Chat response with conversation_id, bot message, and task operation details

    Raises:
        HTTPException: 401 if unauthorized, 403 if forbidden, 429 if rate limited
    """
    try:
        # Step 1: Verify JWT token
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        token = authorization.replace("Bearer ", "")
        token_payload = verify_token(token)

        if not token_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        token_user_id = token_payload.get("sub")  # JWT stores user_id in "sub" field

        logger.info(f"Auth Debug - URL user_id: {user_id}, Token user_id (sub): {token_user_id}")
        logger.info(f"Auth Debug - Token payload: {token_payload}")

        if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user information"
            )

        # Convert to int for comparison
        token_user_id = int(token_user_id)

        logger.info(f"Auth Debug - After conversion - URL user_id: {user_id} (type: {type(user_id)}), Token user_id: {token_user_id} (type: {type(token_user_id)})")

        # Step 2: Verify user_id matches token
        verify_user_access(user_id, token_user_id)

        # Step 3: Check rate limit
        rate_limit_service = RateLimitService(session)
        is_allowed, seconds_until_reset = rate_limit_service.check_rate_limit(
            user_id, "/api/chat/sdk"
        )

        if not is_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {seconds_until_reset} seconds.",
                headers={"Retry-After": str(seconds_until_reset)}
            )

        # Step 4: Process chat message with SDK
        chat_service = ChatServiceSDK(session)

        conversation_id = None
        if request.conversation_id:
            try:
                conversation_id = uuid.UUID(request.conversation_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format"
                )

        result = await chat_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=conversation_id
        )

        # Step 5: Return response
        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=result["message"],
            task_operation=result.get("task_operation")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in SDK chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message"
        )


@router.get(
    "/api/{user_id}/chat/sdk/health",
    summary="Check SDK agent health",
    description="Verify that the OpenAI Agents SDK is properly initialized and operational.",
    tags=["Chat SDK"]
)
async def check_sdk_health(
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    """
    Health check endpoint for SDK agent.

    Returns:
        Status information about SDK agent initialization
    """
    try:
        # Verify authentication
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        token = authorization.replace("Bearer ", "")
        token_payload = verify_token(token)

        if not token_payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        # Test SDK agent initialization
        from ..chatbot_agents.sdk_agent import SDKTaskAgent
        from ..mcp.server import mcp_server

        agent = SDKTaskAgent(mcp_server)

        return {
            "status": "healthy",
            "sdk_version": "0.1.0",
            "agent_name": agent.agent.name if hasattr(agent.agent, 'name') else "TaskManagementAgent",
            "model": agent.model,
            "tools_registered": len(agent.agent.tools) if hasattr(agent.agent, 'tools') else 5,
            "timestamp": "2026-02-15T10:30:00Z"
        }

    except Exception as e:
        logger.error(f"SDK health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2026-02-15T10:30:00Z"
        }
