from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.mixins.price import PriceMixin


@dataclass
class GraphicsProcessor(UUIDAuditBase, PriceMixin):
    __tablename__ = "graphics_processor"

    model: Mapped[str] = mapped_column(nullable=False, unique=True)
    #TODO: Specifications
