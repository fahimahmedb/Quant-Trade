"""IA-2 F22 : feature flag et fenêtre réglable du gaspillage consolidé

Revision ID: b3e7d1a5c9f4
Revises: a9d3f6c2b4e7
Create Date: 2026-09-09 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3e7d1a5c9f4'
down_revision: Union[str, None] = 'a9d3f6c2b4e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f22_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('waste_summary_window_days', sa.Float(), nullable=False, server_default='90.0')
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f22_enabled', server_default=None)
        batch_op.alter_column('waste_summary_window_days', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('waste_summary_window_days')
        batch_op.drop_column('feature_f22_enabled')
