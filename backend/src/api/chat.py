"""
Chat API endpoints for AI chatbot.
Handles chat message processing and conversation management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlmodel import Session
from typing import Optional
from pydantic import BaseModel, Field
import uuid
import logging
from ..database.database import engine
from ..services.chat_service import ChatService
from ..services.rate_limit_service import RateLimitService
from ..auth.jwt_handler import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: str
    message: str
    task_operation: Optional[dict] = None


class ConversationListResponse(BaseModel):
    """Response model for listing conversations."""
    conversations: list[dict]
    total: int
    limit: int
    offset: int


class MessageListResponse(BaseModel):
    """Response model for listing messages."""
    messages: list[dict]
    has_more: bool


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
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    summary="Send chat message to AI assistant",
    description="""
    Send a natural language message to the AI task management assistant.

    The assistant can help you:
    - Create tasks: "remind me to buy groceries tomorrow"
    - List tasks: "show me my tasks" or "what's due today"
    - Complete tasks: "mark 'buy groceries' as done"
    - Update tasks: "change the due date to next Monday"
    - Delete tasks: "delete task 'old reminder'"

    Conversations are persistent - the assistant remembers context from previous messages
    in the same conversation.
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
    tags=["Chat"]
)
async def send_chat_message(
    user_id: int,
    request: ChatRequest,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    """
    Send a chat message and get AI response.

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
        # Step 1: Log incoming request
        logger.info(f"[CHAT_REQUEST] user_id={user_id}, message_length={len(request.message)}, conversation_id={request.conversation_id}")
        logger.debug(f"[CHAT_REQUEST_BODY] {request.model_dump()}")

        # Step 2: Verify JWT token
        if not authorization or not authorization.startswith("Bearer "):
            logger.warning(f"[AUTH_FAILED] Missing or invalid authorization header for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header"
            )

        token = authorization.replace("Bearer ", "")
        token_payload = verify_token(token)

        if not token_payload:
            logger.warning(f"[AUTH_FAILED] Invalid or expired token for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )

        token_user_id = token_payload.get("sub")  # JWT stores user_id in "sub" field

        if not token_user_id:
            logger.error(f"[AUTH_FAILED] Token missing user information for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user information"
            )

        # Convert to int for comparison
        token_user_id = int(token_user_id)
        logger.debug(f"[AUTH_SUCCESS] user_id={user_id}, token_user_id={token_user_id}")

        # Step 3: Verify user_id matches token
        verify_user_access(user_id, token_user_id)
        logger.debug(f"[ACCESS_GRANTED] User {user_id} authorized")

        # Step 4: Check rate limit
        logger.debug(f"[RATE_LIMIT_CHECK] Checking rate limit for user {user_id}")
        rate_limit_service = RateLimitService(session)
        is_allowed, seconds_until_reset = rate_limit_service.check_rate_limit(
            user_id, "/api/chat"
        )

        if not is_allowed:
            logger.warning(f"[RATE_LIMIT_EXCEEDED] User {user_id} exceeded rate limit, retry in {seconds_until_reset}s")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {seconds_until_reset} seconds.",
                headers={"Retry-After": str(seconds_until_reset)}
            )

        logger.debug(f"[RATE_LIMIT_OK] User {user_id} within rate limit")

        # Step 5: Process chat message
        logger.info(f"[CHAT_PROCESSING] Starting message processing for user {user_id}")
        chat_service = ChatService(session)

        conversation_id = None
        if request.conversation_id:
            try:
                conversation_id = uuid.UUID(request.conversation_id)
                logger.debug(f"[CONVERSATION] Using existing conversation {conversation_id}")
            except ValueError:
                logger.error(f"[CONVERSATION_ERROR] Invalid conversation_id format: {request.conversation_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid conversation_id format"
                )

        result = chat_service.process_message(
            user_id=user_id,
            message=request.message,
            conversation_id=conversation_id
        )

        logger.debug(f"[CHAT_RESULT] result_keys={list(result.keys())}, has_error={'error' in result}")

        # Step 6: Check for errors in result
        if "error" in result or result.get("conversation_id") is None:
            # API error occurred, log details and return user-friendly error message
            error_message = result.get("message", "An error occurred processing your message")
            error_details = result.get("error", "Unknown error")
            logger.error(f"[CHAT_ERROR] user_id={user_id}, error={error_details}, message={error_message}")

            # Check if it's a quota error
            if "429" in str(error_details) or "quota" in str(error_details).lower():
                logger.error(f"[API_QUOTA_EXCEEDED] Gemini API quota exhausted")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service temporarily unavailable due to quota limits. Please try again later."
                )

            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_message
            )

        # Step 7: Return successful response
        logger.info(f"[CHAT_SUCCESS] user_id={user_id}, conversation_id={result['conversation_id']}")
        logger.debug(f"[CHAT_RESPONSE] message_length={len(result['message'])}, has_task_operation={result.get('task_operation') is not None}")

        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=result["message"],
            task_operation=result.get("task_operation")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred processing your message"
        )


@router.get(
    "/api/{user_id}/conversations",
    response_model=ConversationListResponse,
    summary="List user's conversations",
    description="Retrieve a paginated list of the authenticated user's chat conversations, ordered by most recent activity.",
    responses={
        200: {
            "description": "Successful response with conversations list",
            "content": {
                "application/json": {
                    "example": {
                        "conversations": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "created_at": "2026-02-14T10:30:00Z",
                                "last_message_at": "2026-02-14T11:45:00Z",
                                "message_count": 12
                            }
                        ],
                        "total": 5,
                        "limit": 20,
                        "offset": 0
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User can only access their own conversations"}
    },
    tags=["Chat"]
)
async def list_conversations(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    """
    List user's conversations.

    Requires JWT authentication.

    Args:
        user_id: ID of the user
        limit: Maximum number of conversations to return (default: 20, max: 100)
        offset: Number of conversations to skip (default: 0)
        session: Database session
        authorization: JWT token from Authorization header

    Returns:
        List of conversations with pagination info

    Raises:
        HTTPException: 401 if unauthorized, 403 if forbidden
    """
    try:
        # Verify JWT token
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

        if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user information"
            )

        # Convert to int for comparison
        token_user_id = int(token_user_id)
        verify_user_access(user_id, token_user_id)

        # Validate parameters
        if limit < 1 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Offset must be non-negative"
            )

        # Get conversations
        chat_service = ChatService(session)
        result = chat_service.list_user_conversations(user_id, limit, offset)

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to list conversations")
            )

        return ConversationListResponse(
            conversations=result["conversations"],
            total=result["total"],
            limit=limit,
            offset=offset
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing conversations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred listing conversations"
        )


@router.get(
    "/api/{user_id}/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    summary="Get conversation messages",
    description="Retrieve messages from a specific conversation, ordered chronologically. Returns up to 200 messages per request.",
    responses={
        200: {
            "description": "Successful response with messages list",
            "content": {
                "application/json": {
                    "example": {
                        "messages": [
                            {
                                "id": "msg-123",
                                "sender": "user",
                                "content": "remind me to buy groceries tomorrow",
                                "created_at": "2026-02-14T10:30:00Z"
                            },
                            {
                                "id": "msg-124",
                                "sender": "bot",
                                "content": "I've created a task to buy groceries for tomorrow.",
                                "created_at": "2026-02-14T10:30:05Z",
                                "task_operation": {"success": True}
                            }
                        ],
                        "has_more": False
                    }
                }
            }
        },
        401: {"description": "Unauthorized - Invalid or missing JWT token"},
        403: {"description": "Forbidden - User can only access their own conversations"},
        404: {"description": "Conversation not found"}
    },
    tags=["Chat"]
)
async def get_conversation_messages(
    user_id: int,
    conversation_id: str,
    limit: int = 50,
    session: Session = Depends(get_session),
    authorization: Optional[str] = Header(None)
):
    """
    Get messages from a conversation.

    Requires JWT authentication.

    Args:
        user_id: ID of the user
        conversation_id: UUID of the conversation
        limit: Maximum number of messages to return (default: 50, max: 200)
        session: Database session
        authorization: JWT token from Authorization header

    Returns:
        List of messages with pagination info

    Raises:
        HTTPException: 401 if unauthorized, 403 if forbidden, 404 if not found
    """
    try:
        # Verify JWT token
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

        if not token_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user information"
            )

        # Convert to int for comparison
        token_user_id = int(token_user_id)
        verify_user_access(user_id, token_user_id)

        # Validate conversation_id
        try:
            conv_uuid = uuid.UUID(conversation_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid conversation_id format"
            )

        # Validate limit
        if limit < 1 or limit > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 200"
            )

        # Get messages
        chat_service = ChatService(session)
        result = chat_service.get_conversation_messages(conv_uuid, user_id, limit)

        if not result.get("success"):
            if "not found" in result.get("error", "").lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to get messages")
            )

        return MessageListResponse(
            messages=result["messages"],
            has_more=result["has_more"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation messages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred getting messages"
        )
