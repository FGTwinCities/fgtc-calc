from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.mixins.price import PriceMixin


@dataclass
class GraphicsProcessor(UUIDAuditBase, PriceMixin):
    __tablename__ = "graphics_processor"

    model: Mapped[str] = mapped_column(nullable=False, unique=False) #TODO: Make unique and merge

    passmark_id: Mapped[int | None] = mapped_column(nullable=True)
    score: Mapped[int | None] = mapped_column(nullable=True)
    score_g2d: Mapped[int | None] = mapped_column(nullable=True)

    def __hash__(self):
        return hash(self.id)
