import datetime
from uuid import UUID

import msgspec

from app.db.enum import BuildType, WirelessNetworkingStandard, MemoryType, StorageDiskType, StorageDiskInterface, \
    StorageDiskForm, MacType
from app.db.model.display import Resolution
from app.db.model.macbuild import Version

"""
Data Transfer Objects (DTOs) for creating and updating builds, processors and GPUs.
These objects match the schema sent by the frontend.
"""


class BuildCreateProcessor(msgspec.Struct):
    model: str
    id: UUID | None = None
    upgradable: bool = True


class BuildCreateMemoryModule(msgspec.Struct):
    type: MemoryType
    clock: int
    size: int
    upgradable: bool = True
    ecc: bool = False


class BuildCreateStorageDisk(msgspec.Struct):
    type: StorageDiskType
    form: StorageDiskForm
    interface: StorageDiskInterface
    size: int
    upgradable: bool = True


class BuildCreateBattery(msgspec.Struct):
    design_capacity: int
    remaining_capacity: int


class BuildCreateDisplay(msgspec.Struct):
    size: float
    refresh_rate: int
    resolution: Resolution
    touchscreen: bool = False


class BuildCreate(msgspec.Struct):
    type: BuildType

    wired_networking: int | None = None
    wireless_networking: WirelessNetworkingStandard | None = None
    bluetooth: bool = False
    webcam: bool = False
    microphone: bool = False

    processors: list[BuildCreateProcessor] = []
    graphics: list[BuildCreateProcessor] = []

    memory: list[BuildCreateMemoryModule] = []
    storage: list[BuildCreateStorageDisk] = []

    batteries: list[BuildCreateBattery] = []
    display: BuildCreateDisplay | None = None

    notes: str | None = None


class ModernBuildCreate(BuildCreate):
    manufacturer: str | None = None
    model: str | None = None
    operating_system: str | None = None


class MacBuildCreate(BuildCreate):
    mac_type: MacType = MacType.OTHER
    macos_version: Version = None


class BuildRetrieve(msgspec.Struct):
    id: UUID
    class_type: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    price: float | None
    priced_at: datetime.datetime | None
    type: BuildType

    wired_networking: int | None
    wireless_networking: WirelessNetworkingStandard  | None
    bluetooth: bool
    webcam: bool
    microphone: bool

    processors: list[BuildCreateProcessor]
    graphics: list[BuildCreateProcessor]

    memory: list[BuildCreateMemoryModule]
    storage: list[BuildCreateStorageDisk]

    batteries: list[BuildCreateBattery]
    display: BuildCreateDisplay | None

    notes: str | None


class ModernBuildRetrieve(BuildRetrieve):
    manufacturer: str | None
    model: str | None
    operating_system: str | None


class MacBuildRetrieve(BuildRetrieve):
    mac_type: MacType
    macos_version: Version
