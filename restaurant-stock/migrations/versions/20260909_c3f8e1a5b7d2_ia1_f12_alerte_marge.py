"""IA-1 F12 : feature flag et seuils réglables de l'alerte de marge

Revision ID: c3f8e1a5b7d2
Revises: 8a4d2f61c9e0
Create Date: 2026-09-09 04:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f8e1a5b7d2'
down_revision: Union[str, None] = '8a4d2f61c9e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f12_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('margin_coefficient_threshold', sa.Float(), nullable=False, server_default='3.0')
        )
        batch_op.add_column(
            sa.Column('margin_drop_pct_threshold', sa.Float(), nullable=False, server_default='10.0')
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f12_enabled', server_default=None)
        batch_op.alter_column('margin_coefficient_threshold', server_default=None)
        batch_op.alter_column('margin_drop_pct_threshold', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('margin_drop_pct_threshold')
        batch_op.drop_column('margin_coefficient_threshold')
        batch_op.drop_column('feature_f12_enabled')
