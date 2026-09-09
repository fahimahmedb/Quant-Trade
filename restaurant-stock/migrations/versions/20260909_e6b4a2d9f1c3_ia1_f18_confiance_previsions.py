"""IA-1 F18 : retour auto v1 par ingrédient, journal de décision modèle

Revision ID: e6b4a2d9f1c3
Revises: c3f8e1a5b7d2
Create Date: 2026-09-09 05:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6b4a2d9f1c3'
down_revision: Union[str, None] = 'c3f8e1a5b7d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('f6_reverted_to_v1', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.alter_column('f6_reverted_to_v1', server_default=None)

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('feature_f18_enabled', sa.Boolean(), nullable=False, server_default=sa.false())
        )
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.alter_column('feature_f18_enabled', server_default=None)

    op.create_table(
        'model_decision_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('feature', sa.String(length=10), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('event', sa.String(length=50), nullable=False),
        sa.Column('detail', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('model_decision_log')

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('feature_f18_enabled')

    with op.batch_alter_table('ingredients', schema=None) as batch_op:
        batch_op.drop_column('f6_reverted_to_v1')
