from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    from typing_extensions import assert_never
else:
    from typing import assert_never


__all__ = ["assert_never"]


def __dir__() -> list[str]:
    return __all__
