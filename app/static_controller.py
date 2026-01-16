import os

from litestar import Controller, get
from litestar.response import Template, File


class StaticController(Controller):
    path = "/"

    @get()
    async def index(self) -> Template:
        return Template("index.html")


    @get("/favicon.ico")
    async def favicon(self) -> File:
        if os.getenv("DEV_MODE", "True").lower() in ("true", 1, "t"):
            return File("assets/favicon.ico")
        else:
            return File("public/favicon.ico")
