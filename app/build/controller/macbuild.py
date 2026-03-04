from typing import Sequence
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import Controller, get, post, patch
from litestar.di import Provide
from litestar.response import Template

from app.build.controller.build import _deduplicate_processors, _deduplicate_graphics_processors
from app.build.controller.common import _convert_create_dto_to_model
from app.build.schema import MacBuildCreate
from app.db.model import MacBuild
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.db.service.processor import provide_processor_service, ProcessorService


class MacBuildController(Controller):
    path = "build/mac"

    dependencies = {
        "build_service": Provide(provide_build_service),
        "processor_service": Provide(provide_processor_service),
        "graphics_service": Provide(provide_graphics_service),
    }

    @get("/create")
    async def create_build_page(self) -> Template:
        return Template("mac/create.html")

    @get("/")
    async def get_mac_builds(self, build_service: BuildService, offset: int = 0, page_size: int = 25) -> Sequence[MacBuild]:
        return await build_service.list(
            LimitOffset(offset=offset, limit=page_size),
            OrderBy(MacBuild.created_at, "desc"),
            MacBuild.class_type.contains("macbuild"),
        )

    @post("/")
    async def create_mac_build(self, build_service: BuildService, processor_service: ProcessorService, graphics_service: GraphicsProcessorService, data: MacBuildCreate) -> MacBuild:
        build = MacBuild()

        await _deduplicate_processors(build, data, processor_service)
        await _deduplicate_graphics_processors(build, data, graphics_service)
        _convert_create_dto_to_model(build, data)

        await build_service.create(build, auto_commit=True, auto_refresh=True)
        return build


    @patch("/{build_id: uuid}")
    async def update_mac_build(self, build_id: UUID, build_service: BuildService, processor_service: ProcessorService, graphics_service: GraphicsProcessorService, data: MacBuildCreate) -> MacBuild:
        build = await build_service.get(build_id)
        assert isinstance(build, MacBuild)

        build.processors = []
        await _deduplicate_processors(build, data, processor_service)

        build.graphics = []
        await _deduplicate_graphics_processors(build, data, graphics_service)
        _convert_create_dto_to_model(build, data)

        build = await build_service.update(build, auto_commit=True, auto_refresh=True)
        return build
