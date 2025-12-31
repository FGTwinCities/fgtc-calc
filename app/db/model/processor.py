from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.mixins.price import PriceMixin


@dataclass
class Processor(UUIDAuditBase, PriceMixin):
    __tablename__ = "processor"

    model: Mapped[str] = mapped_column(nullable=False, unique=True)
    #TODO: Specifications
