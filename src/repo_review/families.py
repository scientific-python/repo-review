from __future__ import annotations

import importlib.metadata
import typing

__all__ = ["Family", "collect_families", "get_familes"]


def __dir__() -> list[str]:
    return __all__


class Family(typing.TypedDict, total=False):
    name: str  # defaults to key
    order: int  # defaults to 0


def collect_families() -> dict[str, Family]:
    return {
        name: family
        for ep in importlib.metadata.entry_points(group="repo_review.families")
        for name, family in ep.load()().items()
    }


def get_familes() -> dict[str, Family]:
    return {
        "general": Family(
            name="General",
            order=-3,
        ),
        "pyproject": Family(
            name="PyProject",
            order=-2,
        ),
        "github": Family(
            name="GitHub Actions",
        ),
        "pre-commit": Family(
            name="Pre-commit",
        ),
        "mypy": Family(
            name="MyPy",
        ),
        "ruff": Family(
            name="Ruff",
        ),
    }
