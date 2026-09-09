"""IA-2 F25 : table production_suggestions, feature flag

Revision ID: c8f2a4e6b1d9
Revises: b3e7d1a5c9f4
Create Date: 2026-09-09 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f2a4e6b1d9'
down_revision: Union[str, None] = 'b3e7d1a5c9f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'production_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False),
        sa.Column('window_days', sa.Integer(), nullable=False),
        sa.Column('suggested_quantity', sa.Float(), nullable=False),
        sa.Column('final_quantity', sa.Float(), nullable=True),
        sa.Column('decision', sa.Enum('en_attente', 'acceptee', 'modifiee', 'rejetee', name='suggestiondecision'), nullable=False),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f25_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f25_enabled', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f25_enabled')

    op.drop_table('production_suggestions')
