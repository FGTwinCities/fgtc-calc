from dataclasses import dataclass
from typing import TypeVar, Generic
from uuid import UUID

from litestar import get
from litestar.controller import Controller
from litestar.di import Provide

from app.build.repository import MemoryModuleRepository, provide_memory_repo, provide_storage_repo, \
    provide_display_repo, provide_battery_repo, StorageDiskRepository, DisplayRepository, BatteryRepository
from app.db.model.battery import Battery
from app.db.model.display import Display
from app.db.model.memory import MemoryModule
from app.db.model.storage import StorageDisk
from app.price.model.pricing import PricingModel, provide_default_pricing_model

T = TypeVar("T")


@dataclass
class WithPrice(Generic[T]):
    price: float
    item: T


class PriceController(Controller):
    path = "price"

    dependencies = {
        "memory_repo": Provide(provide_memory_repo),
        "storage_repo": Provide(provide_storage_repo),
        "display_repo": Provide(provide_display_repo),
        "battery_repo": Provide(provide_battery_repo),
        "model": Provide(provide_default_pricing_model),
    }

    @get("/memory/{module_id: uuid}")
    async def calculate_memory_price(self, module_id: UUID, memory_repo: MemoryModuleRepository, model: PricingModel) -> WithPrice[MemoryModule]:
        module = await memory_repo.get(module_id)
        price = model.memory_model.compute(module)
        return WithPrice(price=price, item=module)


    @get("/storage/{disk_id: uuid}")
    async def calculate_storage_price(self, disk_id: UUID, storage_repo: StorageDiskRepository, model: PricingModel) -> WithPrice[StorageDisk]:
        disk = await storage_repo.get(disk_id)
        price = model.storage_model.compute(disk)
        return WithPrice(price=price, item=disk)


    @get("/display/{display_id: uuid}")
    async def calculate_display_price(self, display_id: UUID, display_repo: DisplayRepository, model: PricingModel) -> WithPrice[Display]:
        display = await display_repo.get(display_id)
        price = model.display_model.calculate(display)
        return WithPrice(price=price, item=display)


    @get("/battery/{battery_id: uuid}")
    async def calculate_battery_price(self, battery_id: UUID, battery_repo: BatteryRepository, model: PricingModel) -> WithPrice[Battery]:
        battery = await battery_repo.get(battery_id)
        price = model.battery_model.calculate(battery)
        return WithPrice(price=price, item=battery)

