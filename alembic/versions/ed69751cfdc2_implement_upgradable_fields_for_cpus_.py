"""Implement upgradable fields for cpus/gpus

Revision ID: ed69751cfdc2
Revises: 741f648bc25c
Create Date: 2026-02-11 12:44:57.157368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed69751cfdc2'
down_revision: Union[str, Sequence[str], None] = '741f648bc25c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('graphics_build_associations', sa.Column('upgradable', sa.Boolean(), nullable=False, default=True, server_default='True'))
    op.add_column('processor_build_associations', sa.Column('upgradable', sa.Boolean(), nullable=False, default=True, server_default='True'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('processor_build_associations', 'upgradable')
    op.drop_column('graphics_build_associations', 'upgradable')
