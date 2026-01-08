from numpy.polynomial.polynomial import Polynomial
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.memory import MemoryModule
from app.lib.math import mb2gb
from app.price.dto import MemoryModulePrice


class MemoryPricingModel:
    size_func: Polynomial
    speed_func: Polynomial

    def compute(self, module: MemoryModule) -> float:
        size_price = self.size_func(mb2gb(module.size))
        speed_price = self.speed_func(module.clock)
        return size_price + speed_price

    def compute_wrapped(self, module: MemoryModule) -> MemoryModulePrice:
        return MemoryModulePrice(module=module, price=self.compute(module))


async def provide_memory_pricing_model(db_session: AsyncSession) -> MemoryPricingModel:
    model = MemoryPricingModel()
    #TODO: Store and retrieve from database
    model.size_func = Polynomial([0, 7.5, 0])
    model.speed_func = Polynomial([0, 0.003, 0])
    return model