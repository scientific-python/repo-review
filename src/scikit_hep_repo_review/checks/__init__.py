from __future__ import annotations

from typing import ClassVar, Protocol


class Check(Protocol):
    family: ClassVar[str]
    requires: ClassVar[set[str]] = set()

    def check(self) -> bool | None:
        ...
