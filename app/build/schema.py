from dataclasses import dataclass, field
from struct import Struct

from app.db.enum import BuildType, WirelessNetworkingStandard, MemoryType, StorageDiskType, StorageDiskInterface, \
    StorageDiskForm
from app.db.model.display import Resolution


@dataclass
class BuildCreateProcessor:
    model: str = field()
    id: str | None = field(default=None)
    upgradable: bool = field(default=True)


@dataclass
class BuildCreateMemoryModule:
    type: MemoryType = field()
    clock: int = field()
    size: int = field()
    upgradable: bool = field(default=True)
    ecc: bool = field(default=False)


@dataclass
class BuildCreateStorageDisk:
    type: StorageDiskType = field()
    form: StorageDiskForm = field()
    interface: StorageDiskInterface = field()
    size: int = field()
    upgradable: bool = field(default=True)


@dataclass
class BuildCreateBattery:
    design_capacity: int = field()
    remaining_capacity: int = field()


@dataclass
class BuildCreateDisplay:
    size: float = field()
    refresh_rate: int = field()
    resolution: Resolution = field()
    touchscreen: bool = field(default=False)


@dataclass
class BuildCreate:
    type: BuildType = field()

    manufacturer: str | None = field()
    model: str | None = field()

    wired_networking: int | None = field()
    wireless_networking: WirelessNetworkingStandard | None = field()
    bluetooth: bool = field(default=False)

    processors: list[BuildCreateProcessor] = field(default_factory=list)
    graphics: list[BuildCreateProcessor] = field(default_factory=list)

    memory: list[BuildCreateMemoryModule] = field(default_factory=list)
    storage: list[BuildCreateStorageDisk] = field(default_factory=list)

    batteries: list[BuildCreateBattery] = field(default_factory=list)
    display: BuildCreateDisplay | None = field(default=None)
