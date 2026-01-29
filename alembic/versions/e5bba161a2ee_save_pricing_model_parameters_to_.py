"""Save pricing model parameters to database

Revision ID: e5bba161a2ee
Revises: 3d90ef9b5138
Create Date: 2026-01-28 15:07:09.918613

"""
from typing import Sequence, Union

import advanced_alchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5bba161a2ee'
down_revision: Union[str, Sequence[str], None] = '3d90ef9b5138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('pricing_model',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('processor_param_a', sa.Float(), nullable=True),
    sa.Column('processor_param_b', sa.Float(), nullable=True),
    sa.Column('memory_param_a', sa.Float(), nullable=True),
    sa.Column('memory_param_b', sa.Float(), nullable=True),
    sa.Column('memory_param_c', sa.Float(), nullable=True),
    sa.Column('memory_param_d', sa.Float(), nullable=True),
    sa.Column('memory_param_e', sa.Float(), nullable=True),
    sa.Column('storage_hdd_param_a', sa.Float(), nullable=True),
    sa.Column('storage_hdd_param_b', sa.Float(), nullable=True),
    sa.Column('storage_hdd_param_c', sa.Float(), nullable=True),
    sa.Column('storage_sata_ssd_param_a', sa.Float(), nullable=True),
    sa.Column('storage_sata_ssd_param_b', sa.Float(), nullable=True),
    sa.Column('storage_sata_ssd_param_c', sa.Float(), nullable=True),
    sa.Column('storage_nvme_ssd_param_a', sa.Float(), nullable=True),
    sa.Column('storage_nvme_ssd_param_b', sa.Float(), nullable=True),
    sa.Column('storage_nvme_ssd_param_c', sa.Float(), nullable=True),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.Column('created_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.Column('updated_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_pricing_model'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('pricing_model')
