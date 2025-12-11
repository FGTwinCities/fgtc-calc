from litestar import Controller, get
from litestar.response import Template


class StaticController(Controller):
    path = "/"

    @get()
    async def index(self) -> Template:
        return Template("index.html")

