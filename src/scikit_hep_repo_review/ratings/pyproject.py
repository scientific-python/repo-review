from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import tomli as tomllib


@functools.cache
def pyproject(package: Path) -> dict[str, Any]:
    pyproject_path = package.joinpath("pyproject.toml")
    if pyproject_path.exists():
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    return {}


# PP: PyProject.toml
## PP0xx: Build system


class PyProject:
    pass


class PP002(PyProject):
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


class PP003(PyProject):
    "Does not list wheel as a build-dep"

    requires = {"PY001"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must not include wheel, setuptools does this via PEP 517 already"

        match pyproject:
            case {"build-system": {"requires": list(req)}}:
                return all("wheel" not in r for r in req)
            case _:
                return False


repo_review_fixtures = {"pyproject"}
repo_review_checks = {p.__name__ for p in PyProject.__subclasses__()}
