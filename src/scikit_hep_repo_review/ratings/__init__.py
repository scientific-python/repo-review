from __future__ import annotations

from typing import ClassVar, Protocol


class Rating(Protocol):
    family: ClassVar[str]
    requires: ClassVar[set[str]] = set()
