"""
Chat service for orchestrating chatbot interactions with OpenAI Agents SDK.
Handles message processing, conversation management, and SDK agent execution.
"""
from sqlmodel import Session
from typing import Dict, Any, Optional
import uuid
import logging
from datetime import datetime
from .conversation_service import ConversationService
from .message_service import MessageService
from ..models.message import MessageSender
from ..chatbot_agents.sdk_agent import SDKTaskAgent
from ..mcp.server import mcp_server

logger = logging.getLogger(__name__)


class ChatServiceSDK:
    """
    Chat service using OpenAI Agents SDK.

    Key differences from original:
    - Uses Agent/Runner/Session primitives
    - Persists session state in conversation.meta
    - PostgreSQL remains source of truth for messages
    - Session provides SDK-level memory, DB provides durable history
    """

    def __init__(self, session: Session):
        self.session = session
        self.conversation_service = ConversationService(session)
        self.message_service = MessageService(session)
        self.agent = SDKTaskAgent(mcp_server)

    async def process_message(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[uuid.UUID] = None
    ) -> Dict[str, Any]:
        """
        Process a user message and generate a bot response using SDK.

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

            # Step 2: Extract session state from conversation.meta
            session_state = None
            if conversation.meta and "sdk_session" in conversation.meta:
                session_state = conversation.meta["sdk_session"]
                logger.info(f"Restored SDK session state for conversation {conversation.id}")

            # Step 3: Execute SDK agent with session state
            logger.info(f"Processing message for user {user_id} in conversation {conversation.id}")
            agent_response = await self.agent.process_message(
                user_id=user_id,
                message=message,
                session_state=session_state
            )

            # Step 4: Save user message to PostgreSQL
            self.message_service.create_message(
                conversation_id=conversation.id,
                sender=MessageSender.USER,
                content=message,
                meta=None
            )

            # Step 5: Extract bot response and tool operations
            bot_message = agent_response.get("message", "I'm not sure how to help with that.")
            tool_operations = agent_response.get("tool_operations")
            updated_session_state = agent_response.get("session_state")

            # Step 6: Save bot response to PostgreSQL
            self.message_service.create_message(
                conversation_id=conversation.id,
                sender=MessageSender.BOT,
                content=bot_message,
                meta={
                    "tool_operations": tool_operations
                } if tool_operations else None
            )

            # Step 7: Update conversation with new session state
            self._update_conversation_session(
                conversation.id,
                user_id,
                updated_session_state
            )

            # Step 8: Update conversation timestamp
            self.conversation_service.update_last_message_at(conversation.id, user_id)

            # Step 9: Return response
            return {
                "conversation_id": str(conversation.id),
                "message": bot_message,
                "task_operation": self._extract_primary_operation(tool_operations)
            }

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "conversation_id": str(conversation_id) if conversation_id else None,
                "message": "I'm having trouble processing your request right now. Please try again or use the task dashboard.",
                "task_operation": None,
                "error": str(e)
            }

    def _update_conversation_session(
        self,
        conversation_id: uuid.UUID,
        user_id: int,
        session_state: Optional[Dict[str, Any]]
    ) -> None:
        """
        Update conversation.meta with SDK session state.

        Args:
            conversation_id: UUID of the conversation
            user_id: ID of the user (for ownership verification)
            session_state: Serialized SDK session state
        """
        try:
            conversation = self.conversation_service.get_conversation(
                conversation_id, user_id
            )

            if not conversation:
                logger.error(f"Cannot update session: conversation {conversation_id} not found")
                return

            # Initialize meta if needed
            if conversation.meta is None:
                conversation.meta = {}

            # Store SDK session state
            conversation.meta["sdk_session"] = session_state
            conversation.meta["sdk_session_updated_at"] = datetime.utcnow().isoformat()

            # Persist to database
            conversation.updated_at = datetime.utcnow()
            self.session.add(conversation)
            self.session.commit()

            logger.info(f"Updated SDK session state for conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Error updating conversation session: {str(e)}")

    def _extract_primary_operation(
        self,
        tool_operations: Optional[list]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract the primary tool operation for backward compatibility.

        Args:
            tool_operations: List of tool operations from SDK

        Returns:
            Primary operation dictionary or None
        """
        if not tool_operations or len(tool_operations) == 0:
            return None

        # Return the first operation for backward compatibility
        # In a more sophisticated implementation, you might aggregate results
        return tool_operations[0] if isinstance(tool_operations, list) else tool_operations

    def load_conversation_history(
        self,
        conversation_id: uuid.UUID,
        message_count: int = 10
    ) -> list[Dict[str, str]]:
        """
        Load recent conversation history from PostgreSQL.

        Note: With SDK Sessions, this is primarily for display purposes.
        The SDK maintains its own conversation context in session state.

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

            # Format for display
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
