#TODO: StorageDisk should not have their own UUID, replace with integer key
from dataclasses import dataclass

from advanced_alchemy.base import UUIDBase
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.enum import StorageDiskType, StorageDiskForm, StorageDiskInterface


@dataclass
class StorageDisk(UUIDBase):
    __tablename__ = "storage_disk"
    build_id = mapped_column(ForeignKey("build.id"), nullable=True)

    type: Mapped[StorageDiskType] = mapped_column(nullable=False)
    upgradable: Mapped[bool] = mapped_column(default=True)
    form: Mapped[StorageDiskForm] = mapped_column(nullable=False)
    interface: Mapped[StorageDiskInterface] = mapped_column(nullable=False)
    size: Mapped[int] = mapped_column(nullable=False)
