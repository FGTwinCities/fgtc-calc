import datetime
from typing import Sequence
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import InternalServerException, ValidationException

from app.db.model.processor import Processor
from app.db.service.processor import provide_processor_service, ProcessorService
from app.ebay.price_estimator import EbayPriceEstimator
from app.lib.math import clamp
from app.passmark.passmark_scraper import PassmarkScraper
from app.passmark.schema import PassmarkPECoreCpuDetails

MAX_SEARCH_ITEMS = 100


class ProcessorController(Controller):
    path = "build/processor"

    dependencies = {
        "processor_service": Provide(provide_processor_service),
    }


    @get("/")
    async def get_processors(self, processor_service: ProcessorService) -> Sequence[Processor]:
        return await processor_service.list()


    @get("/{processor_id: uuid}")
    async def get_processor(self, processor_id: UUID, processor_service: ProcessorService) -> Processor:
        return await processor_service.get(processor_id)


    @post("/")
    async def create_processor(self, processor_service: ProcessorService, data: Processor) -> Processor:
        processor = await processor_service.create(data)
        return processor


    @delete("/{processor_id: uuid}")
    async def delete_processor(self, processor_id: UUID, processor_service: ProcessorService) -> None:
        await processor_service.delete(processor_id)


    @get("/search")
    async def search_processors(self, q: str, processor_service: ProcessorService, limit: int = 50) -> Sequence[Processor]:
        return await processor_service.list(
            Processor.model.icontains(q),
            OrderBy("model"),
            LimitOffset(limit=clamp(limit, 0, MAX_SEARCH_ITEMS), offset=0),
        )

    @get("/{processor_id: uuid}/update_specs")
    async def update_processor_specs(self, processor_id: UUID, processor_service: ProcessorService, rebind: bool = False) -> Processor:
        processor = await processor_service.get(processor_id)

        scraper = PassmarkScraper()

        if not processor.passmark_id or rebind:
            search_results = await scraper.search_cpu(processor.model)
            if len(search_results) <= 0:
                raise ValidationException("CPU not found on Passmark CPU list.")

            processor.passmark_id = search_results[0].passmark_id

        specs = await scraper.retrieve_cpu(processor.passmark_id)

        processor.multithread_score = specs.multithread_score
        processor.single_thread_score = specs.single_thread_score

        if specs is PassmarkPECoreCpuDetails:
            processor.performance_core_count = specs.performance_cores.cores
            processor.performance_thread_count = specs.performance_cores.threads
            processor.performance_clock = specs.performance_cores.clock
            processor.performance_turbo_clock = specs.performance_cores.turbo_clock
            processor.efficient_core_count = specs.efficient_cores.cores
            processor.efficient_thread_count = specs.efficient_cores.threads
            processor.efficient_clock = specs.efficient_cores.clock
            processor.efficient_turbo_clock = specs.efficient_cores.turbo_clock
        else:
            processor.performance_core_count = specs.cores
            processor.performance_thread_count = specs.threads
            processor.performance_clock = specs.clock
            processor.performance_turbo_clock = specs.turbo_clock

        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor


    @get("/{processor_id: uuid}/update_price")
    async def update_processor_price(self, processor_id: UUID, processor_service: ProcessorService) -> Processor:
        processor = await processor_service.get(processor_id)

        estimator = EbayPriceEstimator()
        price = await estimator.estimate_processor(processor)
        processor.price = price
        processor.priced_at = datetime.datetime.now(tz=ZoneInfo("UTC"))

        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor
