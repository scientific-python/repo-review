from __future__ import annotations

import functools
from importlib.abc import Traversable
from typing import Any

from ._compat import tomllib


@functools.cache
def pyproject(package: Traversable) -> dict[str, Any]:
    pyproject_path = package.joinpath("pyproject.toml")
    if pyproject_path.is_file():
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    return {}
