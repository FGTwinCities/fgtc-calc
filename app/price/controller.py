from uuid import UUID

from litestar import get
from litestar.controller import Controller
from litestar.di import Provide

from app.build.repository import MemoryModuleRepository, provide_memory_repo
from app.price.dto import MemoryModulePrice
from app.price.model.pricing import PricingModel, provide_default_pricing_model


class PriceController(Controller):
    path = "price"

    dependencies = {
        "memory_repo": Provide(provide_memory_repo),
        "model": Provide(provide_default_pricing_model),
    }

    @get("/memory/{module_id: uuid}")
    async def calculate_memory_price(self, module_id: UUID, memory_repo: MemoryModuleRepository, model: PricingModel) -> MemoryModulePrice:
        module = await memory_repo.get(module_id)
        price = MemoryModulePrice(module=module)

        module_price = model.memory_model.compute(module.size, module.clock)
        price.price = model.compute_adjustment(module_price)

        return price
