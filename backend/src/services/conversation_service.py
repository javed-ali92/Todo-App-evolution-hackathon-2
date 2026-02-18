"""
Conversation service for managing chat conversations.
Handles CRUD operations for conversations.
"""
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
import os
import logging
from ..models.conversation import Conversation

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing chat conversations."""

    def __init__(self, session: Session):
        self.session = session

    def create_conversation(self, user_id: int, meta: Optional[dict] = None) -> Conversation:
        """
        Create a new conversation for a user.

        Args:
            user_id: ID of the user
            meta: Optional metadata dictionary

        Returns:
            Created conversation
        """
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_message_at=datetime.utcnow(),
            meta=meta
        )

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation

    def get_conversation(
        self,
        conversation_id: uuid.UUID,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID, verifying user ownership.

        Args:
            conversation_id: UUID of the conversation
            user_id: ID of the user (for ownership verification)

        Returns:
            Conversation if found and owned by user, None otherwise
        """
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.session.exec(statement).first()

        if not conversation:
            logger.warning(f"Conversation {conversation_id} not found for user {user_id}")

        return conversation

    def list_conversations(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> List[Conversation]:
        """
        List conversations for a user, ordered by most recent activity.

        Args:
            user_id: ID of the user
            limit: Maximum number of conversations to return
            offset: Number of conversations to skip (for pagination)

        Returns:
            List of conversations
        """
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.last_message_at.desc())
            .limit(limit)
            .offset(offset)
        )

        conversations = self.session.exec(statement).all()
        logger.info(f"Listed {len(conversations)} conversations for user {user_id}")

        return conversations

    def update_last_message_at(
        self,
        conversation_id: uuid.UUID,
        user_id: int
    ) -> Optional[Conversation]:
        """
        Update the last_message_at timestamp for a conversation.

        Args:
            conversation_id: UUID of the conversation
            user_id: ID of the user (for ownership verification)

        Returns:
            Updated conversation if found, None otherwise
        """
        conversation = self.get_conversation(conversation_id, user_id)

        if not conversation:
            return None

        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return conversation

    def archive_old_conversations(self) -> int:
        """
        Archive conversations inactive for more than CONVERSATION_RETENTION_DAYS.

        This is a background task that should run periodically.

        Returns:
            Number of conversations archived
        """
        retention_days = int(os.getenv("CONVERSATION_RETENTION_DAYS", "30"))
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        statement = select(Conversation).where(
            Conversation.last_message_at < cutoff_date
        )

        old_conversations = self.session.exec(statement).all()

        archived_count = 0
        for conv in old_conversations:
            # Soft delete: mark as archived in metadata
            if conv.meta is None:
                conv.meta = {}
            conv.meta['archived'] = True
            conv.meta['archived_at'] = datetime.utcnow().isoformat()
            self.session.add(conv)
            archived_count += 1

        self.session.commit()

        logger.info(f"Archived {archived_count} old conversations")
        return archived_count
