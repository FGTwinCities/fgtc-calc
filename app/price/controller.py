import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from litestar import get, post
from litestar.controller import Controller
from litestar.di import Provide

from app.build.controller.processor import update_processor_specs
from app.db.model import Processor, GraphicsProcessor, MemoryModule, StorageDisk, Display, Battery, Build
from app.db.repository import MemoryModuleRepository, provide_memory_repo, provide_storage_repo, \
    StorageDiskRepository, DisplayRepository, provide_display_repo, BatteryRepository, provide_battery_repo
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.db.service.processor import provide_processor_service, ProcessorService
from app.ebay.price_estimator import EbayPriceEstimator
from app.lib.datetime import now
from app.price.dto import BuildPrice, WithPrice, Price
from app.price.model.service import PricingModelService

PRICE_VALID_TIMESPAN = datetime.timedelta(days=7)


async def _update_processor_price(processor: Processor) -> None:
    estimator = EbayPriceEstimator()
    price = await estimator.estimate_processor(processor)
    processor.price = price
    processor.priced_at = now()


async def _update_graphics_price(graphics: GraphicsProcessor) -> None:
    estimator = EbayPriceEstimator()
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
    }

    @get("/{build_id: uuid}")
    async def calculate_build_price(self, build_id: UUID, build_service: BuildService, processor_service: ProcessorService, pricing_model_service: PricingModelService) -> BuildPrice:
        model = await pricing_model_service.get_model()
        build = await build_service.get(build_id)

        # If prices/specs for associated processors or GPUs are not present or too old, update those first
        for processor in build.processors:
            if not processor.passmark_id:
                await update_processor_specs(processor)
            if not processor.price or not processor.priced_at or now() > (processor.priced_at + PRICE_VALID_TIMESPAN):
                await _update_processor_price(processor)

        for gpu in build.graphics:
            if not gpu.price or gpu.priced_at or now() > (gpu.priced_at + PRICE_VALID_TIMESPAN):
                await _update_graphics_price(gpu)

        price = await model.compute(build)

        build.price = price.price
        build.priced_at = datetime.datetime.now(tz=ZoneInfo("UTC"))

        await build_service.update(build, auto_commit=True)

        return price


    @get("/memory/{module_id: uuid}")
    async def calculate_memory_price(self, module_id: UUID, memory_repo: MemoryModuleRepository, pricing_model_service: PricingModelService) -> WithPrice[MemoryModule]:
        model = await pricing_model_service.get_model()
        module = await memory_repo.get(module_id)
        price = model.memory_model.compute(module)
        return WithPrice(price=price, item=module)


    @get("/storage/{disk_id: uuid}")
    async def calculate_storage_price(self, disk_id: UUID, storage_repo: StorageDiskRepository, pricing_model_service: PricingModelService) -> WithPrice[StorageDisk]:
        model = await pricing_model_service.get_model()
        disk = await storage_repo.get(disk_id)
        price = model.storage_model.compute(disk)
        return WithPrice(price=price, item=disk)


    @get("/display/{display_id: uuid}")
    async def calculate_display_price(self, display_id: UUID, display_repo: DisplayRepository, pricing_model_service: PricingModelService) -> WithPrice[Display]:
        model = await pricing_model_service.get_model()
        display = await display_repo.get(display_id)
        price = model.display_model.calculate(display)
        return WithPrice(price=price, item=display)


    @get("/battery/{battery_id: uuid}")
    async def calculate_battery_price(self, battery_id: UUID, battery_repo: BatteryRepository, pricing_model_service: PricingModelService) -> WithPrice[Battery]:
        model = await pricing_model_service.get_model()
        battery = await battery_repo.get(battery_id)
        price = model.battery_model.calculate(battery)
        return WithPrice(price=price, item=battery)


    @get("/processor/{processor_id: uuid}")
    async def update_processor_price(self, processor_id: UUID, processor_service: ProcessorService) -> Processor:
        processor = await processor_service.get(processor_id)

        await _update_processor_price(processor)

        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor


    @get("/graphics/{gpu_id: uuid}")
    async def update_gpu_price(self, gpu_id: UUID, graphics_service: GraphicsProcessorService) -> GraphicsProcessor:
        gpu = await graphics_service.get(gpu_id)

        await _update_graphics_price(gpu)

        await graphics_service.update(gpu, auto_commit=True, auto_refresh=True)
        return gpu

    @post("/{build_id: uuid}")
    async def set_build_price(self, build_id: UUID, data: Price, build_service: BuildService) -> Build:
        build = await build_service.get(build_id)
        build.price = data.price
        await build_service.update(build, auto_commit=True, auto_refresh=True)
        return build

    @post("/processor/{processor_id: uuid}")
    async def set_processor_price(self, processor_id: UUID, data: Price, processor_service: ProcessorService) -> Processor:
        processor = await processor_service.get(processor_id)
        processor.price = data.price
        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor

    @post("/graphics/{gpu_id: uuid}")
    async def set_gpu_price(self, gpu_id: UUID, data: Price, graphics_service: GraphicsProcessorService) -> GraphicsProcessor:
        gpu = await graphics_service.get(gpu_id)
        gpu.price = data.price
        await graphics_service.update(gpu, auto_commit=True, auto_refresh=True)
        return gpu

    @get("/generate_model")
    async def generate_pricing_model(self, pricing_model_service: PricingModelService) -> dict:
        await pricing_model_service.generate_model()
        return {"message": "Pricing model generated"}
