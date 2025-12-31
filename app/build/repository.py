from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.build.model import Build, Processor, GraphicsProcessor, MemoryModule, StorageDisk


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


class MemoryModuleRepository(SQLAlchemyAsyncRepository[MemoryModule]):
    model_type = MemoryModule


async def provide_memory_repo(db_session: AsyncSession):
    return MemoryModuleRepository(session=db_session)


class StorageDiskRepository(SQLAlchemyAsyncRepository[StorageDisk]):
    model_type = StorageDisk


async def provide_storage_repo(db_session: AsyncSession):
    return StorageDiskRepository(session=db_session)
