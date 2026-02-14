"""
Chat service for orchestrating chatbot interactions.
Handles message processing, conversation management, and agent execution.
"""
from sqlmodel import Session
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime
from .conversation_service import ConversationService
from .message_service import MessageService
from ..models.message import MessageSender
from ..agents.task_agent import TaskAgent
from ..mcp.server import mcp_server

logger = logging.getLogger(__name__)


class ChatService:
    """
    Main service for chat operations.

    Orchestrates conversation management, message persistence,
    and agent execution.
    """

    def __init__(self, session: Session):
        self.session = session
        self.conversation_service = ConversationService(session)
        self.message_service = MessageService(session)
        self.agent = TaskAgent(mcp_server)

    def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a bot response.

        This is the main entry point for chat interactions.

        Args:
            user_id: ID of the authenticated user
            message: User's message text
            conversation_id: Optional existing conversation ID

        Returns:
            Dictionary with conversation_id, bot message, and task_operation details
        """
        try:
            # Step 1: Get or create conversation
            if conversation_id:
                conversation = self.conversation_service.get_conversation(
                    conversation_id, user_id
                )
                if not conversation:
                    logger.warning(f"Conversation {conversation_id} not found, creating new one")
                    conversation = self.conversation_service.create_conversation(user_id)
            else:
                conversation = self.conversation_service.create_conversation(user_id)

            # Step 2: Load conversation history for context
            conversation_history = self.load_conversation_history(conversation.id)

            # Step 3: Set user context in MCP server
            mcp_server.set_user_context(user_id)

            # Step 4: Execute agent with conversation context
            logger.info(f"Processing message for user {user_id} in conversation {conversation.id}")
            agent_response = self.agent.process_message(message, conversation_history)

            # Step 5: Save user message
            self.message_service.create_message(
                conversation_id=conversation.id,
                sender=MessageSender.USER,
                content=message,
                meta=None
            )

            # Step 6: Save bot response
            bot_message = agent_response.get("message", "I'm not sure how to help with that.")
            task_operation = agent_response.get("task_operation")

            self.message_service.create_message(
                conversation_id=conversation.id,
                sender=MessageSender.BOT,
                content=bot_message,
                meta={
                    "task_operation": task_operation
                } if task_operation else None
            )

            # Step 7: Update conversation timestamp
            self.conversation_service.update_last_message_at(conversation.id, user_id)

            # Step 8: Return response
            return {
                "conversation_id": str(conversation.id),
                "message": bot_message,
                "task_operation": task_operation
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "conversation_id": str(conversation_id) if conversation_id else None,
                "message": "I'm having trouble processing your request right now. Please try again or use the task dashboard.",
                "task_operation": None,
                "error": str(e)
            }

    def load_conversation_history(
        self,
        conversation_id: uuid.UUID,
        message_count: int = 10
    ) -> list[Dict[str, str]]:
        """
        Load recent conversation history for agent context.

        Args:
            conversation_id: UUID of the conversation
            message_count: Number of recent messages to load (default: 10)

        Returns:
            List of message dictionaries with role and content
        """
        try:
            messages = self.message_service.get_recent_messages(
                conversation_id,
                count=message_count
            )

            # Format for agent
            return self.message_service.format_for_agent(messages)

        except Exception as e:
            logger.error(f"Error loading conversation history: {str(e)}")
            return []

    def get_conversation_messages(
        self,
        conversation_id: uuid.UUID,
        user_id: int,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get messages from a conversation for display.

        Args:
            conversation_id: UUID of the conversation
            user_id: ID of the user (for ownership verification)
            limit: Maximum number of messages to return
            before: Optional timestamp for pagination

        Returns:
            Dictionary with messages and pagination info
        """
        try:
            # Verify conversation ownership
            conversation = self.conversation_service.get_conversation(
                conversation_id, user_id
            )

            if not conversation:
                return {
                    "success": False,
                    "error": "Conversation not found"
                }

            # Get messages
            messages = self.message_service.get_messages(
                conversation_id, limit, before
            )

            # Format for response
            message_list = []
            for msg in messages:
                message_list.append({
                    "id": str(msg.id),
                    "sender": msg.sender.value,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                    "meta": msg.meta
                })

            return {
                "success": True,
                "messages": message_list,
                "has_more": len(messages) == limit
            }

        except Exception as e:
            logger.error(f"Error getting conversation messages: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def list_user_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List conversations for a user.

        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip

        Returns:
            Dictionary with conversations and pagination info
        """
        try:
            conversations = self.conversation_service.list_conversations(
                user_id, limit, offset
            )

            # Format for response
            conversation_list = []
            for conv in conversations:
                # Get message count and preview
                messages = self.message_service.get_recent_messages(conv.id, count=1)
                preview = messages[0].content if messages else None

                conversation_list.append({
                    "id": str(conv.id),
                    "created_at": conv.created_at.isoformat(),
                    "last_message_at": conv.last_message_at.isoformat(),
                    "preview": preview[:100] if preview else None
                })

            return {
                "success": True,
                "conversations": conversation_list,
                "total": len(conversation_list)
            }

        except Exception as e:
            logger.error(f"Error listing conversations: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
