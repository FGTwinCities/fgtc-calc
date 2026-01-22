"""Initial revision

Revision ID: 17c1bdbc2667
Revises: 
Create Date: 2026-01-21 18:35:04.433601

"""
from typing import Sequence, Union

import advanced_alchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17c1bdbc2667'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('build',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('type', sa.Enum('DESKTOP', 'LAPTOP', 'ALL_IN_ONE', 'SERVER', 'TABLET', 'OTHER', name='buildtype'), nullable=False),
    sa.Column('manufacturer', sa.String(), nullable=True),
    sa.Column('model', sa.String(), nullable=True),
    sa.Column('wired_networking', sa.Integer(), nullable=True),
    sa.Column('wireless_networking', sa.Enum('BG', 'N', 'AC', 'AX', 'BE', name='wirelessnetworkingstandard'), nullable=True),
    sa.Column('bluetooth', sa.Boolean(), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.Column('created_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.Column('priced_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=True),
    sa.Column('updated_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_build'))
    )
    op.create_table('graphics_processor',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.Column('created_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.Column('priced_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=True),
    sa.Column('updated_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_graphics_processor')),
    sa.UniqueConstraint('model', name=op.f('uq_graphics_processor_model'))
    )
    op.create_table('processor',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('model', sa.String(), nullable=False),
    sa.Column('passmark_id', sa.Integer(), nullable=True),
    sa.Column('multithread_score', sa.Integer(), nullable=True),
    sa.Column('single_thread_score', sa.Integer(), nullable=True),
    sa.Column('performance_core_count', sa.Integer(), nullable=True),
    sa.Column('performance_thread_count', sa.Integer(), nullable=True),
    sa.Column('performance_clock', sa.Integer(), nullable=True),
    sa.Column('performance_turbo_clock', sa.Integer(), nullable=True),
    sa.Column('efficient_core_count', sa.Integer(), nullable=True),
    sa.Column('efficient_thread_count', sa.Integer(), nullable=True),
    sa.Column('efficient_clock', sa.Integer(), nullable=True),
    sa.Column('efficient_turbo_clock', sa.Integer(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.Column('created_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.Column('priced_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=True),
    sa.Column('updated_at', advanced_alchemy.types.datetime.DateTimeUTC(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_processor')),
    sa.UniqueConstraint('model', name=op.f('uq_processor_model'))
    )
    op.create_table('battery',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('design_capacity', sa.Integer(), nullable=False),
    sa.Column('remaining_capacity', sa.Integer(), nullable=False),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_battery_build_id_build')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_battery'))
    )
    op.create_table('display',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('size', sa.Float(), nullable=False),
    sa.Column('resolution_x', sa.Integer(), nullable=False),
    sa.Column('resolution_y', sa.Integer(), nullable=False),
    sa.Column('refresh_rate', sa.Integer(), nullable=False),
    sa.Column('touchscreen', sa.Boolean(), nullable=False),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_display_build_id_build')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_display'))
    )
    op.create_table('graphics_build_associations',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('graphics_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_graphics_build_associations_build_id_build')),
    sa.ForeignKeyConstraint(['graphics_id'], ['graphics_processor.id'], name=op.f('fk_graphics_build_associations_graphics_id_graphics_processor')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_graphics_build_associations'))
    )
    op.create_table('memory_module',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('type', sa.Enum('DDR', 'DDR2', 'DDR3', 'DDR4', 'DDR5', name='memorytype'), nullable=False),
    sa.Column('upgradable', sa.Boolean(), nullable=False),
    sa.Column('ecc', sa.Boolean(), nullable=False),
    sa.Column('clock', sa.Integer(), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_memory_module_build_id_build')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_memory_module'))
    )
    op.create_table('processor_build_associations',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('processor_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_processor_build_associations_build_id_build')),
    sa.ForeignKeyConstraint(['processor_id'], ['processor.id'], name=op.f('fk_processor_build_associations_processor_id_processor')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_processor_build_associations'))
    )
    op.create_table('storage_disk',
    sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
    sa.Column('build_id', advanced_alchemy.types.guid.GUID(length=16), nullable=True),
    sa.Column('type', sa.Enum('HDD', 'SSD', name='storagedisktype'), nullable=False),
    sa.Column('upgradable', sa.Boolean(), nullable=False),
    sa.Column('form', sa.Enum('INCH25', 'INCH35', 'M2', 'PCIE', name='storagediskform'), nullable=False),
    sa.Column('interface', sa.Enum('IDE', 'SAS', 'SATA', 'NVME', name='storagediskinterface'), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('sa_orm_sentinel', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['build_id'], ['build.id'], name=op.f('fk_storage_disk_build_id_build')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_storage_disk'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('storage_disk')
    op.drop_table('processor_build_associations')
    op.drop_table('memory_module')
    op.drop_table('graphics_build_associations')
    op.drop_table('display')
    op.drop_table('battery')
    op.drop_table('processor')
    op.drop_table('graphics_processor')
    op.drop_table('build')
