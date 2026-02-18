"""Cascading deletions for database subobjects

Revision ID: acbc40d75e65
Revises: ed69751cfdc2
Create Date: 2026-02-18 15:28:23.764464

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acbc40d75e65'
down_revision: Union[str, Sequence[str], None] = 'ed69751cfdc2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('DELETE FROM battery WHERE build_id IS NULL')
    op.execute('DELETE FROM display WHERE build_id IS NULL')
    op.execute('DELETE FROM memory_module WHERE build_id IS NULL')
    op.execute('DELETE FROM storage_disk WHERE build_id IS NULL')
    op.execute('DELETE FROM processor_build_associations WHERE build_id IS NULL OR processor_id IS NULL')
    op.execute('DELETE FROM graphics_build_associations WHERE build_id IS NULL OR graphics_id IS NULL')

    op.alter_column('battery', 'build_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint(op.f('fk_battery_build_id_build'), 'battery', type_='foreignkey')
    op.create_foreign_key(op.f('fk_battery_build_id_build'), 'battery', 'build', ['build_id'], ['id'], ondelete='CASCADE')
    op.alter_column('display', 'build_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint(op.f('fk_display_build_id_build'), 'display', type_='foreignkey')
    op.create_foreign_key(op.f('fk_display_build_id_build'), 'display', 'build', ['build_id'], ['id'], ondelete='CASCADE')
    op.alter_column('graphics_build_associations', 'build_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('graphics_build_associations', 'graphics_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint(op.f('fk_graphics_build_associations_graphics_id_graphics_processor'), 'graphics_build_associations', type_='foreignkey')
    op.drop_constraint(op.f('fk_graphics_build_associations_build_id_build'), 'graphics_build_associations', type_='foreignkey')
    op.create_foreign_key(op.f('fk_graphics_build_associations_build_id_build'), 'graphics_build_associations', 'build', ['build_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_graphics_build_associations_graphics_id_graphics_processor'), 'graphics_build_associations', 'graphics_processor', ['graphics_id'], ['id'], ondelete='CASCADE')
    op.alter_column('memory_module', 'build_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint(op.f('fk_memory_module_build_id_build'), 'memory_module', type_='foreignkey')
    op.create_foreign_key(op.f('fk_memory_module_build_id_build'), 'memory_module', 'build', ['build_id'], ['id'], ondelete='CASCADE')
    op.alter_column('processor_build_associations', 'build_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('processor_build_associations', 'processor_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint(op.f('fk_processor_build_associations_build_id_build'), 'processor_build_associations', type_='foreignkey')
    op.drop_constraint(op.f('fk_processor_build_associations_processor_id_processor'), 'processor_build_associations', type_='foreignkey')
    op.create_foreign_key(op.f('fk_processor_build_associations_build_id_build'), 'processor_build_associations', 'build', ['build_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(op.f('fk_processor_build_associations_processor_id_processor'), 'processor_build_associations', 'processor', ['processor_id'], ['id'], ondelete='CASCADE')
    op.alter_column('storage_disk', 'build_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_constraint(op.f('fk_storage_disk_build_id_build'), 'storage_disk', type_='foreignkey')
    op.create_foreign_key(op.f('fk_storage_disk_build_id_build'), 'storage_disk', 'build', ['build_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f('fk_storage_disk_build_id_build'), 'storage_disk', type_='foreignkey')
    op.create_foreign_key(op.f('fk_storage_disk_build_id_build'), 'storage_disk', 'build', ['build_id'], ['id'])
    op.alter_column('storage_disk', 'build_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_processor_build_associations_processor_id_processor'), 'processor_build_associations', type_='foreignkey')
    op.drop_constraint(op.f('fk_processor_build_associations_build_id_build'), 'processor_build_associations', type_='foreignkey')
    op.create_foreign_key(op.f('fk_processor_build_associations_processor_id_processor'), 'processor_build_associations', 'processor', ['processor_id'], ['id'])
    op.create_foreign_key(op.f('fk_processor_build_associations_build_id_build'), 'processor_build_associations', 'build', ['build_id'], ['id'])
    op.alter_column('processor_build_associations', 'processor_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('processor_build_associations', 'build_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_memory_module_build_id_build'), 'memory_module', type_='foreignkey')
    op.create_foreign_key(op.f('fk_memory_module_build_id_build'), 'memory_module', 'build', ['build_id'], ['id'])
    op.alter_column('memory_module', 'build_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_graphics_build_associations_graphics_id_graphics_processor'), 'graphics_build_associations', type_='foreignkey')
    op.drop_constraint(op.f('fk_graphics_build_associations_build_id_build'), 'graphics_build_associations', type_='foreignkey')
    op.create_foreign_key(op.f('fk_graphics_build_associations_build_id_build'), 'graphics_build_associations', 'build', ['build_id'], ['id'])
    op.create_foreign_key(op.f('fk_graphics_build_associations_graphics_id_graphics_processor'), 'graphics_build_associations', 'graphics_processor', ['graphics_id'], ['id'])
    op.alter_column('graphics_build_associations', 'graphics_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.alter_column('graphics_build_associations', 'build_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_display_build_id_build'), 'display', type_='foreignkey')
    op.create_foreign_key(op.f('fk_display_build_id_build'), 'display', 'build', ['build_id'], ['id'])
    op.alter_column('display', 'build_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_constraint(op.f('fk_battery_build_id_build'), 'battery', type_='foreignkey')
    op.create_foreign_key(op.f('fk_battery_build_id_build'), 'battery', 'build', ['build_id'], ['id'])
    op.alter_column('battery', 'build_id',
               existing_type=sa.UUID(),
               nullable=True)
