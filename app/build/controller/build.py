from typing import Sequence
from uuid import UUID

from litestar import get, post, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.response import Template

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
from app.lib.attrs import attrcopy


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
    async def get_builds(self, build_service: BuildService) -> Sequence[Build]:
        return await build_service.list()


    @get("/{build_id: uuid}")
    async def get_build(self, build_id: UUID, build_service: BuildService) -> Build:
        return await build_service.get(build_id)


    @post("/")
    async def create_build(self, build_service: BuildService, processor_service: ProcessorService, graphics_service: GraphicsProcessorService, data: BuildCreate) -> Build:
        build = Build()

        # Find existing processors by name
        for i in range(0, len(data.processors)):
            found_processors = await processor_service.list(Processor.model.is_(data.processors[i].model))
            if len(found_processors) > 0:
                build.processors.append(found_processors[0])
            else:
                new_processor = Processor(
                    model=data.processors[i].model,
                )
                new_processor = await processor_service.create(new_processor, auto_commit=True, auto_refresh=True)
                build.processors.append(new_processor)

        # Find existing GPUs by name
        for i in range(0, len(data.graphics)):
            found_gpus = await graphics_service.list(GraphicsProcessor.model.is_(data.graphics[i].model))
            if len(found_gpus) > 0:
                build.graphics.append(found_gpus[0])
            else:
                new_gpu = GraphicsProcessor(
                    model=data.graphics[i].model,
                )
                new_gpu = await graphics_service.create(new_gpu, auto_commit=True, auto_refresh=True)
                build.graphics.append(new_gpu)

        for mem in data.memory:
            module = MemoryModule()
            attrcopy(mem, module)
            build.memory.append(module)

        for store in data.storage:
            disk = StorageDisk()
            attrcopy(store, disk)
            build.storage.append(disk)

        if data.display:
            display = Display()
            attrcopy(data.display, display)
            build.display.append(display)

        for batt in data.batteries:
            battery = Battery()
            attrcopy(batt, battery)
            build.batteries.append(battery)

        # Copy all attributes except the once done manually above between the creation object and the model object
        attr_blocklist = ["processors", "graphics", "memory", "storage", "display", "batteries"]
        attrcopy(data, build, attr_blocklist)

        build = await build_service.create(build, auto_commit=True, auto_refresh=True)
        return build


    @delete("/{build_id: uuid}")
    async def delete_build(self, build_id: UUID, build_service: BuildService) -> None:
        build = await build_service.get(build_id)
        await build_service.delete(build_id)
