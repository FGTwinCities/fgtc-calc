import os
import sys
from typing import NoReturn

from litestar.cli import litestar_group


def setup_environment() -> None:
    os.environ.setdefault("LITESTAR_APP", "app.asgi:create_app")
    os.environ.setdefault("LITESTAR_APP_NAME", "Application")


def run_cli() -> NoReturn:
    setup_environment()

    sys.exit(litestar_group())


if __name__ == "__main__":
    run_cli()