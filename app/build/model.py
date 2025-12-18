import uuid
from typing import Optional

from litestar.plugins.sqlalchemy import base
from sqlalchemy import ForeignKey, Column, Table, Boolean, BINARY, UUID
from sqlalchemy.orm import Mapped, relationship

from app.build.build import BuildType, MemoryType, StorageDiskType, StorageDiskForm, StorageDiskInterface, \
    WirelessNetworkingStandard

build_to_processor = Table(
    "build_to_processor",
    base.UUIDBase.metadata,
    Column("build_id", ForeignKey("build.id")),
    Column("processor_id", ForeignKey("processor.id")),
)


class Processor(base.UUIDBase):
    __tablename__ = "processor"

    model: Mapped[str]
    #TODO: Specifications


#TODO: MemoryModules should not have their own UUID, replace with integer key
class MemoryModule(base.UUIDBase):
    __tablename__ = "memory_module"
    build_id = Column(ForeignKey("build.id"), primary_key=True, nullable=True)

    type: Mapped[MemoryType]
    upgradable: Mapped[bool]
    ecc: Mapped[bool]
    clock: Mapped[int]
    size: Mapped[int]


#TODO: StorageDisk should not have their own UUID, replace with integer key
class StorageDisk(base.UUIDBase):
    __tablename__ = "storage_disk"
    build_id = Column(ForeignKey("build.id"), primary_key=True, nullable=True)

    type: Mapped[StorageDiskType]
    upgradable: Mapped[bool]
    form: Mapped[StorageDiskForm]
    interface: Mapped[StorageDiskInterface]
    size: Mapped[int]


build_to_graphics_processor = Table(
    "build_to_graphics_processor",
    base.UUIDBase.metadata,
    Column("build_id", ForeignKey("build.id")),
    Column("graphics_processor_id", ForeignKey("graphics_processor.id")),
)


class GraphicsProcessor(base.UUIDBase):
    __tablename__ = "graphics_processor"

    model: Mapped[str]
    #TODO: Specifications


class Build(base.UUIDAuditBase):
    __tablename__ = "build"

    type: Mapped[BuildType]
    manufacturer: Mapped[str]
    model: Mapped[str]
    price: Mapped[Optional[float]]
    processors: Mapped[list[Processor]] = relationship("Processor", secondary=build_to_processor, lazy="selectin")
    memory: Mapped[list[MemoryModule]] = relationship("MemoryModule", lazy="selectin")
    storage: Mapped[list[StorageDisk]] = relationship("StorageDisk", lazy="selectin")
    graphics: Mapped[list[GraphicsProcessor]] = relationship("GraphicsProcessor", secondary=build_to_graphics_processor, lazy="selectin")
    wired_networking: Mapped[Optional[int]] = None
    wireless_networking: Mapped[Optional[WirelessNetworkingStandard]] = None
