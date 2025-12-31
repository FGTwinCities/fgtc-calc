from pathlib import Path

from advanced_alchemy.extensions.litestar import SQLAlchemyInitPlugin, SQLAlchemySerializationPlugin, \
    SQLAlchemyAsyncConfig
from click import Group
from litestar.config.app import AppConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import LoggingConfig
from litestar.plugins.base import InitPluginProtocol, CLIPluginProtocol
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

from app.build.controller import BuildController
from app.price.controller import PriceController
from app.static_controller import StaticController


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        pass

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        sqlalchemy_config = SQLAlchemyAsyncConfig(connection_string="sqlite+aiosqlite:///database.sqlite",
                                                  create_all=True)

        app_config.plugins.extend(
            [
                SQLAlchemyInitPlugin(config=sqlalchemy_config),
                SQLAlchemySerializationPlugin(),
            ]
        )

        app_config.route_handlers.extend(
            [
                create_static_files_router("/static", ["assets"]),
                StaticController,
                BuildController,
                PriceController,
            ]
        )

        app_config.template_config = TemplateConfig(
            directory=Path(__file__).parent.parent / "templates",
            engine=JinjaTemplateEngine,
        )

        app_config.logging_config = LoggingConfig(log_exceptions="always")

        return app_config
