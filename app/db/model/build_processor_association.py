from advanced_alchemy.base import UUIDBase
from pygments.lexer import default
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from app.db.model.processor import Processor


class BuildProcessorAssociation(UUIDBase):
    __tablename__ = "processor_build_associations"

    build_id = mapped_column(ForeignKey("build.id", ondelete="CASCADE"), nullable=False)
    processor_id = mapped_column(ForeignKey("processor.id", ondelete="CASCADE"), nullable=False)

    upgradable: Mapped[bool] = mapped_column(nullable=False, default=True)

    processor: Mapped[Processor] = relationship(lazy="selectin")