"""Add notes to build

Revision ID: 15ce799e639b
Revises: a8de254ec7b2
Create Date: 2026-01-29 11:27:00.767622

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15ce799e639b'
down_revision: Union[str, Sequence[str], None] = 'a8de254ec7b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('build', sa.Column('notes', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('build', 'notes')
