"""Create messages table

Revision ID: 55c40cfa8679
Revises: 841568e0aabc
Create Date: 2026-02-14 01:45:47.111501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '55c40cfa8679'
down_revision: Union[str, None] = '841568e0aabc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for message sender
    message_sender = postgresql.ENUM('user', 'bot', name='messagesender')
    message_sender.create(op.get_bind())

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sender', message_sender, nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('meta', postgresql.JSONB(), nullable=True),
        sa.Column('parent_message_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.CheckConstraint('length(content) > 0 AND length(content) <= 10000', name='check_content_length')
    )

    # Create indexes for performance
    op.create_index('idx_messages_conversation_id', 'messages', ['conversation_id'])
    op.create_index('idx_messages_created_at', 'messages', ['created_at'])
    op.create_index('idx_messages_conversation_time', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_parent', 'messages', ['parent_message_id'],
                    postgresql_where=sa.text('parent_message_id IS NOT NULL'))


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_messages_parent')
    op.drop_index('idx_messages_conversation_time')
    op.drop_index('idx_messages_created_at')
    op.drop_index('idx_messages_conversation_id')

    # Drop table
    op.drop_table('messages')

    # Drop enum type
    message_sender = postgresql.ENUM('user', 'bot', name='messagesender')
    message_sender.drop(op.get_bind())

