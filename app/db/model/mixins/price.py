import datetime

from advanced_alchemy.types.datetime import DateTimeUTC
from sqlalchemy.orm import Mapped, mapped_column, declarative_mixin


@declarative_mixin
class PriceMixin:
    price: Mapped[float | None] = mapped_column(nullable=True, default=None)

    priced_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTimeUTC(timezone=True),
        nullable=True,
        default=None,
        sort_order=3002,
    )
