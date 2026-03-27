from __future__ import annotations

__lazy_modules__ = ["importlib", "importlib.abc", "importlib.resources.abc"]

import sys

if sys.version_info < (3, 11):
    # pylint: disable-next=deprecated-class
    from importlib.abc import Traversable
else:
    from importlib.resources.abc import Traversable


__all__ = ["Traversable"]


def __dir__() -> list[str]:
    return __all__
