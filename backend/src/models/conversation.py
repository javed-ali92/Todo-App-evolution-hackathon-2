"""
Conversation model for AI chatbot feature.
Represents a chat session between a user and the AI assistant.
"""
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from datetime import datetime
from typing import Optional, List
import uuid


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    Each conversation belongs to one user and contains multiple messages.
    Tracks conversation metadata and activity timestamps.
    """
    __tablename__ = "conversations"

    # Primary Key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False
    )

    # Foreign Key
    user_id: int = Field(
        foreign_key="user.id",
        nullable=False,
        index=True
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    last_message_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True  # For sorting by activity
    )

    # Optional metadata (stores OpenAI thread_id and assistant_id)
    meta: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    # Relationships
    # Note: Relationships will be set up after all models are defined
    # user: "User" = Relationship(back_populates="conversations")
    # messages: List["Message"] = Relationship(
    #     back_populates="conversation",
    #     sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    # )
