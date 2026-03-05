from typing import Any


def attrcopy(src: Any, dest: Any, attr_blocklist: list[str] = list()) -> None:
    for attr in src.__dict__.keys():
        if attr in attr_blocklist:
            continue

        try:
            setattr(dest, attr, getattr(src, attr))
        except AttributeError:
            pass

def attrcopy_allowlist(src: Any, dest: Any, attrs: list[str] = list()) -> None:
    for attr in attrs:
        try:
            setattr(dest, attr, getattr(src, attr))
        except AttributeError:
            pass
