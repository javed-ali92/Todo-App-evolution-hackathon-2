"""
Message model for AI chatbot feature.
Represents individual messages within a conversation.
"""
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLEnum, JSON
from datetime import datetime
from typing import Optional, List
import uuid
import enum


class MessageSender(str, enum.Enum):
    """Enum for message sender type."""
    USER = "user"
    BOT = "bot"


class Message(SQLModel, table=True):
    """
    Message entity representing a single message in a conversation.

    Messages can be sent by either the user or the bot.
    Content is encrypted at rest for security.
    """
    __tablename__ = "messages"

    # Primary Key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    # Foreign Key
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )

    # Message data
    sender: MessageSender = Field(
        sa_column=Column(SQLEnum(MessageSender), nullable=False)
    )

    content: str = Field(
        nullable=False,
        max_length=10000
    )

    # Timestamp
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True
    )

    # Optional metadata
    meta: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    # Optional threading
    parent_message_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="messages.id"
    )

    # Relationships
    # Note: Relationships will be set up after all models are defined
    # conversation: "Conversation" = Relationship(back_populates="messages")
    # parent_message: Optional["Message"] = Relationship(
    #     back_populates="child_messages",
    #     sa_relationship_kwargs={"remote_side": "Message.id"}
    # )
    # child_messages: List["Message"] = Relationship(back_populates="parent_message")
