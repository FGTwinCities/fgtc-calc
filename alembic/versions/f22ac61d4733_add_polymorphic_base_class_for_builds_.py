"""Add polymorphic base class for builds, add mac build class

Revision ID: f22ac61d4733
Revises: acbc40d75e65
Create Date: 2026-03-04 13:07:31.363121

"""
from typing import Sequence, Union

import advanced_alchemy
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f22ac61d4733'
down_revision: Union[str, Sequence[str], None] = 'acbc40d75e65'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('modernbuild',
        sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['build.id'], name=op.f('fk_modernbuild_id_build')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_modernbuild')),
        sa.Column('manufacturer', sa.String(), nullable=True),
    )

    op.add_column('build', sa.Column('class_type', sa.String(), nullable=True))

    op.execute("INSERT INTO modernbuild (id, manufacturer) SELECT id, manufacturer FROM build")
    op.execute("UPDATE build SET class_type = 'modernbuild'")

    op.alter_column('build', 'class_type', nullable=False)

    op.drop_column('build', 'manufacturer')

    op.create_table('macbuild',
        sa.Column('id', advanced_alchemy.types.guid.GUID(length=16), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['build.id'], name=op.f('fk_macbuild_id_build')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_macbuild'))
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('build', sa.Column('manufacturer', sa.VARCHAR(), autoincrement=False, nullable=True))

    op.execute("UPDATE build SET manufacturer = (SELECT manufacturer FROM modernbuild WHERE build.id = modernbuild.id)")

    op.drop_column('build', 'class_type')
    op.drop_table('modernbuild')
    op.drop_table('macbuild')
