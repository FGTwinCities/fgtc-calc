from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from litestar import get, post
from litestar.controller import Controller
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.build.model import Processor, Build, GraphicsProcessor


class BuildRepository(SQLAlchemyAsyncRepository[Build]):
    model_type = Build


async def provide_builds_repo(db_session: AsyncSession) -> BuildRepository:
    return BuildRepository(session=db_session)


class ProcessorRepository(SQLAlchemyAsyncRepository[Processor]):
    model_type = Processor


async def provide_processors_repo(db_session: AsyncSession) -> ProcessorRepository:
    return ProcessorRepository(session=db_session)


class GraphicsProcessorRepository(SQLAlchemyAsyncRepository[GraphicsProcessor]):
    model_type = GraphicsProcessor


async def provide_graphics_repo(db_session: AsyncSession) -> GraphicsProcessorRepository:
    return GraphicsProcessorRepository(session=db_session)


class BuildController(Controller):
    path = "build"

    dependencies = {
        "builds_repo": Provide(provide_builds_repo),
        "processors_repo": Provide(provide_processors_repo),
        "graphics_repo": Provide(provide_graphics_repo),
    }


    @get("/")
    async def get_builds(self, builds_repo: BuildRepository) -> list[Build]:
        return await builds_repo.list()


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


    @get("/processor")
    async def get_processors(self, processors_repo: ProcessorRepository) -> list[Processor]:
        return await processors_repo.list()


    @post("/processor")
    async def create_processor(self, processors_repo: ProcessorRepository, data: Processor) -> Processor:
        await processors_repo.add(data)
        await processors_repo.session.commit()
        await processors_repo.session.refresh(data)
        return data
