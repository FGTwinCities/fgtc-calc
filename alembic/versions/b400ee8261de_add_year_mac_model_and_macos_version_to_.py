"""Add year, Mac model, and MacOS version to Mac build database schema

Revision ID: b400ee8261de
Revises: f22ac61d4733
Create Date: 2026-03-05 16:08:24.784184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b400ee8261de'
down_revision: Union[str, Sequence[str], None] = 'f22ac61d4733'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    sa.Enum('OTHER', 'MACBOOK', 'MACBOOK_AIR', 'MACBOOK_PRO', 'MACBOOK_NEO', 'IMAC', 'IMAC_PRO', 'MAC_PRO', 'MAC_MINI', 'MAC_STUDIO', name='mactype').create(op.get_bind())
    op.add_column('macbuild', sa.Column('year', sa.Integer(), nullable=False))
    op.add_column('macbuild', sa.Column('mac_type', postgresql.ENUM('OTHER', 'MACBOOK', 'MACBOOK_AIR', 'MACBOOK_PRO', 'MACBOOK_NEO', 'IMAC', 'IMAC_PRO', 'MAC_PRO', 'MAC_MINI', 'MAC_STUDIO', name='mactype', create_type=False), nullable=False))
    op.add_column('macbuild', sa.Column('macos_version_major', sa.Integer(), nullable=True))
    op.add_column('macbuild', sa.Column('macos_version_minor', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('macbuild', 'macos_version_minor')
    op.drop_column('macbuild', 'macos_version_major')
    op.drop_column('macbuild', 'mac_type')
    op.drop_column('macbuild', 'year')
    sa.Enum('OTHER', 'MACBOOK', 'MACBOOK_AIR', 'MACBOOK_PRO', 'MACBOOK_NEO', 'IMAC', 'IMAC_PRO', 'MAC_PRO', 'MAC_MINI', 'MAC_STUDIO', name='mactype').drop(op.get_bind())
