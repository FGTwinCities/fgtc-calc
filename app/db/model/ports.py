from dataclasses import dataclass

from advanced_alchemy.base import AdvancedDeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped


@dataclass
class Ports(AdvancedDeclarativeBase):
    __tablename__ = "ports"
    build_id = mapped_column(ForeignKey("build.id", ondelete="CASCADE"), primary_key=True)

    hdmi: Mapped[int] = mapped_column(default=0)
    dp: Mapped[int] = mapped_column(default=0)
    dvi: Mapped[int] = mapped_column(default=0)
    vga: Mapped[int] = mapped_column(default=0)
    sd: Mapped[int] = mapped_column(default=0)
    usb: Mapped[int] = mapped_column(default=0)
    usb3: Mapped[int] = mapped_column(default=0)
    usbc: Mapped[int] = mapped_column(default=0)
    thunderbolt: Mapped[int] = mapped_column(default=0)
