from advanced_alchemy.base import UUIDBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from app.db.model.processor import Processor


class BuildProcessorAssociation(UUIDBase):
    __tablename__ = "processor_build_associations"

    build_id = mapped_column(ForeignKey("build.id"))
    processor_id = mapped_column(ForeignKey("processor.id"))

    processor: Mapped[Processor] = relationship(lazy="selectin")