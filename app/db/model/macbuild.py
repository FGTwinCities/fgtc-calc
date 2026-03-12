from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, composite

from app.db.enum import MacType
from app.db.model import BuildBase

@dataclass
class Version:
    major: int | None
    minor: int | None

class MacBuild(BuildBase):
    __tablename__ = "macbuild"

    id: Mapped[UUID] = mapped_column(ForeignKey("build.id"), primary_key=True, sort_order=-100)

    year: Mapped[int] = mapped_column()
    is_retro: Mapped[bool] = mapped_column(default=False)
    mac_type: Mapped[MacType] = mapped_column(default=MacType.OTHER)
    macos_version: Mapped[Version] = composite(
        mapped_column("macos_version_major"),
        mapped_column("macos_version_minor"),
    )
    browser_installed: Mapped[bool | None] = mapped_column(default=None, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "mac",
    }
