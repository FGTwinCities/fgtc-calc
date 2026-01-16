import os
from pathlib import Path

from advanced_alchemy.config import AsyncSessionConfig
from advanced_alchemy.extensions.litestar import SQLAlchemyInitPlugin, SQLAlchemySerializationPlugin, \
    SQLAlchemyAsyncConfig
from click import Group
from litestar.config.app import AppConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.logging import LoggingConfig
from litestar.plugins.base import InitPluginProtocol, CLIPluginProtocol
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig
from litestar_vite import VitePlugin, PathConfig
from litestar_vite.config import ViteConfig

from app.build.controller.build import BuildController
from app.build.controller.graphics import GraphicsController
from app.build.controller.processor import ProcessorController
from app.price.controller import PriceController
from app.static_controller import StaticController


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        pass

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        session_config = AsyncSessionConfig(expire_on_commit=False)
        sqlalchemy_config = SQLAlchemyAsyncConfig(
            connection_string=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.sqlite"),
            before_send_handler="autocommit",
            session_config=session_config,
            create_all=True,
        )

        vite_config = ViteConfig(
            dev_mode=os.getenv("DEV_MODE", "True").lower() in ("true", 1, "t"),
            mode="template",
            types=False,
            paths=PathConfig(
                bundle_dir="public",
                resource_dir="src",
                static_dir="assets",
            )
        )

        app_config.plugins.extend(
            [
                SQLAlchemyInitPlugin(config=sqlalchemy_config),
                SQLAlchemySerializationPlugin(),
                VitePlugin(config=vite_config),
            ]
        )

        app_config.route_handlers.extend(
            [
                StaticController,
                BuildController,
                ProcessorController,
                GraphicsController,
                PriceController,
            ]
        )

        app_config.template_config = TemplateConfig(
            directory=Path(__file__).parent.parent / "templates",
            engine=JinjaTemplateEngine,
        )

        app_config.logging_config = LoggingConfig(log_exceptions="always")

        return app_config
