from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.model.battery import Battery
from app.db.model.display import Display
from app.db.model.memory import MemoryModule
from app.db.model.storage import StorageDisk


class MemoryModuleRepository(SQLAlchemyAsyncRepository[MemoryModule]):
    model_type = MemoryModule


async def provide_memory_repo(db_session: AsyncSession):
    return MemoryModuleRepository(session=db_session)


class StorageDiskRepository(SQLAlchemyAsyncRepository[StorageDisk]):
    model_type = StorageDisk


async def provide_storage_repo(db_session: AsyncSession):
    return StorageDiskRepository(session=db_session)


class DisplayRepository(SQLAlchemyAsyncRepository[Display]):
    model_type = Display


async def provide_display_repo(db_session: AsyncSession):
    return DisplayRepository(session=db_session)


class BatteryRepository(SQLAlchemyAsyncRepository[Battery]):
    model_type = Battery


async def provide_battery_repo(db_session: AsyncSession) -> BatteryRepository:
    return BatteryRepository(session=db_session)
