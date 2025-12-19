from dataclasses import dataclass
from typing import Optional

from app.build.model import MemoryModule


@dataclass
class Price:
    price: Optional[float] = None


@dataclass
class MemoryModulePrice(Price):
    module: MemoryModule = None