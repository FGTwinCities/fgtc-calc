from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.memory import MemoryModule


def memory_model_func(x: tuple[float, float], a: float, b: float, c: float, d: float, e: float) -> float:
    x_1, x_2 = x
    return ((a * x_1) + (b * x_1 ** 2) + (c * x_2) + (d * x_2 ** 2) + e)

class MemoryPricingModel:
    parameters = (1, 1, 1, 1, 1)

    def compute(self, module: MemoryModule) -> float:
        return memory_model_func((module.size, module.clock), *self.parameters)


async def provide_memory_pricing_model(db_session: AsyncSession) -> MemoryPricingModel:
    return MemoryPricingModel()