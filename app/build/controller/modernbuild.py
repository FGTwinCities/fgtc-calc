from typing import Sequence
from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import Controller, get, patch, post
from litestar.di import Provide
from litestar.response import Template

from app.build.controller.common import _deduplicate_processors, _deduplicate_graphics_processors, \
    _convert_create_dto_to_model
from app.build.schema import ModernBuildCreate, ModernBuildRetrieve
from app.db.model import Build
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.db.service.processor import provide_processor_service, ProcessorService


class ModernBuildController(Controller):
    path = "build/modern"

    dependencies = {
        "build_service": Provide(provide_build_service),
        "processor_service": Provide(provide_processor_service),
        "graphics_service": Provide(provide_graphics_service),
    }

    @get("/create")
    async def create_build_page(self) -> Template:
        """ Render the create build form page """
        return Template("build/modern.html")

    @get("/")
    async def get_modern_builds(self, build_service: BuildService, offset: int = 0, page_size: int = 25) -> Sequence[ModernBuildRetrieve]:
        builds = await build_service.list(
            LimitOffset(offset=offset, limit=page_size),
            OrderBy(Build.created_at, "desc"),
            Build.class_type.contains("modern"),
        )

        return [build_service.to_schema(b, schema_type=ModernBuildRetrieve) for b in builds]

    @get("/{build_id: uuid}")
    async def get_modern_build(self, build_id: UUID, build_service: BuildService) -> ModernBuildRetrieve:
        return build_service.to_schema(await build_service.get(build_id), schema_type=ModernBuildRetrieve)

    @patch("/{build_id: uuid}")
    async def update_build(self, build_id: UUID, build_service: BuildService, processor_service: ProcessorService,
                           graphics_service: GraphicsProcessorService, data: ModernBuildCreate) -> ModernBuildRetrieve:
        """
        Update an existing build.
        :param build_id: ID of build to update
        :param build_service: builds database service [injected]
        :param processor_service: processor database service [injected]
        :param graphics_service: graphics database service [injected]
        :param data:
        :return:
        """
        build = await build_service.get(build_id)

        build.processors = []
        await _deduplicate_processors(build, data, processor_service)

        build.graphics = []
        await _deduplicate_graphics_processors(build, data, graphics_service)
        _convert_create_dto_to_model(build, data)

        build = await build_service.update(build, auto_commit=True, auto_refresh=True)
        return build_service.to_schema(build, schema_type=ModernBuildRetrieve)

    @post("/")
    async def create_build(self, build_service: BuildService, processor_service: ProcessorService,
                           graphics_service: GraphicsProcessorService, data: ModernBuildCreate) -> ModernBuildRetrieve:
        """
        Create new build.
        Converts the *Create DTO objects to the database model, commits to database and returns the result.
        """
        build = Build()

        await _deduplicate_processors(build, data, processor_service)
        await _deduplicate_graphics_processors(build, data, graphics_service)
        _convert_create_dto_to_model(build, data)

        build = await build_service.create(build, auto_commit=True, auto_refresh=True)
        return build_service.to_schema(build, schema_type=ModernBuildRetrieve)