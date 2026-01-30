import logging
from typing import Sequence
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import ValidationException

from app.db.model.processor import Processor
from app.db.service.processor import provide_processor_service, ProcessorService
from app.extern.benchmark.geekbench.geekbench import GeekbenchDataSource
from app.lib.math import clamp
from app.extern.benchmark.passmark import PassmarkScraper
from app.extern.benchmark.passmark import PassmarkPECoreCpuDetails

MAX_SEARCH_ITEMS = 100


async def update_processor_specs(processor: Processor, rebind: bool = False):
    try:
        scraper = PassmarkScraper()
        await scraper.update_cpu(processor, rebind)
    except RuntimeError as e:
        logging.warn("Failed to update CPU specifications from Passmark", e)

    try:
        source = GeekbenchDataSource()
        await source.update_cpu(processor, rebind)
    except RuntimeError as e:
        logging.warn("Failed to update CPU specifications from Geekbench", e)


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
        await update_processor_specs(processor, rebind)
        await processor_service.update(processor, auto_commit=True, auto_refresh=True)
        return processor