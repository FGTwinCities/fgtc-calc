from dataclasses import dataclass
from typing import Optional

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, relationship

from app.db.model.build_graphics import build_to_graphics_processor
from app.db.model.build_processor import build_to_processor
from app.db.enum import BuildType, WirelessNetworkingStandard
from app.db.model.graphics import GraphicsProcessor
from app.db.model.memory import MemoryModule
from app.db.model.processor import Processor
from app.db.model.storage import StorageDisk


@dataclass
class Build(UUIDAuditBase):
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