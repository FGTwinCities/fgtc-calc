"""Add browser installed field to Mac builds

Revision ID: 78626b32ca6d
Revises: b400ee8261de
Create Date: 2026-03-11 14:06:02.563694

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78626b32ca6d'
down_revision: Union[str, Sequence[str], None] = 'b400ee8261de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('macbuild', sa.Column('browser_installed', sa.Boolean(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('macbuild', 'browser_installed')
