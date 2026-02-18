from dataclasses import dataclass, field
from typing import Optional, Any, Generic, TypeVar

from app.db.model.build import Build

"""
Data Transfer object schemas used to return pricing information to the frontend.
"""

T = TypeVar("T")

@dataclass
class WithPrice(Generic[T]):
    price: float
    item: T


@dataclass
class Price:
    price: Optional[float] = None


@dataclass
class BuildPrice(Price):
    build: Build = None
    component_pricing: list[Any] = field(default_factory=list)


@dataclass
class PriceAdjustment(Price):
    comment: str | None = None
