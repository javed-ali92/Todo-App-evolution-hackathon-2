"""
Message service for managing chat messages.
Handles CRUD operations for messages with encryption.
"""
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
import os
import logging
from cryptography.fernet import Fernet
from ..models.message import Message, MessageSender

logger = logging.getLogger(__name__)


class MessageService:
    """Service for managing chat messages with encryption."""

    def __init__(self, session: Session):
        self.session = session

        # Initialize encryption
        encryption_key = os.getenv("CONVERSATION_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError("CONVERSATION_ENCRYPTION_KEY environment variable not set")

        self.cipher = Fernet(encryption_key.encode())

    def encrypt_content(self, content: str) -> str:
        """
        Encrypt message content using Fernet symmetric encryption.

        Args:
            content: Plain text message content

        Returns:
            Encrypted content as string
        """
        try:
            encrypted = self.cipher.encrypt(content.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"Error encrypting content: {str(e)}")
            raise

    def decrypt_content(self, encrypted_content: str) -> str:
        """
        Decrypt message content.

        Args:
            encrypted_content: Encrypted message content

        Returns:
            Decrypted plain text content
        """
        try:
            decrypted = self.cipher.decrypt(encrypted_content.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Error decrypting content: {str(e)}")
            raise

    def create_message(
        self,
        conversation_id: uuid.UUID,
        sender: MessageSender,
        content: str,
        meta: Optional[dict] = None,
        parent_message_id: Optional[uuid.UUID] = None
    ) -> Message:
        """
        Create a new message in a conversation.

        Args:
            conversation_id: UUID of the conversation
            sender: Message sender (user or bot)
            content: Message content (will be encrypted)
            meta: Optional metadata dictionary
            parent_message_id: Optional parent message for threading

        Returns:
            Created message (with decrypted content)
        """
        # Encrypt content before storing
        encrypted_content = self.encrypt_content(content)

        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            sender=sender,
            content=encrypted_content,
            created_at=datetime.utcnow(),
            meta=meta,
            parent_message_id=parent_message_id
        )

        self.session.add(message)
        self.session.commit()
        self.session.refresh(message)

        # Decrypt content for return
        message.content = self.decrypt_content(message.content)

        logger.info(f"Created message {message.id} in conversation {conversation_id}")
        return message

    def get_messages(
        self,
        conversation_id: uuid.UUID,
        limit: int = 50,
        before: Optional[datetime] = None
    ) -> List[Message]:
        """
        Get messages from a conversation, ordered chronologically.

        Args:
            conversation_id: UUID of the conversation
            limit: Maximum number of messages to return
            before: Optional timestamp to get messages before (for pagination)

        Returns:
            List of messages (with decrypted content)
        """
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        if before:
            statement = statement.where(Message.created_at < before)

        messages = self.session.exec(statement).all()

        # Decrypt all message content
        for message in messages:
            try:
                message.content = self.decrypt_content(message.content)
            except Exception as e:
                logger.error(f"Failed to decrypt message {message.id}: {str(e)}")
                message.content = "[Decryption failed]"

        # Reverse to get chronological order (oldest first)
        messages.reverse()

        logger.info(f"Retrieved {len(messages)} messages from conversation {conversation_id}")
        return messages

    def get_recent_messages(
        self,
        conversation_id: uuid.UUID,
        count: int = 10
    ) -> List[Message]:
        """
        Get the most recent N messages from a conversation.

        Args:
            conversation_id: UUID of the conversation
            count: Number of recent messages to retrieve

        Returns:
            List of recent messages in chronological order (with decrypted content)
        """
        return self.get_messages(conversation_id, limit=count)

    def format_for_agent(self, messages: List[Message]) -> List[dict]:
        """
        Format messages for agent context.

        Args:
            messages: List of messages

        Returns:
            List of message dictionaries with role and content
        """
        formatted = []
        for message in messages:
            role = "user" if message.sender == MessageSender.USER else "assistant"
            formatted.append({
                "role": role,
                "content": message.content
            })
        return formatted
