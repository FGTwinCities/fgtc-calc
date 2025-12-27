from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession


class MemoryPricingModel:
    size_func: Polynomial
    speed_func: Polynomial

    def compute(self, size: int, speed: int) -> float:
        size_price = self.size_func(float(size) / 1000)
        speed_price = self.speed_func(speed)
        return size_price + speed_price


async def provide_memory_pricing_model(db_session: AsyncSession) -> MemoryPricingModel:
    model = MemoryPricingModel()
    #TODO: Store and retrieve from database
    model.size_func = Polynomial([0, 7.5, 0])
    model.speed_func = Polynomial([0, 0.003, 0])
    return model