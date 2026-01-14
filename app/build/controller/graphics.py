import datetime
from typing import Sequence
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide

from app.db.model.graphics import GraphicsProcessor
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.ebay.price_estimator import EbayPriceEstimator
from app.lib.math import clamp

MAX_SEARCH_ITEMS = 100


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
