from advanced_alchemy.base import UUIDBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, relationship, Mapped

from app.db.model.graphics import GraphicsProcessor


class BuildGraphicsAssociation(UUIDBase):
    __tablename__ = "graphics_build_associations"

    build_id = mapped_column(ForeignKey("build.id"))
    graphics_id = mapped_column(ForeignKey("graphics_processor.id"))

    graphics: Mapped[GraphicsProcessor] = relationship(lazy="selectin")