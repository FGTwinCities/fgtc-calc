import os
from pathlib import Path

import anyio
from advanced_alchemy.config import AsyncSessionConfig
from advanced_alchemy.extensions.litestar import SQLAlchemyInitPlugin, SQLAlchemySerializationPlugin, \
    SQLAlchemyAsyncConfig
from click import Group
from litestar.config.app import AppConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.di import Provide
from litestar.logging import LoggingConfig
from litestar.plugins.base import InitPluginProtocol, CLIPluginProtocol
from litestar.template.config import TemplateConfig
from litestar_vite import VitePlugin, PathConfig
from litestar_vite.config import ViteConfig

from app.build.controller.build import BuildController
from app.build.controller.graphics import GraphicsController
from app.build.controller.processor import ProcessorController
from app.db.service.pricing import provide_pricing_model_service, PricingModelService
from app.lib.deps import provide_services
from app.price.controller import PriceController
from app.static_controller import StaticController

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


class ApplicationCore(InitPluginProtocol, CLIPluginProtocol):
    def on_cli_init(self, cli: Group) -> None:
        @cli.command()
        def generate_pricing_model():
            async def generate_pricing_model():
                async with provide_services(provide_pricing_model_service) as (pricing_model_service,):
                    await pricing_model_service.generate_model()

            anyio.run(generate_pricing_model)

    def on_app_init(self, app_config: AppConfig) -> AppConfig:

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

        app_config.dependencies = {
            "pricing_model_service": Provide(provide_pricing_model_service),
        }

        return app_config
