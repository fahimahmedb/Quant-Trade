"""IA-0 feature flags F5/F6/F7/F9

Revision ID: 93c5015f5db7
Revises: 45d4859fda91
Create Date: 2026-09-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93c5015f5db7'
down_revision: Union[str, None] = '45d4859fda91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default indispensable : la table settings contient déjà une
    # ligne sur une base existante, une colonne NOT NULL sans défaut échouerait.
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f5_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('feature_f6_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('feature_f7_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(
            sa.Column('feature_f9_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    # Le défaut applicatif prend le relais pour les insertions suivantes.
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f5_enabled', server_default=None)
        batch_op.alter_column('feature_f6_enabled', server_default=None)
        batch_op.alter_column('feature_f7_enabled', server_default=None)
        batch_op.alter_column('feature_f9_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f9_enabled')
        batch_op.drop_column('feature_f7_enabled')
        batch_op.drop_column('feature_f6_enabled')
        batch_op.drop_column('feature_f5_enabled')
