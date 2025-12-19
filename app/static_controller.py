from litestar import Controller, get
from litestar.response import Template, Redirect


class StaticController(Controller):
    path = "/"

    @get()
    async def index(self) -> Template:
        return Template("index.html")


    @get("/favicon.ico")
    async def favicon(self) -> Redirect:
        return Redirect("/static/favicon.ico")
