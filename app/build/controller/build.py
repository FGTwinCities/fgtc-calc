import datetime
import uuid
from typing import Sequence
from unittest.mock import magic_methods
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, post, delete, patch
from litestar.controller import Controller
from litestar.di import Provide
from litestar.response import Template
from sqlalchemy.sql.elements import SQLCoreOperations

from app.build.schema import BuildCreate
from app.db.model.battery import Battery
from app.db.model.build import Build
from app.db.model.display import Display
from app.db.model.graphics import GraphicsProcessor
from app.db.model.memory import MemoryModule
from app.db.model.processor import Processor
from app.db.model.storage import StorageDisk
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service, GraphicsProcessorService
from app.db.service.processor import provide_processor_service, ProcessorService
from app.lib.attrs import attrcopy, attrcopy_allowlist
from app.lib.math import mb2gb


class BuildController(Controller):
    path = "build"

    dependencies = {
        "build_service": Provide(provide_build_service),
        "processor_service": Provide(provide_processor_service),
        "graphics_service": Provide(provide_graphics_service),
    }


    @get("/create")
    async def create_build_page(self) -> Template:
        return Template("build/create.html")


    @get("/")
    async def get_builds(self, build_service: BuildService, offset: int = 0, page_size: int = 25) -> Sequence[Build]:
        return await build_service.list(
            LimitOffset(offset=offset, limit=page_size),
            OrderBy(Build.created_at, "desc"),
        )


    @get("/{build_id: uuid}")
    async def get_build(self, build_id: UUID, build_service: BuildService) -> Build:
        return await build_service.get(build_id)

    @patch("/{build_id: uuid}")
    async def update_build(self, build_id: UUID, build_service: BuildService, processor_service: ProcessorService, graphics_service: GraphicsProcessorService, data: BuildCreate) -> Build:
        build = await build_service.get(build_id)

        build.processors = []
        await self._deduplicate_processors(build, data, processor_service)

        build.graphics = []
        await self._deduplicate_graphics_processors(build, data, graphics_service)
        self._convert_create_dto_to_model(build, data)

        build = await build_service.update(build, auto_commit=True, auto_refresh=True)
        return build

    @post("/")
    async def create_build(self, build_service: BuildService, processor_service: ProcessorService, graphics_service: GraphicsProcessorService, data: BuildCreate) -> Build:
        build = Build()

        await self._deduplicate_processors(build, data, processor_service)
        await self._deduplicate_graphics_processors(build, data, graphics_service)
        self._convert_create_dto_to_model(build, data)

        build = await build_service.create(build, auto_commit=True, auto_refresh=True)
        return build

    def _convert_create_dto_to_model(self, build: Build, data: BuildCreate):
        build.memory = []
        for mem in data.memory:
            module = MemoryModule()
            attrcopy(mem, module)
            build.memory.append(module)

        build.storage = []
        for store in data.storage:
            disk = StorageDisk()
            attrcopy(store, disk)
            build.storage.append(disk)

        build.display = []
        if data.display:
            display = Display()
            attrcopy(data.display, display)
            build.display.append(display)

        build.batteries = []
        for batt in data.batteries:
            battery = Battery()
            attrcopy(batt, battery)
            build.batteries.append(battery)

        # Copy all attributes except the once done manually above between the creation object and the model object
        attr_blocklist = ["processors", "graphics", "memory", "storage", "display", "batteries"]
        attrcopy(data, build, attr_blocklist)

    async def _deduplicate_graphics_processors(self, build: Build, data: BuildCreate,
                                               graphics_service: GraphicsProcessorService):
        # Find existing GPUs by name
        for i in range(0, len(data.graphics)):
            found_gpus = await graphics_service.list(GraphicsProcessor.model.contains(data.graphics[i].model))

            is_found = False
            for gpu in found_gpus:
                if gpu.model == data.graphics[i].model:
                    build.graphics.append(gpu)
                    is_found = True

            if not is_found:
                new_gpu = GraphicsProcessor(
                    model=data.graphics[i].model,
                )
                new_gpu = await graphics_service.create(new_gpu, auto_commit=True, auto_refresh=True)
                build.graphics.append(new_gpu)

    async def _deduplicate_processors(self, build: Build, data: BuildCreate, processor_service: ProcessorService):
        # Find existing processors by name
        for i in range(0, len(data.processors)):
            # For some dumb reason, model.is_() breaks everything when using postgres, so query by contains and do final comparison here
            # TODO: Please find a fix
            found_processors = await processor_service.list(Processor.model.contains(data.processors[i].model))

            is_found = False
            for processor in found_processors:
                if processor.model == data.processors[i].model:
                    build.processors.append(processor)
                    is_found = True

            if not is_found:
                new_processor = Processor(
                    model=data.processors[i].model,
                )
                new_processor = await processor_service.create(new_processor, auto_commit=True, auto_refresh=True)
                build.processors.append(new_processor)

    @delete("/{build_id: uuid}")
    async def delete_build(self, build_id: UUID, build_service: BuildService) -> None:
        await build_service.delete(build_id, auto_commit=True)

    @get("/{build_id: uuid}/duplicate")
    async def duplicate_build(self, build_id: UUID, build_service: BuildService) -> Build:
        build = await build_service.get(build_id)
        new_build = Build()

        attrcopy_allowlist(build, new_build, [
            "type",
            "manufacturer",
            "model",
            "operating_system",
            "wired_networking",
            "wireless_networking",
            "bluetooth",
            "notes",
            "processors",
            "graphics",
            "price",
            "priced_at",
        ])

        for mem in build.memory:
            new_mem = MemoryModule()
            attrcopy(mem, new_mem, ["build_id"])
            new_build.memory.append(new_mem)

        for disk in build.storage:
            new_disk = StorageDisk()
            attrcopy(disk, new_disk, ["build_id"])
            new_build.storage.append(new_disk)

        for batt in build.batteries:
            new_batt = Battery()
            attrcopy(batt, new_batt, ["build_id"])
            new_build.batteries.append(new_batt)

        for disp in build.display:
            new_disp = Display()
            attrcopy(disp, new_disp, ["build_id"])
            new_build.display.append(new_disp)

        await build_service.create(new_build, auto_commit=True, auto_refresh=True)
        return new_build


    @get("/{build_id: uuid}/sheet")
    async def generate_buildsheet(self, build_id: UUID, build_service: BuildService) -> Template:
        build = await build_service.get(build_id)

        total_memory = 0
        for mem in build.memory:
            total_memory += mem.size

        total_designcapacity = 0
        total_remainingcapacity = 0
        for battery in build.batteries:
            total_designcapacity += battery.design_capacity
            total_remainingcapacity += battery.remaining_capacity

        return Template("build/buildsheet.html", context=
        {
            "build": build,
            "total_memory": mb2gb(total_memory),
            "total_designcapacity": total_designcapacity,
            "total_remainingcapacity": total_remainingcapacity,
            "current_datetime": datetime.datetime.now(tz=ZoneInfo("UTC"))
        })
