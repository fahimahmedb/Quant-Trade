"""IA-1 F15 : empreinte de fichier, jours fermés, seuil d'alerte de volume

Revision ID: 9d24e6a1f7b8
Revises: 7a13f0c5b2de
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d24e6a1f7b8'
down_revision: Union[str, None] = '7a13f0c5b2de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('sales_imports', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content_hash', sa.String(length=64), nullable=True))
        batch_op.create_index(
            batch_op.f('ix_sales_imports_content_hash'), ['content_hash'], unique=False
        )

    op.create_table(
        'closed_days',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('closed_on', sa.Date(), nullable=False),
        sa.Column('reason', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('closed_on'),
    )

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('import_volume_alert_pct', sa.Float(), nullable=False, server_default='40.0')
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('import_volume_alert_pct', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('import_volume_alert_pct')

    op.drop_table('closed_days')

    with op.batch_alter_table('sales_imports', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sales_imports_content_hash'))
        batch_op.drop_column('content_hash')
