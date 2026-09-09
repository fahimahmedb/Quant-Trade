"""IA-1 F11 : comptage tournant — flag, intervalle, forçage de session

Revision ID: 3c8f1a92e4d6
Revises: 9d24e6a1f7b8
Create Date: 2026-09-09 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c8f1a92e4d6'
down_revision: Union[str, None] = '9d24e6a1f7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f11_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('full_count_interval_days', sa.Float(), nullable=False, server_default='28.0')
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f11_enabled', server_default=None)
        batch_op.alter_column('full_count_interval_days', server_default=None)

    op.create_table(
        'daily_session_overrides',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('include', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ingredient_id'),
    )


def downgrade() -> None:
    op.drop_table('daily_session_overrides')

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('full_count_interval_days')
        batch_op.drop_column('feature_f11_enabled')
