from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import model as m


class BuildService(SQLAlchemyAsyncRepositoryService[m.Build]):

    class Repository(SQLAlchemyAsyncRepository[m.Build]):
        model_type = m.Build

    repository_type = Repository


async def provide_build_service(db_session: AsyncSession) -> BuildService:
    return BuildService(db_session)