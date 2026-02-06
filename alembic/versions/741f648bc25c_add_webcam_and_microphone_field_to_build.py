"""Add webcam and microphone field to build

Revision ID: 741f648bc25c
Revises: ebb694d1d861
Create Date: 2026-02-05 18:21:24.556695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '741f648bc25c'
down_revision: Union[str, Sequence[str], None] = 'ebb694d1d861'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('build', sa.Column('webcam', sa.Boolean(), nullable=False, default=False, server_default='False'))
    op.add_column('build', sa.Column('microphone', sa.Boolean(), nullable=False, default=False, server_default='False'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('build', 'microphone')
    op.drop_column('build', 'webcam')
