from dataclasses import dataclass, field
from typing import Optional, Any

from app.db.model.battery import Battery
from app.db.model.build import Build
from app.db.model.display import Display
from app.db.model.memory import MemoryModule
from app.db.model.storage import StorageDisk


@dataclass
class Price:
    price: Optional[float] = None


@dataclass
class MemoryModulePrice(Price):
    module: MemoryModule = None


@dataclass
class StorageDiskPrice(Price):
    disk: StorageDisk = None


@dataclass
class DisplayPrice(Price):
    display: Display = None


@dataclass
class BatteryPrice(Price):
    battery: Battery = None


@dataclass
class BuildPrice(Price):
    build: Build = None
    component_pricing: list[Any] = field(default_factory=list)


@dataclass
class PriceAdjustment(Price):
    comment: str | None = None
