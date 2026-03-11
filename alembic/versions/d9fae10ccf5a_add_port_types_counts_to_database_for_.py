"""Add port types/counts to database for builds

Revision ID: d9fae10ccf5a
Revises: 78626b32ca6d
Create Date: 2026-03-11 15:28:24.857177

"""
from typing import Sequence, Union

import advanced_alchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9fae10ccf5a'
down_revision: Union[str, Sequence[str], None] = '78626b32ca6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('ports',
        sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.Column('hdmi', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('dp', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('dvi', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('vga', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('sd', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('usb', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('usb3', sa.Integer(), nullable=False, server_default="0"),
        sa.Column('usbc', sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_ports_build_id_build'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('build_id', name=op.f('pk_ports'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('ports')
