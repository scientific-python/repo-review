from __future__ import annotations

__lazy_modules__ = ["typing"]

import sys

if sys.version_info < (3, 11):
    from typing_extensions import Self, assert_never
else:
    from typing import Self, assert_never


__all__ = ["Self", "assert_never"]


def __dir__() -> list[str]:
    return __all__
