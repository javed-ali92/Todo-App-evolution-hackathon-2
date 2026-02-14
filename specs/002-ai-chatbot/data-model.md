# Data Model: AI Chatbot

**Feature**: AI Chatbot for Task Management
**Branch**: 002-ai-chatbot
**Date**: 2026-02-13

This document defines the database schema and data models for the chatbot feature.

---

## Overview

The chatbot feature introduces two new entities:
1. **Conversation**: Represents a chat session between a user and the AI assistant
2. **Message**: Represents individual messages within a conversation

These entities integrate with existing User and Task entities without modifying them.

---

## Entity Relationship Diagram

```text
User (existing)
  ├── 1:N → Conversation (new)
  │         ├── 1:N → Message (new)
  │         └── metadata: JSON
  └── 1:N → Task (existing, no changes)

RateLimit (new)
  └── N:1 → User
```

---

## 1. Conversation Entity

### Purpose
Represents a chat session between a user and the AI chatbot. Each conversation maintains its own context and history.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
import uuid

class Conversation(SQLModel, table=True):
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
        foreign_key="users.id",
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

    # Optional metadata
    metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

### Database Schema (PostgreSQL)

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB
);

-- Indexes for performance
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_last_message_at ON conversations(last_message_at DESC);
CREATE INDEX idx_conversations_user_activity ON conversations(user_id, last_message_at DESC);
```

### Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Unique conversation identifier | Primary key, auto-generated |
| user_id | Integer | Owner of the conversation | Foreign key to users.id, NOT NULL |
| created_at | DateTime | When conversation was created | NOT NULL, defaults to current time |
| updated_at | DateTime | Last time conversation was modified | NOT NULL, auto-updated |
| last_message_at | DateTime | Timestamp of most recent message | NOT NULL, indexed for sorting |
| metadata | JSON | Optional conversation metadata | Nullable, stores title, tags, etc. |

### Validation Rules

1. **user_id**: Must reference an existing user in the users table
2. **created_at**: Cannot be in the future
3. **last_message_at**: Must be >= created_at
4. **updated_at**: Must be >= created_at

### State Transitions

```text
[Created] → [Active] → [Archived]
    ↓          ↓           ↓
  New      Has messages  30+ days inactive
```

### Business Rules

1. A user can have multiple conversations
2. Conversations are soft-deleted (archived) after 30 days of inactivity
3. Deleting a user cascades to delete all their conversations
4. Deleting a conversation cascades to delete all its messages

---

## 2. Message Entity

### Purpose
Represents a single message in a conversation, sent by either the user or the AI bot.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLEnum
from datetime import datetime
from typing import Optional
import uuid
import enum

class MessageSender(str, enum.Enum):
    USER = "user"
    BOT = "bot"

class Message(SQLModel, table=True):
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
        sa_column=Column(SQLEnum(MessageSender)),
        nullable=False
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
    metadata: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON)
    )

    # Optional threading
    parent_message_id: Optional[uuid.UUID] = Field(
        default=None,
        foreign_key="messages.id"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
    parent_message: Optional["Message"] = Relationship(
        back_populates="child_messages",
        sa_relationship_kwargs={"remote_side": "Message.id"}
    )
    child_messages: List["Message"] = Relationship(back_populates="parent_message")
```

### Database Schema (PostgreSQL)

```sql
CREATE TYPE message_sender AS ENUM ('user', 'bot');

CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender message_sender NOT NULL,
    content TEXT NOT NULL CHECK (length(content) > 0 AND length(content) <= 10000),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    metadata JSONB,
    parent_message_id UUID REFERENCES messages(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_messages_conversation_time ON messages(conversation_id, created_at);
CREATE INDEX idx_messages_parent ON messages(parent_message_id) WHERE parent_message_id IS NOT NULL;
```

### Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Unique message identifier | Primary key, auto-generated |
| conversation_id | UUID | Parent conversation | Foreign key to conversations.id, NOT NULL |
| sender | Enum | Who sent the message | 'user' or 'bot', NOT NULL |
| content | Text | Message content (encrypted) | NOT NULL, 1-10000 characters |
| created_at | DateTime | When message was sent | NOT NULL, indexed |
| metadata | JSON | Optional message metadata | Nullable, stores intent, task_operation, etc. |
| parent_message_id | UUID | Parent message for threading | Nullable, self-referential FK |

### Validation Rules

1. **conversation_id**: Must reference an existing conversation
2. **sender**: Must be either 'user' or 'bot'
3. **content**: Cannot be empty, max 10,000 characters
4. **created_at**: Cannot be in the future
5. **parent_message_id**: If set, must reference an existing message in the same conversation

### Metadata Schema

The `metadata` JSON field can contain:

```json
{
  "intent": "create_task",
  "confidence": 0.95,
  "task_operation": {
    "action": "create",
    "task_id": 123,
    "success": true
  },
  "processing_time_ms": 1250,
  "model_used": "gpt-4-turbo-preview"
}
```

### Business Rules

1. Messages are immutable once created (no updates)
2. Messages are ordered chronologically within a conversation
3. Deleting a conversation cascades to delete all messages
4. Message content is encrypted at rest using Fernet encryption
5. Parent message must belong to the same conversation

---

## 3. RateLimit Entity (Supporting Table)

### Purpose
Tracks API rate limits per user to prevent abuse.

### SQLModel Definition

```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class RateLimit(SQLModel, table=True):
    __tablename__ = "rate_limits"

    # Composite primary key
    user_id: int = Field(
        foreign_key="users.id",
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
```

### Database Schema (PostgreSQL)

```sql
CREATE TABLE rate_limits (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(100) NOT NULL,
    count INTEGER NOT NULL DEFAULT 0,
    reset_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, endpoint)
);

-- Index for cleanup queries
CREATE INDEX idx_rate_limits_reset_at ON rate_limits(reset_at);
```

### Field Descriptions

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| user_id | Integer | User being rate limited | Part of composite PK, FK to users.id |
| endpoint | String | API endpoint path | Part of composite PK, max 100 chars |
| count | Integer | Number of requests made | NOT NULL, default 0 |
| reset_at | DateTime | When the counter resets | NOT NULL |
| updated_at | DateTime | Last update timestamp | NOT NULL |

### Business Rules

1. Counter increments on each API call
2. Counter resets to 0 when current time > reset_at
3. Expired rate limit records are cleaned up daily
4. Default limit: 100 messages per day per user

---

## 4. Database Migrations

### Migration 1: Create Conversations Table

```python
# alembic/versions/xxx_create_conversations_table.py

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_last_message_at', 'conversations', ['last_message_at'], postgresql_ops={'last_message_at': 'DESC'})
    op.create_index('idx_conversations_user_activity', 'conversations', ['user_id', 'last_message_at'], postgresql_ops={'last_message_at': 'DESC'})

def downgrade():
    op.drop_index('idx_conversations_user_activity')
    op.drop_index('idx_conversations_last_message_at')
    op.drop_index('idx_conversations_user_id')
    op.drop_table('conversations')
```

### Migration 2: Create Messages Table

```python
# alembic/versions/xxx_create_messages_table.py

def upgrade():
    # Create enum type
    message_sender = postgresql.ENUM('user', 'bot', name='message_sender')
    message_sender.create(op.get_bind())

    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender', message_sender, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.CheckConstraint('length(content) > 0 AND length(content) <= 10000', name='check_content_length')
    )

    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    op.create_index('idx_messages_conversation_time', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_parent', 'messages', ['parent_message_id'], postgresql_where=sa.text('parent_message_id IS NOT NULL'))

def downgrade():
    op.drop_index('idx_messages_parent')
    op.drop_index('idx_messages_conversation_time')
    op.drop_index('idx_messages_created_at')
    op.drop_index('idx_messages_conversation_id')
    op.drop_table('messages')

    message_sender = postgresql.ENUM('user', 'bot', name='message_sender')
    message_sender.drop(op.get_bind())
```

### Migration 3: Create RateLimits Table

```python
# alembic/versions/xxx_create_rate_limits_table.py

def upgrade():
    op.create_table(
        'rate_limits',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(100), nullable=False),
        sa.Column('count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('reset_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'endpoint')
    )

    op.create_index('idx_rate_limits_reset_at', 'rate_limits', ['reset_at'])

def downgrade():
    op.drop_index('idx_rate_limits_reset_at')
    op.drop_table('rate_limits')
```

---

## 5. Query Patterns

### Load Recent Conversation History

```python
# Get last 10 messages for a conversation
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(10)
).all()

# Reverse to get chronological order (oldest first)
messages.reverse()
```

### List User's Conversations

```python
# Get user's conversations ordered by activity
conversations = session.exec(
    select(Conversation)
    .where(Conversation.user_id == user_id)
    .order_by(Conversation.last_message_at.desc())
    .limit(20)
).all()
```

### Check Rate Limit

```python
# Get or create rate limit record
rate_limit = session.exec(
    select(RateLimit)
    .where(
        RateLimit.user_id == user_id,
        RateLimit.endpoint == "/api/chat"
    )
).first()

if rate_limit and rate_limit.reset_at > datetime.utcnow():
    if rate_limit.count >= 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
```

---

## 6. Data Retention Policy

### Conversation Archival

Conversations inactive for 30+ days are archived:

```python
# Background task (runs daily)
def archive_old_conversations():
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    old_conversations = session.exec(
        select(Conversation)
        .where(Conversation.last_message_at < cutoff_date)
    ).all()

    for conv in old_conversations:
        # Soft delete: mark as archived in metadata
        conv.metadata = conv.metadata or {}
        conv.metadata['archived'] = True
        conv.metadata['archived_at'] = datetime.utcnow().isoformat()
        session.add(conv)

    session.commit()
```

### Rate Limit Cleanup

Expired rate limit records are cleaned up:

```python
# Background task (runs daily)
def cleanup_expired_rate_limits():
    session.exec(
        delete(RateLimit)
        .where(RateLimit.reset_at < datetime.utcnow())
    )
    session.commit()
```

---

## 7. Security Considerations

### Encryption

Message content is encrypted using Fernet symmetric encryption:

```python
from cryptography.fernet import Fernet
import os

# Initialize cipher
encryption_key = os.getenv("CONVERSATION_ENCRYPTION_KEY")
cipher = Fernet(encryption_key.encode())

# Encrypt before storing
encrypted_content = cipher.encrypt(message_content.encode()).decode()

# Decrypt when loading
decrypted_content = cipher.decrypt(encrypted_content.encode()).decode()
```

### Access Control

All queries must enforce user ownership:

```python
# CORRECT: Verify user owns conversation
conversation = session.exec(
    select(Conversation)
    .where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id  # Enforce ownership
    )
).first()

# INCORRECT: Missing ownership check
conversation = session.exec(
    select(Conversation)
    .where(Conversation.id == conversation_id)
).first()
```

---

## Summary

### New Tables
1. **conversations**: 5 columns, 3 indexes
2. **messages**: 7 columns, 4 indexes
3. **rate_limits**: 5 columns, 1 index

### Relationships
- User → Conversations (1:N)
- Conversation → Messages (1:N)
- Message → Message (1:N, self-referential for threading)
- User → RateLimits (1:N)

### Storage Estimates
- Conversation: ~200 bytes per record
- Message: ~500 bytes per record (encrypted)
- RateLimit: ~100 bytes per record

For 1000 users with avg 10 conversations and 50 messages each:
- Conversations: 10,000 records × 200 bytes = 2 MB
- Messages: 500,000 records × 500 bytes = 250 MB
- Rate Limits: 1,000 records × 100 bytes = 100 KB

**Total: ~252 MB** (well within PostgreSQL capacity)
