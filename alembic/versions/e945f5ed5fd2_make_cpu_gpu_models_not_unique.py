"""Make CPU/GPU models not unique

Revision ID: e945f5ed5fd2
Revises: 15ce799e639b
Create Date: 2026-02-04 14:08:51.830633

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e945f5ed5fd2'
down_revision: Union[str, Sequence[str], None] = '15ce799e639b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(op.f('uq_graphics_processor_model'), 'graphics_processor', type_='unique')
    op.drop_constraint(op.f('uq_processor_model'), 'processor', type_='unique')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_unique_constraint(op.f('uq_processor_model'), 'processor', ['model'], postgresql_nulls_not_distinct=False)
    op.create_unique_constraint(op.f('uq_graphics_processor_model'), 'graphics_processor', ['model'], postgresql_nulls_not_distinct=False)
