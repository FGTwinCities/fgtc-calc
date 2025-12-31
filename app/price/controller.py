from uuid import UUID

from litestar import get
from litestar.controller import Controller
from litestar.di import Provide

from app.build.repository import MemoryModuleRepository, provide_memory_repo, provide_storage_repo, StorageDiskRepository
from app.price.dto import MemoryModulePrice, StorageDiskPrice
from app.price.model.pricing import PricingModel, provide_default_pricing_model


class PriceController(Controller):
    path = "price"

    dependencies = {
        "memory_repo": Provide(provide_memory_repo),
        "storage_repo": Provide(provide_storage_repo),
        "model": Provide(provide_default_pricing_model),
    }

    @get("/memory/{module_id: uuid}")
    async def calculate_memory_price(self, module_id: UUID, memory_repo: MemoryModuleRepository, model: PricingModel) -> MemoryModulePrice:
        module = await memory_repo.get(module_id)
        price = MemoryModulePrice(module=module)
        module_price = model.memory_model.compute(module)
        price.price = model.compute_adjustment(module_price)
        return price


    @get("/storage/{disk_id: uuid}")
    async def calculate_storage_price(self, disk_id: UUID, storage_repo: StorageDiskRepository, model: PricingModel) -> StorageDiskPrice:
        disk = await storage_repo.get(disk_id)
        price = StorageDiskPrice(disk=disk)
        disk_price = model.storage_model.compute(disk)
        price.price = model.compute_adjustment(disk_price)
        return price
