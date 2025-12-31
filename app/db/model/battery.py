from dataclasses import dataclass

from advanced_alchemy.base import UUIDBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


@dataclass
class Battery(UUIDBase):
    __tablename__ = "battery"
    build_id = mapped_column(ForeignKey("build.id"))

    design_capacity: Mapped[int] = mapped_column(nullable=False)
    remaining_capacity: Mapped[int] = mapped_column(nullable=False)
