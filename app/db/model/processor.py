from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped


@dataclass
class Processor(UUIDAuditBase):
    __tablename__ = "processor"

    model: Mapped[str]
    #TODO: Specifications
