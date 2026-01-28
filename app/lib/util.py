import os
from typing import Any


def try_int(value: Any) -> int | None:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def getenv_bool(key: str, default: bool = False) -> bool:
    var = os.getenv(key)

    if var is None:
        return default

    return var.lower() in ("true", 1, "t", "yes", "y")
