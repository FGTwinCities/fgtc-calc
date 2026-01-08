from typing import Any


def attrcopy(src: Any, dest: Any, attr_blocklist: list[str] = list()) -> None:
    for attr in src.__dict__.keys():
        if attr in attr_blocklist:
            continue

        setattr(dest, attr, getattr(src, attr))
