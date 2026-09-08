"""IA-0 : seuils IA réglables (F5 perte récurrente, F7 marge de sécurité)

Revision ID: 2f1b7c4e9a03
Revises: c95dd4d8c38e
Create Date: 2026-09-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f1b7c4e9a03'
down_revision: Union[str, None] = 'c95dd4d8c38e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('loss_alert_pct', sa.Float(), nullable=False, server_default='5.0')
        )
        batch_op.add_column(
            sa.Column('loss_alert_eur', sa.Float(), nullable=False, server_default='10.0')
        )
        batch_op.add_column(
            sa.Column('order_safety_margin_pct', sa.Float(), nullable=False, server_default='15.0')
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('loss_alert_pct', server_default=None)
        batch_op.alter_column('loss_alert_eur', server_default=None)
        batch_op.alter_column('order_safety_margin_pct', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('order_safety_margin_pct')
        batch_op.drop_column('loss_alert_eur')
        batch_op.drop_column('loss_alert_pct')
