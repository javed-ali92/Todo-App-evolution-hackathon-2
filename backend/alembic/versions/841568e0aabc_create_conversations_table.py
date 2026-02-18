"""Create conversations table

Revision ID: 841568e0aabc
Revises:
Create Date: 2026-02-14 01:44:49.120720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '841568e0aabc'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=False),
        sa.Column('meta', postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for performance
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('idx_conversations_last_message_at', 'conversations', ['last_message_at'],
                    postgresql_ops={'last_message_at': 'DESC'})
    op.create_index('idx_conversations_user_activity', 'conversations', ['user_id', 'last_message_at'],
                    postgresql_ops={'last_message_at': 'DESC'})


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_conversations_user_activity')
    op.drop_index('idx_conversations_last_message_at')
    op.drop_index('idx_conversations_user_id')

    # Drop table
    op.drop_table('conversations')

