from pathlib import Path

from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import LoggingConfig
from litestar.static_files.config import create_static_files_router
from litestar.template.config import TemplateConfig

from app.static_controller import StaticController

app = Litestar(
    route_handlers=[
        create_static_files_router("/static", ["assets"]),
        StaticController
    ],
    template_config=TemplateConfig(
        directory=Path(__file__).parent.parent / "templates",
        engine=JinjaTemplateEngine,
    ),
    logging_config=LoggingConfig(log_exceptions="always"),
)