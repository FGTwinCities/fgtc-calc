from typing import Optional

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.build.schema import BuildRetrieve, ModernBuildRetrieve, BuildCreateProcessor, BuildCreateMemoryModule, \
    BuildCreateStorageDisk, BuildCreateBattery, BuildCreateDisplay
from app.db import model as m


class BuildService(SQLAlchemyAsyncRepositoryService[m.BuildBase]):

    class Repository(SQLAlchemyAsyncRepository[m.BuildBase]):
        model_type = m.BuildBase

    repository_type = Repository

    def retrieve_schema(self, build: m.BuildBase) -> BuildRetrieve:
        schema = BuildRetrieve
        if isinstance(build, m.Build):
            schema = ModernBuildRetrieve
        elif isinstance(build, m.MacBuild):
            schema = BuildRetrieve

        return self.to_schema(build, schema_type=schema)

    def to_schema(self,
                  data: "Union[ModelOrRowMappingT, Sequence[ModelOrRowMappingT], ModelProtocol, Sequence[ModelProtocol], RowMapping, Sequence[RowMapping], Row[Any], Sequence[Row[Any]], dict[str, Any], Sequence[dict[str, Any]]]",
                  total: "Optional[int]" = None,
                  filters: "Union[Sequence[Union[StatementFilter, ColumnElement[bool]]], Sequence[StatementFilter], None]" = None,
                  *,
                  schema_type: "Optional[type[ModelDTOT]]" = None) -> "Union[ModelOrRowMappingT, OffsetPagination[ModelOrRowMappingT], ModelDTOT, OffsetPagination[ModelDTOT]]":

        if issubclass(schema_type, BuildCreateProcessor):
            if isinstance(data, m.BuildProcessorAssociation):
                return BuildCreateProcessor(
                    id=data.processor.id,
                    model=data.processor.model,
                    upgradable=data.upgradable,
                )

            if isinstance(data, m.BuildGraphicsAssociation):
                return BuildCreateProcessor(
                    id=data.graphics.id,
                    model=data.graphics.model,
                    upgradable=data.upgradable,
                )

        if issubclass(schema_type, BuildCreateMemoryModule):
            return BuildCreateMemoryModule(
                type=data.type,
                clock=data.clock,
                size=data.size,
                upgradable=data.upgradable,
                ecc=data.ecc,
            )

        if issubclass(schema_type, ModernBuildRetrieve):
            return ModernBuildRetrieve(
                id=data.id,
                class_type=data.class_type,
                created_at=data.created_at,
                updated_at=data.updated_at,
                price=data.price,
                priced_at=data.priced_at,
                type=data.type,
                wired_networking=data.wired_networking,
                wireless_networking=data.wireless_networking,
                bluetooth=data.bluetooth,
                webcam=data.webcam,
                microphone=data.microphone,
                processors=[self.to_schema(x, schema_type=BuildCreateProcessor) for x in data.processor_associations],
                graphics=[self.to_schema(x, schema_type=BuildCreateProcessor) for x in data.graphics_associations],
                memory=[self.to_schema(x, schema_type=BuildCreateMemoryModule) for x in data.memory],
                storage=[self.to_schema(x, schema_type=BuildCreateStorageDisk) for x in data.storage],
                batteries=[self.to_schema(x, schema_type=BuildCreateBattery) for x in data.batteries],
                display=self.to_schema(data.display, schema_type=BuildCreateDisplay),
                notes=data.notes,

                manufacturer=data.manufacturer,
                model=data.model,
                operating_system=data.operating_system,
            )

        if issubclass(schema_type, BuildRetrieve):
            return BuildRetrieve(
                id=data.id,
                class_type=data.class_type,
                created_at=data.created_at,
                updated_at=data.updated_at,
                price=data.price,
                priced_at=data.priced_at,
                type=data.type,
                wired_networking=data.wired_networking,
                wireless_networking=data.wireless_networking,
                bluetooth=data.bluetooth,
                webcam=data.webcam,
                microphone=data.microphone,
                processors=[self.to_schema(x, schema_type=BuildCreateProcessor) for x in data.processor_associations],
                graphics=[self.to_schema(x, schema_type=BuildCreateProcessor) for x in data.graphics_associations],
                memory=[self.to_schema(x, schema_type=BuildCreateMemoryModule) for x in data.memory],
                storage=[self.to_schema(x, schema_type=BuildCreateStorageDisk) for x in data.storage],
                batteries=[self.to_schema(x, schema_type=BuildCreateBattery) for x in data.batteries],
                display=self.to_schema(data.display, schema_type=BuildCreateDisplay),
                notes=data.notes,
            )

        return super().to_schema(data, total, filters, schema_type=schema_type)




async def provide_build_service(db_session: AsyncSession) -> BuildService:
    return BuildService(db_session)