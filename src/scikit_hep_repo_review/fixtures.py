from __future__ import annotations

from typing import Any

from ._compat import tomllib
from ._compat.importlib.resources.abc import Traversable

__all__ = ["pyproject", "package"]


def __dir__() -> list[str]:
    return __all__


def pyproject(package: Traversable) -> dict[str, Any]:
    pyproject_path = package.joinpath("pyproject.toml")
    if pyproject_path.is_file():
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    return {}


def package(package: Traversable) -> Traversable:
    return package
