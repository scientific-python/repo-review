from __future__ import annotations

from typing import Any

from . import Rating

# PP: PyProject.toml
## PP0xx: Build system


class PP002(Rating):
    "Has a proper build-system table"

    requires = {"PY001"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have build-system.requires & build-system.backend"

        match pyproject:
            case {"build-system": {"requires": list(), "build-backend": str()}}:
                return True
            case _:
                return False
