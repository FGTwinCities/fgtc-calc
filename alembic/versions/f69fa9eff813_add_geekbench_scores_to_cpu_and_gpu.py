"""Add Geekbench scores to CPU and GPU

Revision ID: f69fa9eff813
Revises: 15ce799e639b
Create Date: 2026-01-30 14:27:00.017437

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f69fa9eff813'
down_revision: Union[str, Sequence[str], None] = '15ce799e639b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('graphics_processor', 'score', new_column_name='passmark_score')
    op.alter_column('graphics_processor', 'score_g2d', new_column_name='passmark_score_g2d')
    op.alter_column('processor', 'multithread_score', new_column_name='passmark_multithread_score')
    op.alter_column('processor', 'single_thread_score', new_column_name='passmark_single_thread_score')
    op.add_column('processor', sa.Column('geekbench_id', sa.Integer(), nullable=True))
    op.add_column('processor', sa.Column('geekbench_multithread_score', sa.Integer(), nullable=True))
    op.add_column('processor', sa.Column('geekbench_single_thread_score', sa.Integer(), nullable=True))
    op.add_column('graphics_processor', sa.Column('geekbench_id', sa.Integer(), nullable=True))
    op.add_column('graphics_processor', sa.Column('geekbench_score', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('processor', 'passmark_single_thread_score', new_column_name='single_thread_score')
    op.alter_column('processor', 'passmark_multithread_score', new_column_name='multithread_score')
    op.alter_column('graphics_processor', 'passmark_score_g2d', new_column_name='score_g2d')
    op.alter_column('graphics_processor', 'passmark_score', new_column_name='score')
    op.drop_column('graphics_processor', 'geekbench_score')
    op.drop_column('graphics_processor', 'geekbench_id')
    op.drop_column('processor', 'geekbench_single_thread_score')
    op.drop_column('processor', 'geekbench_multithread_score')
    op.drop_column('processor', 'geekbench_id')
