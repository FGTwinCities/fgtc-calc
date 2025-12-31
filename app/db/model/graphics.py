from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped


@dataclass
class GraphicsProcessor(UUIDAuditBase):
    __tablename__ = "graphics_processor"

    model: Mapped[str]
    #TODO: Specifications