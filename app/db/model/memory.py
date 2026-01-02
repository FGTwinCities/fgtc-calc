#TODO: MemoryModules should not have their own UUID, replace with integer key
from dataclasses import dataclass

from advanced_alchemy.base import UUIDBase
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enum import MemoryType


@dataclass
class MemoryModule(UUIDBase):
    __tablename__ = "memory_module"
    build_id = mapped_column(ForeignKey("build.id"), nullable=True)

    type: Mapped[MemoryType] = mapped_column(nullable=False)
    upgradable: Mapped[bool] = mapped_column(default=True)
    ecc: Mapped[bool] = mapped_column(default=False)
    clock: Mapped[int] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
