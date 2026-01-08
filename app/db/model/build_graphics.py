from advanced_alchemy.base import orm_registry
from sqlalchemy import Table, Column, ForeignKey

build_to_graphics_processor = Table(
    "build_to_graphics_processor",
    orm_registry.metadata,
    Column("build_id", ForeignKey("build.id")),
    Column("graphics_processor_id", ForeignKey("graphics_processor.id")),
)
