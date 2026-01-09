import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from litestar import get
from litestar.controller import Controller
from litestar.di import Provide

from app.db.repository import MemoryModuleRepository, provide_memory_repo, provide_storage_repo, \
    StorageDiskRepository, DisplayRepository, provide_display_repo, BatteryRepository, provide_battery_repo
from app.db.service.build import provide_build_service, BuildService
from app.price.dto import MemoryModulePrice, StorageDiskPrice, DisplayPrice, BatteryPrice, BuildPrice
from app.price.model.pricing import PricingModel, provide_default_pricing_model


class PriceController(Controller):
    path = "price"

    dependencies = {
        "build_service": Provide(provide_build_service),
        "memory_repo": Provide(provide_memory_repo),
        "storage_repo": Provide(provide_storage_repo),
        "display_repo": Provide(provide_display_repo),
        "battery_repo": Provide(provide_battery_repo),
        "model": Provide(provide_default_pricing_model),
    }

    @get("/{build_id: uuid}")
    async def calculate_build_price(self, build_id: UUID, build_service: BuildService, model: PricingModel) -> BuildPrice:
        build = await build_service.get(build_id)
        price = await model.compute(build)

        build.price = price.price
        build.priced_at = datetime.datetime.now(tz=ZoneInfo("UTC"))

        await build_service.update(build, auto_commit=True)

        return price


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


    @get("/display/{display_id: uuid}")
    async def calculate_display_price(self, display_id: UUID, display_repo: DisplayRepository, model: PricingModel) -> DisplayPrice:
        display = await display_repo.get(display_id)
        price = DisplayPrice(display=display)
        price.price = model.display_model.compute(display)
        return price


    @get("/battery/{battery_id: uuid}")
    async def calculate_battery_price(self, battery_id: UUID, battery_repo: BatteryRepository, model: PricingModel) -> BatteryPrice:
        battery = await battery_repo.get(battery_id)
        price = BatteryPrice(battery=battery)
        price.price = model.battery_model.compute(battery)
        return price

