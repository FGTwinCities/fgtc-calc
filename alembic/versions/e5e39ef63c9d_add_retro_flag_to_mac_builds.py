"""Add retro flag to Mac builds

Revision ID: e5e39ef63c9d
Revises: d9fae10ccf5a
Create Date: 2026-03-12 12:38:14.557067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5e39ef63c9d'
down_revision: Union[str, Sequence[str], None] = 'd9fae10ccf5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('macbuild', sa.Column('is_retro', sa.Boolean(), nullable=False, default=False, server_default='False'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('macbuild', 'is_retro')
