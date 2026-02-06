"""Add enum values for storing soldered eMMC storage drives

Revision ID: ebb694d1d861
Revises: e945f5ed5fd2
Create Date: 2026-02-05 18:09:34.745310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic_postgresql_enum import TableReference

# revision identifiers, used by Alembic.
revision: str = 'ebb694d1d861'
down_revision: Union[str, Sequence[str], None] = 'e945f5ed5fd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.sync_enum_values(
        enum_schema='public',
        enum_name='storagediskform',
        new_values=['INCH25', 'INCH35', 'M2', 'PCIE', 'SOLDERED'],
        affected_columns=[TableReference(table_schema='public', table_name='storage_disk', column_name='form')],
        enum_values_to_rename=[],
    )
    op.sync_enum_values(
        enum_schema='public',
        enum_name='storagediskinterface',
        new_values=['IDE', 'SAS', 'SATA', 'NVME', 'EMMC'],
        affected_columns=[TableReference(table_schema='public', table_name='storage_disk', column_name='interface')],
        enum_values_to_rename=[],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.sync_enum_values(
        enum_schema='public',
        enum_name='storagediskinterface',
        new_values=['IDE', 'SAS', 'SATA', 'NVME'],
        affected_columns=[TableReference(table_schema='public', table_name='storage_disk', column_name='interface')],
        enum_values_to_rename=[],
    )
    op.sync_enum_values(
        enum_schema='public',
        enum_name='storagediskform',
        new_values=['INCH25', 'INCH35', 'M2', 'PCIE'],
        affected_columns=[TableReference(table_schema='public', table_name='storage_disk', column_name='form')],
        enum_values_to_rename=[],
    )
