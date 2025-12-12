from dataclasses import field, dataclass
from enum import Enum
from typing import List, Optional
from uuid import uuid4, UUID

""" DTO data structures/classes for builds and components """


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
    upgradable: bool
    ecc: bool
    clock: int #mhz
    size: int #mb


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


@dataclass
class StorageDisk(BuildComponent):
    type: StorageDiskType
    upgradable: bool
    size: int #mb
    form: StorageDiskForm
    interface: StorageDiskInterface


@dataclass
class GraphicsCard(BuildComponent):
    model: str
    upgradable: bool
    memory: Optional[int] = None #mb
    clock: Optional[int] = None #mhz


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


@dataclass
class Build:
    type: BuildType
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
