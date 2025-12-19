from dataclasses import dataclass
from enum import Enum
from typing import Optional

from litestar.plugins.sqlalchemy import base
from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, relationship


class MemoryType(Enum):
    DDR = 1
    DDR2 = 2
    DDR3 = 3
    DDR4 = 4
    DDR5 = 5


class StorageDiskType(Enum):
    HDD = "hdd"
    SSD = "ssd"


class StorageDiskForm(Enum):
    INCH25 = "2.5"
    INCH35 = "3.5"
    M2 = "m2"
    PCIE = "pcie"


class StorageDiskInterface(Enum):
    IDE = "ide"
    SAS = "sas"
    SATA = "sata"
    NVME = "nvme"


class WirelessNetworkingStandard(Enum):
    BG = "bg"
    N = "n"
    AC = "ac"
    AX = "ax"
    BE = "be"


class BuildType(Enum):
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    ALL_IN_ONE = "aio"
    SERVER = "server"
    TABLET = "tablet"
    OTHER = "other"


build_to_processor = Table(
    "build_to_processor",
    base.UUIDBase.metadata,
    Column("build_id", ForeignKey("build.id")),
    Column("processor_id", ForeignKey("processor.id")),
)


@dataclass
class Processor(base.UUIDBase):
    __tablename__ = "processor"

    model: Mapped[str]
    #TODO: Specifications


#TODO: MemoryModules should not have their own UUID, replace with integer key
@dataclass
class MemoryModule(base.UUIDBase):
    __tablename__ = "memory_module"
    build_id = Column(ForeignKey("build.id"), primary_key=True, nullable=True)

    type: Mapped[MemoryType]
    upgradable: Mapped[bool]
    ecc: Mapped[bool]
    clock: Mapped[int]
    size: Mapped[int]


#TODO: StorageDisk should not have their own UUID, replace with integer key
@dataclass
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


@dataclass
class GraphicsProcessor(base.UUIDBase):
    __tablename__ = "graphics_processor"

    model: Mapped[str]
    #TODO: Specifications


@dataclass
class Build(base.UUIDAuditBase):
    __tablename__ = "build"

    type: Mapped[BuildType]
    manufacturer: Mapped[str]
    model: Mapped[str]
    price: Mapped[Optional[float]] = None
    processors: Mapped[list[Processor]] = relationship("Processor", secondary=build_to_processor, lazy="selectin")
    memory: Mapped[list[MemoryModule]] = relationship("MemoryModule", lazy="selectin")
    storage: Mapped[list[StorageDisk]] = relationship("StorageDisk", lazy="selectin")
    graphics: Mapped[list[GraphicsProcessor]] = relationship("GraphicsProcessor", secondary=build_to_graphics_processor, lazy="selectin")
    wired_networking: Mapped[Optional[int]] = None #TODO: Handle multiple, store connector type
    wireless_networking: Mapped[Optional[WirelessNetworkingStandard]] = None
    bluetooth: Mapped[bool] = False
