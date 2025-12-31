from dataclasses import dataclass
from typing import Optional

from app.build.model import MemoryModule, StorageDisk


@dataclass
class Price:
    price: Optional[float] = None


@dataclass
class MemoryModulePrice(Price):
    module: MemoryModule = None


@dataclass
class StorageDiskPrice(Price):
    disk: StorageDisk = None