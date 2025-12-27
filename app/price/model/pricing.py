from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.price.model.memory import MemoryPricingModel, provide_memory_pricing_model


class PricingModel:
    adjustment: Polynomial = Polynomial([0, 1, 0])

    def compute_adjustment(self, price: float) -> float:
        return self.adjustment(price)

    memory_model: MemoryPricingModel


async def provide_default_pricing_model(db_session: AsyncSession) -> PricingModel:
    model = PricingModel()
    model.adjustment = Polynomial([0, 0.5, 0])
    model.memory_model = await provide_memory_pricing_model(db_session)
    return model
