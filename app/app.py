from pathlib import Path

from advanced_alchemy.extensions.litestar import SQLAlchemyInitPlugin
from advanced_alchemy.extensions.litestar.plugins.init.config.asyncio import SQLAlchemyAsyncConfig
from advanced_alchemy.extensions.litestar.plugins.serialization import SQLAlchemySerializationPlugin
from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import LoggingConfig
from litestar.static_files.config import create_static_files_router
from litestar.template.config import TemplateConfig

from app.build.controller import BuildController
from app.price.controller import PriceController
from app.static_controller import StaticController

sqlalchemy_config = SQLAlchemyAsyncConfig(connection_string="sqlite+aiosqlite:///database.sqlite", create_all=True)

app = Litestar(
    route_handlers=[
        create_static_files_router("/static", ["assets"]),
        StaticController,
        BuildController,
        PriceController,
    ],
    template_config=TemplateConfig(
        directory=Path(__file__).parent.parent / "templates",
        engine=JinjaTemplateEngine,
    ),
    logging_config=LoggingConfig(log_exceptions="always"),
    plugins=[
      SQLAlchemyInitPlugin(config=sqlalchemy_config),
        SQLAlchemySerializationPlugin(),
    ],
)