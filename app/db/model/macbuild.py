from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model import BuildBase


class MacBuild(BuildBase):
    __tablename__ = "macbuild"

    id: Mapped[UUID] = mapped_column(ForeignKey("build.id"), primary_key=True, sort_order=-100)

    __mapper_args__ = {
        "polymorphic_identity": "macbuild",
    }
