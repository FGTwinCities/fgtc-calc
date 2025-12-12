from dataclasses import field, dataclass
from enum import Enum
from typing import List, Optional
from uuid import uuid4, UUID

""" Data Structures/Classes for builds and components """


class BuildComponent:
    pass


@dataclass
class Processor(BuildComponent):
    manufacturer: str
    model: str
    clock: Optional[int] = None #mhz
    cores: Optional[int] = None
    threads: Optional[int] = None


class MemoryType(Enum):
    DDR = 1
    DDR2 = 2
    DDR3 = 3
    DDR4 = 4
    DDR5 = 5


@dataclass
class MemoryModule(BuildComponent):
    type: MemoryType
    clock: int #mhz
    size: int #mb


class StorageDiskForm(Enum):
    LAPTOP = "laptop"
    DESKTOP = "desktop"
    M2 = "m2"
    PCIE = "pcie"


class StorageDiskInterface(Enum):
    IDE = "ide"
    SAS = "sas"
    SATA = "sata"
    NVME = "nvme"


@dataclass
class StorageDisk(BuildComponent):
    size: int #mb
    form: StorageDiskForm
    interface: StorageDiskInterface


@dataclass
class SolidStateDisk(StorageDisk):
    pass


@dataclass
class HardDriveDisk(StorageDisk):
    pass


@dataclass
class GraphicsCard(BuildComponent):
    model: str
    memory: Optional[int] = None #mb
    clock: Optional[int] = None #mhz


class WirelessNetworkingStandard[Enum]:
    BGN = "bgn"
    AC = "ac"
    AX = "ax"


@dataclass
class Build:
    manufacturer: str
    model: str
    sku: str = ""
    price: Optional[float] = None
    processors: List[Optional[Processor]] = field(default_factory=List)
    memory: List[Optional[MemoryModule]] = field(default_factory=List)
    storage: List[StorageDisk] = field(default_factory=List)
    graphics: List[GraphicsCard] = field(default_factory=List)
    wired_networking: Optional[int] = None #mbps
    wireless_networking: Optional[WirelessNetworkingStandard] = None
    id: UUID = field(default_factory=uuid4)
