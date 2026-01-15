import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from litestar import get
from litestar.controller import Controller
from litestar.di import Provide

from app.build.controller.processor import update_processor_specs
from app.db.model import Processor, GraphicsProcessor, MemoryModule, StorageDisk, Display, Battery
from app.db.repository import MemoryModuleRepository, provide_memory_repo, provide_storage_repo, \
    StorageDiskRepository, DisplayRepository, provide_display_repo, BatteryRepository, provide_battery_repo
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.db.service.processor import provide_processor_service, ProcessorService
from app.ebay.price_estimator import EbayPriceEstimator
from app.lib.datetime import now
from app.price.dto import BuildPrice, WithPrice
from app.price.model.pricing import PricingModel, provide_default_pricing_model

PRICE_VALID_TIMESPAN = datetime.timedelta(days=7)


async def _update_processor_price(processor: Processor, model: PricingModel) -> None:
    estimator = EbayPriceEstimator(model)
    price = await estimator.estimate_processor(processor)
    processor.price = price
    processor.priced_at = now()


async def _update_graphics_price(graphics: GraphicsProcessor, model: PricingModel) -> None:
    estimator = EbayPriceEstimator(model)
    price = await estimator.estimate_graphics(graphics)
    graphics.price = price
    graphics.priced_at = now()


class PriceController(Controller):
    path = "price"

    dependencies = {
        "build_service": Provide(provide_build_service),
        "processor_service": Provide(provide_processor_service),
        "graphics_service": Provide(provide_graphics_service),
        "memory_repo": Provide(provide_memory_repo),
        "storage_repo": Provide(provide_storage_repo),
        "display_repo": Provide(provide_display_repo),
        "battery_repo": Provide(provide_battery_repo),
        "model": Provide(provide_default_pricing_model),
    }

    @get("/{build_id: uuid}")
    async def calculate_build_price(self, build_id: UUID, build_service: BuildService, processor_service: ProcessorService, model: PricingModel) -> BuildPrice:
        build = await build_service.get(build_id)

        # If prices/specs for associated processors or GPUs are not present or too old, update those first
        for processor in build.processors:
            if not processor.passmark_id:
                await update_processor_specs(processor)
            if not processor.price or not processor.priced_at or now() > (processor.priced_at + PRICE_VALID_TIMESPAN):
                await _update_processor_price(processor, model)

        for gpu in build.graphics:
            if not gpu.price or gpu.priced_at or now() > (gpu.priced_at + PRICE_VALID_TIMESPAN):
                await _update_graphics_price(gpu, model)

        price = await model.compute(build)

        build.price = price.price
        build.priced_at = datetime.datetime.now(tz=ZoneInfo("UTC"))

        await build_service.update(build, auto_commit=True)

        return price


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


    @get("/processor/{processor_id: uuid}")
    async def update_processor_price(self, processor_id: UUID, processor_service: ProcessorService, model: PricingModel) -> Processor:
        processor = await processor_service.get(processor_id)

        await _update_processor_price(processor, model)

        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor


    @get("/graphics/{gpu_id: uuid}")
    async def update_gpu_price(self, gpu_id: UUID, graphics_service: GraphicsProcessorService, model: PricingModel) -> GraphicsProcessor:
        gpu = await graphics_service.get(gpu_id)

        await _update_graphics_price(gpu, model)

        await graphics_service.update(gpu, auto_commit=True, auto_refresh=True)
        return gpu

