"""
This accesses the schema for repo-review's tool section.
"""

from __future__ import annotations

__lazy_modules__ = [f"{__spec__.parent}.resources", "json", "typing"]

import json
from typing import Any

from .resources import resources

__all__ = ["get_schema"]


def __dir__() -> list[str]:
    return __all__


def get_schema(tool_name: str = "repo-review") -> dict[str, Any]:
    """Get the stored complete schema for repo-review settings."""
    if tool_name != "repo-review":
        msg = f"Only 'repo-review' is supported, got {tool_name!r}"
        raise ValueError(msg)

    with resources.joinpath("repo-review.schema.json").open(encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]
