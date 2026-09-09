"""IA-1 F16 : fournisseur/franco sur ingredient, feature flag

Revision ID: 5e2b9c14a7f3
Revises: 3c8f1a92e4d6
Create Date: 2026-09-09 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5e2b9c14a7f3'
down_revision: Union[str, None] = '3c8f1a92e4d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('supplier_name', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('supplier_free_shipping_threshold', sa.Float(), nullable=True))

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f16_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f16_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f16_enabled')

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('supplier_free_shipping_threshold')
        batch_op.drop_column('supplier_name')
