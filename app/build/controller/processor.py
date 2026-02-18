import re
from typing import Sequence
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import ValidationException

from app.db.model.processor import Processor
from app.db.service.processor import provide_processor_service, ProcessorService
from app.lib.math import clamp
from app.passmark.passmark_scraper import PassmarkScraper
from app.passmark.schema import PassmarkPECoreCpuDetails

MAX_SEARCH_ITEMS = 100


async def update_processor_specs(processor: Processor, rebind: bool = False):
    """
    Searches Passmark (cpubenchmark.net) for a given processor by name, and adds specifications to the CPU object if found.
    :param processor: CPU to search for
    :param rebind: set to True to force searching by model instead of using cached Passmark ID
    """
    scraper = PassmarkScraper()

    if not processor.passmark_id or rebind:
        search_results = await scraper.search_cpu(processor.model)
        if len(search_results) <= 0:
            raise ValidationException("CPU not found on Passmark CPU list.")

        processor.passmark_id = search_results[0].passmark_id

    specs = await scraper.retrieve_cpu_by_id(processor.passmark_id)

    # Remove the '@ x.y Ghz' from the end of Intel CPU models
    specs.name = re.sub(r'\s*@\s*\d+\.?\d*\+?\s?[MmGgHhZz]+$', '', specs.name)

    processor.model = specs.name
    processor.multithread_score = specs.score
    processor.single_thread_score = specs.single_thread_score

    if isinstance(specs, PassmarkPECoreCpuDetails):
        processor.performance_core_count = specs.performance_cores.cores
        processor.performance_thread_count = specs.performance_cores.threads
        if specs.performance_cores.clock:
            processor.performance_clock = round(specs.performance_cores.clock * 1000)
        if specs.performance_cores.turbo_clock:
            processor.performance_turbo_clock = round(specs.performance_cores.turbo_clock * 1000)
        processor.efficient_core_count = specs.efficient_cores.cores
        processor.efficient_thread_count = specs.efficient_cores.threads
        if specs.efficient_cores.clock:
            processor.efficient_clock = round(specs.efficient_cores.clock * 1000)
        if specs.efficient_cores.turbo_clock:
            processor.efficient_turbo_clock = round(specs.efficient_cores.turbo_clock * 1000)
    else:
        processor.performance_core_count = specs.cores
        processor.performance_thread_count = specs.threads
        if specs.clock:
            processor.performance_clock = round(specs.clock * 1000)
        if specs.turbo_clock:
            processor.performance_turbo_clock = round(specs.turbo_clock * 1000)


class ProcessorController(Controller):
    """
    Route controller class for CRUD operations on CPU objects
    """
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
        await update_processor_specs(processor, rebind)
        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor