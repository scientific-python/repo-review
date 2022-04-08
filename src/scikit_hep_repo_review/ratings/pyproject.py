from __future__ import annotations

import functools
from importlib.abc import Traversable
from typing import Any

import tomli as tomllib


@functools.cache
def pyproject(package: Traversable) -> dict[str, Any]:
    pyproject_path = package.joinpath("pyproject.toml")
    if pyproject_path.is_file():
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    return {}


# PP: PyProject.toml
## PP0xx: Build system


class PyProject:
    family = "pyproject"


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


class PP301(PyProject):
    "Has pytest in pyproject"

    requires = {"PY001"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have build-system.requires & build-system.backend"

        match pyproject:
            case {"tool": {"pytest": {"ini_options": {}}}}:
                return True
            case _:
                return False


class PP302(PyProject):
    "Sets a minimum pytest to at least 6"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have a minversion, and must be at least 6"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "minversion" in options and float(options["minversion"]) >= 6


class PP303(PyProject):
    "Sets the test paths"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "The testpaths should be set (like to ['tests'])"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "testpaths" in options


class PP304(PyProject):
    "Sets the log level in pytest"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "log_cli_level should be set (probably to INFO)"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "log_cli_level" in options


class PP305(PyProject):
    "Specifies xfail_strict"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "xfail_strict should be set (probably to true)"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "xfail_strict" in options


class PP306(PyProject):
    "Specifies strict config"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "--strict-config should be in addopts"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "--strict-config" in options.get("addopts", [])


class PP307(PyProject):
    "Specifies strict markers"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "--strict-markers should be in addopts"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "--strict-markers" in options.get("addopts", [])


class PP308(PyProject):
    "Specifies useful pytest summary"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "-ra should be in addopts (summary of all fails/errors)"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "-ra" in options.get("addopts", [])


class PP309(PyProject):
    "Filter warnings specified"
    requires = {"PP301"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "filterwarnings must be set (probably to at least ['error'])"
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "-ra" in options.get("addopts", [])


repo_review_fixtures = {"pyproject"}
repo_review_checks = {p.__name__ for p in PyProject.__subclasses__()}
