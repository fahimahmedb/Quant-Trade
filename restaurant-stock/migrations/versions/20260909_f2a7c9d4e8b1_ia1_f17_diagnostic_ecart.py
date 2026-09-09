"""IA-1 F17 : feature flag diagnostic de cause d'écart

Revision ID: f2a7c9d4e8b1
Revises: e6b4a2d9f1c3
Create Date: 2026-09-09 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2a7c9d4e8b1'
down_revision: Union[str, None] = 'e6b4a2d9f1c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f17_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f17_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f17_enabled')
