from dataclasses import dataclass

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column

from app.db.model.mixins.price import PriceMixin


@dataclass
class Processor(UUIDAuditBase, PriceMixin):
    __tablename__ = "processor"

    model: Mapped[str] = mapped_column(nullable=False, unique=True)

    performance_core_count: Mapped[int | None] = mapped_column(nullable=True)
    performance_thread_count: Mapped[int | None] = mapped_column(nullable=True)
    performance_clock: Mapped[int | None] = mapped_column(nullable=True)
    performance_turbo_clock: Mapped[int | None] = mapped_column(nullable=True)
    efficient_core_count: Mapped[int | None] = mapped_column(nullable=True)
    efficient_thread_count: Mapped[int | None] = mapped_column(nullable=True)
    efficient_clock: Mapped[int | None] = mapped_column(nullable=True)
    efficient_turbo_clock: Mapped[int | None] = mapped_column(nullable=True)

    passmark_id: Mapped[int | None] = mapped_column(nullable=True)
    passmark_multithread_score: Mapped[int | None] = mapped_column(nullable=True)
    passmark_single_thread_score: Mapped[int | None] = mapped_column(nullable=True)

    geekbench_id: Mapped[int | None] = mapped_column(nullable=True)
    geekbench_multithread_score: Mapped[int | None] = mapped_column(nullable=True)
    geekbench_single_thread_score: Mapped[int | None] = mapped_column(nullable=True)

    def __hash__(self):
        return hash(self.id)
