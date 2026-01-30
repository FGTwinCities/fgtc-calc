import logging
from typing import Sequence
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.exceptions import ValidationException

from app.db.model.graphics import GraphicsProcessor
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.extern.benchmark.geekbench.geekbench import GeekbenchDataSource
from app.lib.math import clamp
from app.extern.benchmark.passmark import PassmarkScraper

MAX_SEARCH_ITEMS = 100


async def update_graphics_specs(gpu: GraphicsProcessor, rebind: bool = False):
    try:
        scraper = PassmarkScraper()
        await scraper.update_gpu(gpu, rebind)
    except (ValidationException | RuntimeError) as e:
        logging.warn("Failed to update CPU specifications from Passmark", e)

    try:
        source = GeekbenchDataSource()
        await source.update_gpu(gpu, rebind)
    except (ValidationException | RuntimeError) as e:
        logging.warn("Failed to update CPU specifications from Geekbench", e)


class GraphicsController(Controller):
    path = "build/graphics"

    dependencies = {
        "graphics_service": Provide(provide_graphics_service),
    }


    @get("/")
    async def get_graphics(self, graphics_service: GraphicsProcessorService) -> Sequence[GraphicsProcessor]:
        return await graphics_service.list()


    @get("/{gpu_id: uuid}")
    async def get_gpu(self, gpu_id: UUID, graphics_service: GraphicsProcessorService) -> GraphicsProcessor:
        return await graphics_service.get(gpu_id)


    @post("/")
    async def create_gpu(self, data: GraphicsProcessor, graphics_service: GraphicsProcessorService) -> GraphicsProcessor:
        data = await graphics_service.create(data)
        return data


    @delete("/{gpu_id: uuid}")
    async def delete_gpu(self, gpu_id: UUID, graphics_service: GraphicsProcessorService) -> None:
        await graphics_service.delete(gpu_id)


    @get("/search")
    async def search_gpu(self, q: str, graphics_service: GraphicsProcessorService, limit: int = 50) -> Sequence[GraphicsProcessor]:
        return await graphics_service.list(
            GraphicsProcessor.model.icontains(q),
            OrderBy("model"),
            LimitOffset(limit=clamp(limit, 0, MAX_SEARCH_ITEMS), offset=0),
        )


    @get("/{gpu_id: uuid}/update_specs")
    async def update_gpu_specs(self, gpu_id: UUID, graphics_service: GraphicsProcessorService, rebind: bool = False) -> GraphicsProcessor:
        gpu = await graphics_service.get(gpu_id)
        await update_graphics_specs(gpu, rebind)
        await graphics_service.update(gpu, auto_commit=True, auto_refresh=True)
        return gpu
