from uuid import UUID

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.response import Template

from app.build.repository import provide_builds_repo, provide_processors_repo, provide_graphics_repo, BuildRepository, \
    ProcessorRepository, GraphicsProcessorRepository
from app.db.model.build import Build
from app.db.model.graphics import GraphicsProcessor
from app.db.model.processor import Processor
from app.lib.math import clamp

MAX_SEARCH_ITEMS = 100


class BuildController(Controller):
    path = "build"

    dependencies = {
        "builds_repo": Provide(provide_builds_repo),
        "processors_repo": Provide(provide_processors_repo),
        "graphics_repo": Provide(provide_graphics_repo),
    }


    @get("/create")
    async def create_build_page(self) -> Template:
        return Template("build/create.html")


    @get("/")
    async def get_builds(self, builds_repo: BuildRepository) -> list[Build]:
        return await builds_repo.list()


    @get("/{build_id: uuid}")
    async def get_build(self, build_id: UUID, builds_repo: BuildRepository) -> Build:
        return await builds_repo.get(build_id)


    @post("/")
    async def create_build(self, builds_repo: BuildRepository, processors_repo: ProcessorRepository, graphics_repo: GraphicsProcessorRepository, data: Build) -> Build:
        #De-duplicate processors
        for i in range(0, len(data.processors)):
            found_processors = await processors_repo.list(Processor.model.is_(data.processors[i].model))
            if len(found_processors) > 0:
                data.processors[i] = found_processors[0]

        #De-duplicate graphics processors
        for i in range(0, len(data.graphics)):
            found_gpus = await graphics_repo.list(GraphicsProcessor.model.is_(data.graphics[i].model))
            if len(found_gpus) > 0:
                data.graphics[i] = found_gpus[0]

        await builds_repo.add(data)
        await builds_repo.session.commit()
        await builds_repo.session.refresh(data)
        return data


    @delete("/{build_id: uuid}")
    async def delete_build(self, build_id: UUID, builds_repo: BuildRepository) -> None:
        # Delete any memory modules associated with this build
        build = await builds_repo.get(build_id)
        for module in build.memory:
            await builds_repo.session.delete(module)

        for disk in build.storage:
            await builds_repo.session.delete(disk)

        await builds_repo.session.commit()
        await builds_repo.session.refresh(build)

        await builds_repo.delete(build_id)
        await builds_repo.session.commit()


    @get("/processor")
    async def get_processors(self, processors_repo: ProcessorRepository) -> list[Processor]:
        return await processors_repo.list()


    @get("/processor/{processor_id: uuid}")
    async def get_processor(self, processor_id: UUID, processors_repo: ProcessorRepository) -> Processor:
        return await processors_repo.get(processor_id)


    @post("/processor")
    async def create_processor(self, processors_repo: ProcessorRepository, data: Processor) -> Processor:
        await processors_repo.add(data)
        await processors_repo.session.commit()
        await processors_repo.session.refresh(data)
        return data


    @delete("/processor/{processor_id: uuid}")
    async def delete_processor(self, processor_id: UUID, processors_repo: ProcessorRepository) -> None:
        await processors_repo.delete(processor_id)
        await processors_repo.session.commit()


    @get("/processor/search")
    async def search_processors(self, q: str, processors_repo: ProcessorRepository, limit: int = 50) -> list[Processor]:
        return await processors_repo.list(
            Processor.model.icontains(q),
            OrderBy("model"),
            LimitOffset(limit=clamp(limit, 0, MAX_SEARCH_ITEMS), offset=0),
        )


    @get("/graphics")
    async def get_graphics(self, graphics_repo: GraphicsProcessorRepository) -> list[GraphicsProcessor]:
        return await graphics_repo.list()


    @get("/graphics/{gpu_id: uuid}")
    async def get_gpu(self, gpu_id: UUID, graphics_repo: GraphicsProcessorRepository) -> GraphicsProcessor:
        return await graphics_repo.get(gpu_id)


    @post("/graphics")
    async def create_gpu(self, data: GraphicsProcessor, graphics_repo: GraphicsProcessorRepository) -> GraphicsProcessor:
        await graphics_repo.add(data)
        await graphics_repo.session.commit()
        await graphics_repo.session.refresh(data)
        return data


    @delete("/graphics/{gpu_id: uuid}")
    async def delete_gpu(self, gpu_id: UUID, graphics_repo: GraphicsProcessorRepository) -> None:
        await graphics_repo.delete(gpu_id)
        await graphics_repo.session.commit()


    @get("/graphics/search")
    async def search_gpu(self, q: str, graphics_repo: GraphicsProcessorRepository, limit: int = 50) -> list[GraphicsProcessor]:
        return await graphics_repo.list(
            GraphicsProcessor.model.icontains(q),
            OrderBy("model"),
            LimitOffset(limit=clamp(limit, 0, MAX_SEARCH_ITEMS), offset=0),
        )
