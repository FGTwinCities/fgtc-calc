from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.mixins.price import PriceMixin


@dataclass
class Processor(UUIDAuditBase, PriceMixin):
    __tablename__ = "processor"

    model: Mapped[str] = mapped_column(nullable=False, unique=True)

    passmark_id: Mapped[int | None] = mapped_column(nullable=True)
    multithread_score: Mapped[int | None] = mapped_column(nullable=True)
    single_thread_score: Mapped[int | None] = mapped_column(nullable=True)
    performance_core_count: Mapped[int | None] = mapped_column(nullable=True)
    performance_thread_count: Mapped[int | None] = mapped_column(nullable=True)
    performance_clock: Mapped[int | None] = mapped_column(nullable=True)
    performance_turbo_clock: Mapped[int | None] = mapped_column(nullable=True)
    efficient_core_count: Mapped[int | None] = mapped_column(nullable=True)
    efficient_thread_count: Mapped[int | None] = mapped_column(nullable=True)
    efficient_clock: Mapped[int | None] = mapped_column(nullable=True)
    efficient_turbo_clock: Mapped[int | None] = mapped_column(nullable=True)
