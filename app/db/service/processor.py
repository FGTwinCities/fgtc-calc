from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import model as m


class ProcessorService(SQLAlchemyAsyncRepositoryService[m.Processor]):

    class Repository(SQLAlchemyAsyncRepository[m.Processor]):
        model_type = m.Processor

    repository_type = Repository


async def provide_processor_service(db_session: AsyncSession) -> ProcessorService:
    return ProcessorService(db_session)