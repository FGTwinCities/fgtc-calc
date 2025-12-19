from uuid import UUID

from litestar import get
from litestar.controller import Controller
from litestar.di import Provide

from app.build.repository import MemoryModuleRepository, provide_memory_repo
from app.price.dto import MemoryModulePrice, Price


class PriceController(Controller):
    path = "price"

    dependencies = {
        "memory_repo": Provide(provide_memory_repo),
    }

    @get("/memory/{module_id: uuid}")
    async def calculate_memory_price(self, module_id: UUID, memory_repo: MemoryModuleRepository) -> MemoryModulePrice:
        module = await memory_repo.get(module_id)
        price = MemoryModulePrice(module=module)
        return price
