from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import model as m


class GraphicsProcessorService(SQLAlchemyAsyncRepositoryService[m.GraphicsProcessor]):

    class Repository(SQLAlchemyAsyncRepository[m.GraphicsProcessor]):
        model_type = m.GraphicsProcessor

    repository_type = Repository


async def provide_graphics_service(db_session: AsyncSession) -> GraphicsProcessorService:
    return GraphicsProcessorService(db_session)