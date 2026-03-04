from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.buildbase import BuildBase


class Build(BuildBase):
    __tablename__ = "modernbuild"

    id: Mapped[UUID] = mapped_column(ForeignKey("build.id"), primary_key=True, sort_order=-100)

    manufacturer: Mapped[str | None] = mapped_column(nullable=True, default=None)

    __mapper_args__ = {
        "polymorphic_identity": "modernbuild",
    }