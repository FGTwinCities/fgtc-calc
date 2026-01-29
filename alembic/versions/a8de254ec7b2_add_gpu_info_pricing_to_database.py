"""Add GPU info/pricing to database

Revision ID: a8de254ec7b2
Revises: e5bba161a2ee
Create Date: 2026-01-28 18:19:48.249882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8de254ec7b2'
down_revision: Union[str, Sequence[str], None] = 'e5bba161a2ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('graphics_processor', sa.Column('passmark_id', sa.Integer(), nullable=True))
    op.add_column('graphics_processor', sa.Column('score', sa.Integer(), nullable=True))
    op.add_column('graphics_processor', sa.Column('score_g2d', sa.Integer(), nullable=True))
    op.add_column('pricing_model', sa.Column('graphics_param_a', sa.Float(), nullable=True))
    op.add_column('pricing_model', sa.Column('graphics_param_b', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pricing_model', 'graphics_param_b')
    op.drop_column('pricing_model', 'graphics_param_a')
    op.drop_column('graphics_processor', 'score_g2d')
    op.drop_column('graphics_processor', 'score')
    op.drop_column('graphics_processor', 'passmark_id')
