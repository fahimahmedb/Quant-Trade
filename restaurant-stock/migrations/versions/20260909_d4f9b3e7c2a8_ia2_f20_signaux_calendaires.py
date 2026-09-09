"""IA-2 F20 : table exceptional_days, zone de vacances, feature flag

Revision ID: d4f9b3e7c2a8
Revises: c8f2a4e6b1d9
Create Date: 2026-09-09 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f9b3e7c2a8'
down_revision: Union[str, None] = 'c8f2a4e6b1d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'exceptional_days',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('on_date', sa.Date(), nullable=False),
        sa.Column('note', sa.String(length=200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('on_date'),
    )

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f20_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
        batch_op.add_column(sa.Column('school_vacation_zone', sa.String(length=1), nullable=True))
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f20_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('school_vacation_zone')
        batch_op.drop_column('feature_f20_enabled')

    op.drop_table('exceptional_days')
