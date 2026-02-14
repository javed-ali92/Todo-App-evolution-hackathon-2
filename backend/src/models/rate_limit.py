"""
RateLimit model for AI chatbot feature.
Tracks API rate limits per user to prevent abuse.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime


class RateLimit(SQLModel, table=True):
    """
    RateLimit entity for tracking API usage per user.

    Uses composite primary key (user_id, endpoint) to track
    rate limits separately for different endpoints.
    """
    __tablename__ = "rate_limits"

    # Composite primary key
    user_id: int = Field(
        foreign_key="user.id",
        primary_key=True,
        nullable=False
    )

    endpoint: str = Field(
        primary_key=True,
        nullable=False,
        max_length=100
    )

    # Rate limit data
    count: int = Field(
        default=0,
        nullable=False
    )

    reset_at: datetime = Field(
        nullable=False
    )

    # Timestamp
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
