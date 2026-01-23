from typing import Any


def try_int(value: Any) -> int | None:
    try:
        return int(value)
    except (ValueError, TypeError):
        return None