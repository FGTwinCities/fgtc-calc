import datetime
from email.iterators import typed_subpart_iterator
from math import ceil
from typing import Sequence
from uuid import UUID
from zoneinfo import ZoneInfo

import dateutil
from advanced_alchemy.filters import LimitOffset, OrderBy, CollectionFilter, StatementFilter, SearchFilter, \
    OnBeforeAfter
from aiohttp import ClientSession
from litestar import get, delete
from litestar.controller import Controller
from litestar.di import Provide
from litestar.pagination import AbstractAsyncClassicPaginator, T, ClassicPagination
from litestar.response import Template, Redirect
from sqlalchemy import ColumnElement

from app.build.schema import BuildRetrieve
from app.db.enum import MacType
from app.db.model import BuildProcessorAssociation, BuildGraphicsAssociation, MacBuild, BuildBase
from app.db.model.battery import Battery
from app.db.model.build import Build
from app.db.model.display import Display
from app.db.model.macbuild import Version
from app.db.model.memory import MemoryModule
from app.db.model.storage import StorageDisk
from app.db.service.build import provide_build_service, BuildService
from app.db.service.graphics import provide_graphics_service
from app.db.service.processor import provide_processor_service
from app.lib.attrs import attrcopy, attrcopy_allowlist
from app.lib.math import mb2gb
from app.lib.util import try_int


async def get_macos_version_info(version: Version) -> dict | None:
    async with ClientSession() as session:
        async with session.get("https://endoflife.date/api/v1/products/macos/") as response:
            assert response.ok

            version_str = f"{version.major}{f".{version.minor}" if version.major <= 10 else ""}"

            data = await response.json()
            releases = data["result"]["releases"]
            for release in releases:
                if release["name"] == version_str:
                    return release

            return None

def try_parse_mac_type(token: str) -> list[MacType]:
    parsed_types = []
    for type in MacType:
        if type == MacType.OTHER:
            continue

        for type_token in type.__str__().lower().split():
            if token in type_token:
                parsed_types.append(type)

    return parsed_types


class BuildClassicPaginator(AbstractAsyncClassicPaginator[BuildRetrieve]):
    build_service: BuildService
    filters: list[StatementFilter | ColumnElement[bool]]

    def __init__(self, build_service: BuildService, filters: list[StatementFilter | ColumnElement[bool]] = []) -> None:
        self.build_service = build_service
        self.filters = filters

    async def get_total(self, page_size: int) -> int:
        return ceil(await self.build_service.count(*self.filters) / page_size)

    async def get_items(self, page_size: int, current_page: int) -> list[BuildRetrieve]:
        builds = await self.build_service.list(
            LimitOffset(offset=current_page * page_size, limit=page_size),
            OrderBy(Build.created_at, "desc"),
            *self.filters,
        )

        return [self.build_service.retrieve_schema(b) for b in builds]


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
    async def get_builds(self,
                         build_service: BuildService,
                         page: int = 0, page_size: int = 25,
                         type: list[str] | None = None,
                         search: str | None = None,
                         strict_search: bool = False,
                         before: datetime.datetime | None = None,
                         after: datetime.datetime | None = None,
                         ) -> ClassicPagination[BuildRetrieve]:
        filters = []

        if type is not None:
            filters.append(CollectionFilter("class_type", type))

        if search is not None:
            search_filters = None
            tokens = search.split()
            for token in tokens:
                token_filter = (BuildBase.notes.icontains(token)
                    | Build.manufacturer.icontains(token)
                    | Build.model.icontains(token)
                    | Build.operating_system.icontains(token)
                    | MacBuild.year.__eq__(try_int(token))
                )

                for mac_type in try_parse_mac_type(token):
                    token_filter = token_filter | MacBuild.mac_type.__eq__(mac_type)

                if strict_search:
                    filters.append(token_filter)
                else:
                    if search_filters is None:
                        search_filters = token_filter
                    else:
                        search_filters = search_filters | token_filter

            if not strict_search:
                filters.append(search_filters)

        if before or after:
            filters.append(OnBeforeAfter("created_at", before, after))

        paginator = BuildClassicPaginator(build_service, filters)
        return await paginator(page_size=page_size, current_page=page)

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

        context = {
            "build": build,
            "total_memory": mb2gb(total_memory),
            "total_designcapacity": total_designcapacity,
            "total_remainingcapacity": total_remainingcapacity,
            "current_datetime": datetime.datetime.now(tz=ZoneInfo("UTC")),
        }

        if isinstance(build, MacBuild):
            macos_info = await get_macos_version_info(build.macos_version)
            context["macos_name"] = macos_info["codename"]
            context["macos_release_year"] = dateutil.parser.parse(macos_info["releaseDate"]).year

        # See app/templates/build/buildsheet.html
        return Template("build/buildsheet.html", context=context)

    @get("/create")
    async def legacy_redirect_create_page(self) -> Redirect:
        return Redirect("/build/modern/create")
