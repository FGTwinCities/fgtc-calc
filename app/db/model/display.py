from dataclasses import dataclass

from advanced_alchemy.base import UUIDBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, composite
from sqlalchemy.testing.schema import mapped_column


@dataclass
class Resolution:
    x: int
    y: int


@dataclass
class Display(UUIDBase):
    __tablename__ = "display"
    build_id = mapped_column(ForeignKey("build.id"), nullable=True)

    size: Mapped[float] = mapped_column(nullable=False)
    resolution: Mapped[Resolution] = composite(mapped_column("resolution_x"), mapped_column("resolution_y"))
    refresh_rate: Mapped[int] = mapped_column(nullable=False)
    touchscreen: Mapped[bool] = mapped_column(default=False)