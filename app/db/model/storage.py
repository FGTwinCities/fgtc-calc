#TODO: StorageDisk should not have their own UUID, replace with integer key
from dataclasses import dataclass

from advanced_alchemy.base import UUIDBase
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped

from app.db.enum import StorageDiskType, StorageDiskForm, StorageDiskInterface


@dataclass
class StorageDisk(UUIDBase):
    __tablename__ = "storage_disk"
    build_id = Column(ForeignKey("build.id"), primary_key=True, nullable=True)

    type: Mapped[StorageDiskType]
    upgradable: Mapped[bool]
    form: Mapped[StorageDiskForm]
    interface: Mapped[StorageDiskInterface]
    size: Mapped[int]