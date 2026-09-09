"""IA-2 F23 : estimation initiale du chef sur un plat, feature flag et constante de lissage

Revision ID: e1a4c9f7d3b2
Revises: d4f9b3e7c2a8
Create Date: 2026-09-09 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a4c9f7d3b2'
down_revision: Union[str, None] = 'd4f9b3e7c2a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('dishes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('initial_daily_estimate', sa.Float(), nullable=True))

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f23_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('cold_start_smoothing_days', sa.Float(), nullable=False, server_default='14.0')
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f23_enabled', server_default=None)
        batch_op.alter_column('cold_start_smoothing_days', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('cold_start_smoothing_days')
        batch_op.drop_column('feature_f23_enabled')

    with op.batch_alter_table('dishes', schema=None) as batch_op:
        batch_op.drop_column('initial_daily_estimate')
