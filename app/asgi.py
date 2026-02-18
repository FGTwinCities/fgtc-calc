from litestar import Litestar

from app.core import ApplicationCore


def create_app() -> Litestar:
    """Application entrypoint for use with litestar CLI commands"""
    return Litestar(plugins=[ApplicationCore()])
