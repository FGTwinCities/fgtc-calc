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
from litestar_saq import startup_logger, shutdown_logger, timing_before_process, timing_after_process
from litestar_saq.base import CronJob
from litestar_saq.config import SAQConfig, QueueConfig
from litestar_saq.plugin import SAQPlugin
from litestar_vite import VitePlugin, PathConfig
from litestar_vite.config import ViteConfig

from app.build.controller.build import BuildController
from app.build.controller.graphics import GraphicsController
from app.build.controller.processor import ProcessorController
from app.db.service.pricing import provide_pricing_model_service, generate_pricing_model_job
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

saq_config = SAQConfig(
    web_enabled=True,
    use_server_lifespan=True,
    queue_configs=[
        QueueConfig(
            dsn=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            name="default",
            tasks=[
                generate_pricing_model_job,
            ],
            scheduled_tasks=[
                CronJob(
                    function=generate_pricing_model_job,
                    cron="0 0 * * MON", #Midnight, every monday
                    timeout=3600,
                ),
            ],
            startup=[startup_logger],
            shutdown=[shutdown_logger],
            before_process=[timing_before_process],
            after_process=[timing_after_process],
        )
    ]
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
                SAQPlugin(config=saq_config),
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
