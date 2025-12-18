from typing import List, Any
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.repository.typing import SQLAlchemyAsyncRepositoryT
from litestar import get, post, put, Response
from litestar.controller import Controller
from litestar.di import Provide
from litestar.handlers import delete
from litestar.response import Template, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from app.build.model import Processor, Build


class BuildRepository(SQLAlchemyAsyncRepository[Build]):
    model_type = Build


async def provide_builds_repo(db_session: AsyncSession) -> BuildRepository:
    return BuildRepository(session=db_session)


class ProcessorRepository(SQLAlchemyAsyncRepository[Processor]):
    model_type = Processor


async def provide_processors_repo(db_session: AsyncSession) -> ProcessorRepository:
    return ProcessorRepository(session=db_session)


class BuildController(Controller):
    path = "build"

    dependencies = {
        "builds_repo": Provide(provide_builds_repo),
        "processors_repo": Provide(provide_processors_repo),
    }


    @get("/")
    async def get_builds(self, builds_repo: BuildRepository) -> list[Build]:
        return await builds_repo.list()


    @post("/")
    async def create_build(self, builds_repo: BuildRepository, data: Build) -> Build:
        for m in data.memory:
            m.build_id = data.id

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
