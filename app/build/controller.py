from typing import List, Any
from uuid import UUID

from litestar import get, post, put, Response
from litestar.controller import Controller
from litestar.handlers import delete
from litestar.response import Template, Response

from app.build.build import Build


class BuildController(Controller):
    path = "build"

    builds: List[Build] = []

    @get("/create")
    async def create_build_page(self) -> Template:
        return Template("build/create.html")


    @get("/view")
    async def view_builds_page(self) -> Template:
        return None #TODO


    @get("/view/{build_id: uuid}")
    async def view_build_page(self, build_id: UUID) -> Template:
        return None #TODO


    @get("/")
    async def get_builds(self) -> List[Build]:
        return self.builds


    @get("/{build_id: uuid}")
    async def get_build(self, build_id: UUID) -> Build | Response[Any]:
        for build in self.builds:
            if build.id == build_id:
                return build

        return Response(status_code=404)


    @post("/")
    async def create_build(self, data: Build) -> Build:
        self.builds.append(data)
        return data


    @put("/{build_id: uuid}")
    async def update_build(self, build_id: UUID, data: Build) -> Build:
        return None #TODO


    @delete("/{build_id: uuid}")
    async def delete_build(self, build_id: UUID) -> None:
        return None #TODO
