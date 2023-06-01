from __future__ import annotations

from collections.abc import Set
from typing import ClassVar, Protocol


class Check(Protocol):
    family: ClassVar[str]
    requires: ClassVar[Set[str]] = frozenset()

    def check(self) -> bool | None:
        ...
