from typing import Optional

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from app.build.schema import BuildRetrieve, ModernBuildRetrieve, BuildCreateProcessor, BuildCreateMemoryModule, \
    BuildCreateStorageDisk, BuildCreateBattery, BuildCreateDisplay, MacBuildRetrieve
from app.db import model as m
from app.lib.attrs import attrcopy_allowlist


class BuildService(SQLAlchemyAsyncRepositoryService[m.BuildBase]):

    class Repository(SQLAlchemyAsyncRepository[m.BuildBase]):
        model_type = m.BuildBase

    repository_type = Repository

    async def duplicate(self, build: m.BuildBase, auto_commit: bool = True, auto_refresh: bool = True):
        new_build = type(build)()

        attrcopy_allowlist(build, new_build, [
            "class_type",
            "type",
            "manufacturer",
            "model",
            "operating_system",
            "wired_networking",
            "wireless_networking",
            "bluetooth",
            "webcam",
            "microphone",
            "notes",
            "price",
            "priced_at",
            "macos_version",
        ])

        for cpu in build.processor_associations:
            new_build.processor_associations.append(m.BuildProcessorAssociation(
                processor=cpu.processor,
                upgradable=cpu.upgradable,
            ))

        for gpu in build.graphics_associations:
            new_build.graphics_associations.append(m.BuildGraphicsAssociation(
                graphics=gpu.graphics,
                upgradable=gpu.upgradable,
            ))

        for mem in build.memory:
            new_build.memory.append(m.MemoryModule(
                type=mem.type,
                upgradable=mem.upgradable,
                ecc=mem.ecc,
                clock=mem.clock,
                size=mem.size,
            ))

        for disk in build.storage:
            new_build.storage.append(m.StorageDisk(
                type=disk.type,
                upgradable=disk.upgradable,
                form=disk.form,
                interface=disk.interface,
                size=disk.size,
            ))

        for disp in build.display:
            new_build.display.append(m.Display(
                size=disp.size,
                resolution=disp.resolution,
                refresh_rate=disp.refresh_rate,
                touchscreen=disp.touchscreen,
            ))

        for batt in build.batteries:
            new_build.batteries.append(m.Battery(
                design_capacity=batt.design_capacity,
                remaining_capacity=batt.remaining_capacity,
            ))

        await self.create(new_build, auto_commit=auto_commit, auto_refresh=auto_refresh)
        return new_build

    def retrieve_schema(self, build: m.BuildBase) -> BuildRetrieve:
        schema = BuildRetrieve
        if isinstance(build, m.Build):
            schema = ModernBuildRetrieve
        elif isinstance(build, m.MacBuild):
            schema = MacBuildRetrieve

        return self.to_schema(build, schema_type=schema)

    def to_schema(self,
                  data: "Union[ModelOrRowMappingT, Sequence[ModelOrRowMappingT], ModelProtocol, Sequence[ModelProtocol], RowMapping, Sequence[RowMapping], Row[Any], Sequence[Row[Any]], dict[str, Any], Sequence[dict[str, Any]]]",
                  total: "Optional[int]" = None,
                  filters: "Union[Sequence[Union[StatementFilter, ColumnElement[bool]]], Sequence[StatementFilter], None]" = None,
                  *,
                  schema_type: "Optional[type[ModelDTOT]]" = None) -> "Union[ModelOrRowMappingT, OffsetPagination[ModelOrRowMappingT], ModelDTOT, OffsetPagination[ModelDTOT]]":

        if data is None:
            return None

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
                display=self.to_schema(next(iter(data.display), None), schema_type=BuildCreateDisplay),
                notes=data.notes,

                manufacturer=data.manufacturer,
                model=data.model,
                operating_system=data.operating_system,
            )

        if issubclass(schema_type, MacBuildRetrieve):
            return MacBuildRetrieve(
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
                display=self.to_schema(next(iter(data.display), None), schema_type=BuildCreateDisplay),
                notes=data.notes,

                macos_version=data.macos_version,
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
                display=self.to_schema(next(iter(data.display), None), schema_type=BuildCreateDisplay),
                notes=data.notes,
            )

        return super().to_schema(data, total, filters, schema_type=schema_type)




async def provide_build_service(db_session: AsyncSession) -> BuildService:
    return BuildService(db_session)