"""IA-2 F24 : feature flag comparaison de prix multi-fournisseurs

Revision ID: f5b8e2a1c4d6
Revises: e1a4c9f7d3b2
Create Date: 2026-09-10 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5b8e2a1c4d6'
down_revision: Union[str, None] = 'e1a4c9f7d3b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f24_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f24_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f24_enabled')
