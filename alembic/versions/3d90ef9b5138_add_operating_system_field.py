"""Add Operating System field

Revision ID: 3d90ef9b5138
Revises: 17c1bdbc2667
Create Date: 2026-01-22 13:52:31.174508

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d90ef9b5138'
down_revision: Union[str, Sequence[str], None] = '17c1bdbc2667'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('build', sa.Column('operating_system', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('build', 'operating_system')
