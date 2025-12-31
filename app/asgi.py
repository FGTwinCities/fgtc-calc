from litestar import Litestar

from app.core import ApplicationCore


def create_app() -> Litestar:
    return Litestar(plugins=[ApplicationCore()])
