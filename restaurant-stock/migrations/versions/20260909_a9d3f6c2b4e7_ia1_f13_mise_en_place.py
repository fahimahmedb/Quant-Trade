"""IA-1 F13 : préparé en interne (ingredient), feature flag

Revision ID: a9d3f6c2b4e7
Revises: f2a7c9d4e8b1
Create Date: 2026-09-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a9d3f6c2b4e7'
down_revision: Union[str, None] = 'f2a7c9d4e8b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_prepared_in_house', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('is_prepared_in_house', server_default=None)

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f13_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f13_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f13_enabled')

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('is_prepared_in_house')
