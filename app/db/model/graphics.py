from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.mixins.price import PriceMixin


@dataclass
class GraphicsProcessor(UUIDAuditBase, PriceMixin):
    __tablename__ = "graphics_processor"

    model: Mapped[str] = mapped_column(nullable=False, unique=True)

    passmark_id: Mapped[int | None] = mapped_column(nullable=True)
    passmark_score: Mapped[int | None] = mapped_column(nullable=True)
    passmark_score_g2d: Mapped[int | None] = mapped_column(nullable=True)

    geekbench_id: Mapped[int | None] = mapped_column(nullable=True)
    geekbench_score: Mapped[int | None] = mapped_column(nullable=True)

    def __hash__(self):
        return hash(self.id)
