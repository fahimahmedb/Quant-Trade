"""IA-0 F7 : champs optionnels ingredient (conservation, livraison, conditionnement)

Revision ID: c95dd4d8c38e
Revises: 93c5015f5db7
Create Date: 2026-09-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c95dd4d8c38e'
down_revision: Union[str, None] = '93c5015f5db7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('shelf_life_days', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('delivery_weekdays', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('pack_size', sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('pack_size')
        batch_op.drop_column('delivery_weekdays')
        batch_op.drop_column('shelf_life_days')
