"""Create rate_limits table

Revision ID: 64f499085532
Revises: 55c40cfa8679
Create Date: 2026-02-14 01:47:09.850025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '64f499085532'
down_revision: Union[str, None] = '55c40cfa8679'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create rate_limits table
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

    # Create index for cleanup queries
    op.create_index('idx_rate_limits_reset_at', 'rate_limits', ['reset_at'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_rate_limits_reset_at')

    # Drop table
    op.drop_table('rate_limits')

