from advanced_alchemy.base import UUIDBase, orm_registry
from sqlalchemy import Table, Column, ForeignKey

build_to_processor = Table(
    "build_to_processor",
    orm_registry.metadata,
    Column("build_id", ForeignKey("build.id")),
    Column("processor_id", ForeignKey("processor.id")),
)