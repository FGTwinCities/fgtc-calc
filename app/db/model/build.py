from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, relationship, mapped_column

from app.db.enum import BuildType, WirelessNetworkingStandard
from app.db.model.battery import Battery
from app.db.model.build_graphics import build_to_graphics_processor
from app.db.model.build_processor import build_to_processor
from app.db.model.display import Display
from app.db.model.graphics import GraphicsProcessor
from app.db.model.memory import MemoryModule
from app.db.model.mixins.price import PriceMixin
from app.db.model.processor import Processor
from app.db.model.storage import StorageDisk


@dataclass
class Build(UUIDAuditBase, PriceMixin):
    __tablename__ = "build"

    type: Mapped[BuildType] = mapped_column(nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(nullable=True, default=None)
    model: Mapped[str | None] = mapped_column(nullable=True, default=None)
    wired_networking: Mapped[int | None] = mapped_column(nullable=True, default=None) #TODO: Handle multiple, store connector type
    wireless_networking: Mapped[WirelessNetworkingStandard | None] = mapped_column(nullable=True, default=None)
    bluetooth: Mapped[bool] = mapped_column(nullable=False, default=False)

    # ORM Relationships
    processors: Mapped[list[Processor]] = relationship(
        "Processor",
        secondary=build_to_processor,
        lazy="selectin",
    )

    memory: Mapped[list[MemoryModule]] = relationship(
        "MemoryModule",
        lazy="selectin",
    )

    storage: Mapped[list[StorageDisk]] = relationship(
        "StorageDisk",
        lazy="selectin",
    )

    graphics: Mapped[list[GraphicsProcessor]] = relationship(
        "GraphicsProcessor",
        secondary=build_to_graphics_processor,
        lazy="selectin",
    )

    #TODO: Figure out some way to make this not a list!
    #   -> once SQLAlchemy 2.1 is released, upgrade and use a composite object instead
    display: Mapped[list[Display]] = relationship(
        "Display",
        lazy="selectin",
    )

    batteries: Mapped[list[Battery]] = relationship(
        "Battery",
        lazy="selectin",
    )
