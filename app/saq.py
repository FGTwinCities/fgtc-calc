import os

from litestar_saq import SAQConfig, QueueConfig, CronJob, startup_logger, shutdown_logger, timing_before_process, \
    timing_after_process, SAQPlugin

from app.db.service.pricing import generate_pricing_model_job
from app.lib.util import getenv_bool

saq_config = SAQConfig(
    web_enabled=getenv_bool("SAQ_WEB_ENABLED", False),
    use_server_lifespan=getenv_bool("SAQ_USE_SERVER_LIFESPAN", True),
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

saq_plugin = SAQPlugin(config=saq_config)