from __future__ import annotations

from typing import ClassVar, Protocol


class Rating(Protocol):
    requires: ClassVar[set[str]] = set()
