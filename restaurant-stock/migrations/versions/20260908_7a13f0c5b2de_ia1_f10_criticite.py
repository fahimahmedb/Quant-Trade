"""IA-1 F10 : feature flags F10/F15, forçage manuel de criticité

Revision ID: 7a13f0c5b2de
Revises: 2f1b7c4e9a03
Create Date: 2026-09-08 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7a13f0c5b2de'
down_revision: Union[str, None] = '2f1b7c4e9a03'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f10_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('feature_f15_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f10_enabled', server_default=None)
        batch_op.alter_column('feature_f15_enabled', server_default=None)

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('criticality_override', sa.String(length=1), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('criticality_override')

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f15_enabled')
        batch_op.drop_column('feature_f10_enabled')
