"""Add thunderbolt to port types, add Hybrid as storage device type

Revision ID: 4fe4afe437ed
Revises: e5e39ef63c9d
Create Date: 2026-03-12 15:13:32.651544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = '4fe4afe437ed'
down_revision: Union[str, Sequence[str], None] = 'e5e39ef63c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('ports', sa.Column('thunderbolt', sa.Integer(), nullable=False, server_default='0'))
    op.sync_enum_values(
        enum_schema='public',
        enum_name='storagedisktype',
        new_values=['HDD', 'SSD', 'HYBRID'],
        affected_columns=[TableReference(table_schema='public', table_name='storage_disk', column_name='type')],
        enum_values_to_rename=[],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("UPDATE storage_disk SET type = 'HDD' WHERE type = 'HYBRID'")
    op.sync_enum_values(
        enum_schema='public',
        enum_name='storagedisktype',
        new_values=['HDD', 'SSD'],
        affected_columns=[TableReference(table_schema='public', table_name='storage_disk', column_name='type')],
        enum_values_to_rename=[],
    )
    op.drop_column('ports', 'thunderbolt')
