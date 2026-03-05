import datetime
from typing import Sequence
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar import get, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.response import Template, Redirect

from app.build.schema import BuildRetrieve
from app.db.model import BuildProcessorAssociation, BuildGraphicsAssociation
from app.db.model.battery import Battery
from app.db.model.build import Build
from app.db.model.display import Display
from app.db.model.memory import MemoryModule
from app.db.model.storage import StorageDisk
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service
from app.db.service.processor import provide_processor_service
from app.lib.attrs import attrcopy, attrcopy_allowlist
from app.lib.math import mb2gb


class BuildController(Controller):
    """
    Main controller class for creating, updating and managing builds
    """
    path = "build"

    dependencies = {
        "build_service": Provide(provide_build_service),
        "processor_service": Provide(provide_processor_service),
        "graphics_service": Provide(provide_graphics_service),
    }

    @get("/")
    async def get_builds(self, build_service: BuildService, offset: int = 0, page_size: int = 25) -> Sequence[BuildRetrieve]:
        builds = await build_service.list(
            LimitOffset(offset=offset, limit=page_size),
            OrderBy(Build.created_at, "desc"),
        )

        return [build_service.retrieve_schema(b) for b in builds]

    @get("/{build_id: uuid}")
    async def get_build(self, build_id: UUID, build_service: BuildService) -> BuildRetrieve:
        return build_service.retrieve_schema(await build_service.get(build_id))

    @delete("/{build_id: uuid}")
    async def delete_build(self, build_id: UUID, build_service: BuildService) -> None:
        await build_service.delete(build_id, auto_commit=True)

    @get("/{build_id: uuid}/duplicate")
    async def duplicate_build(self, build_id: UUID, build_service: BuildService) -> BuildRetrieve:
        """
        Duplicate an existing build by copying its attributes to a new build object
        :param build_id: ID of build to duplicate
        :param build_service: builds databse service [injected]
        :return: new build object
        """
        build = await build_service.get(build_id)
        new_build = await build_service.duplicate(build)
        return build_service.to_schema(new_build, schema_type=BuildRetrieve)


    @get("/{build_id: uuid}/sheet")
    async def generate_buildsheet(self, build_id: UUID, build_service: BuildService) -> Template:
        """
        Render a printable buildsheet template for a given build.
        :param build_id: build to render buldsheet for
        :param build_service: builds database service [injected]
        :return: rendered template
        """
        build = await build_service.get(build_id)

        total_memory = 0
        for mem in build.memory:
            total_memory += mem.size

        total_designcapacity = 0
        total_remainingcapacity = 0
        for battery in build.batteries:
            total_designcapacity += battery.design_capacity
            total_remainingcapacity += battery.remaining_capacity
        total_designcapacity = max(1, total_designcapacity)

        # See app/templates/build/buildsheet.html
        return Template("build/buildsheet.html", context=
        {
            "build": build,
            "total_memory": mb2gb(total_memory),
            "total_designcapacity": total_designcapacity,
            "total_remainingcapacity": total_remainingcapacity,
            "current_datetime": datetime.datetime.now(tz=ZoneInfo("UTC"))
        })

    @get("/create")
    async def legacy_redirect_create_page(self) -> Redirect:
        return Redirect("/build/modern/create")
