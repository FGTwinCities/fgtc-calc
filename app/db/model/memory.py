#TODO: MemoryModules should not have their own UUID, replace with integer key
from dataclasses import dataclass

from advanced_alchemy.base import UUIDBase
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped

from app.db.enum import MemoryType


@dataclass
class MemoryModule(UUIDBase):
    __tablename__ = "memory_module"
    build_id = Column(ForeignKey("build.id"), primary_key=True, nullable=True)

    type: Mapped[MemoryType]
    upgradable: Mapped[bool]
    ecc: Mapped[bool]
    clock: Mapped[int]
    size: Mapped[int]