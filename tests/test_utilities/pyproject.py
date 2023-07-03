from __future__ import annotations

from typing import Any

from repo_review._compat.importlib.resources.abc import Traversable

# PP: PyProject.toml
## PP0xx: Build system


class General:
    family = "general"


class PY001(General):
    "Has a pyproject.toml"

    @staticmethod
    def check(package: Traversable) -> bool:
        """
        All projects should have a `pyproject.toml` file to support a modern
        build system and support wheel installs properly.
        """
        return package.joinpath("pyproject.toml").is_file()


class PY002(General):
    "Has a README.(md|rst) file"

    @staticmethod
    def check(root: Traversable) -> bool:
        "Projects must have a readme file"
        return (
            root.joinpath("README.md").is_file()
            or root.joinpath("README.rst").is_file()
        )


class PY004(General):
    "Has docs folder"

    @staticmethod
    def check(root: Traversable) -> bool:
        "Projects must have documentation in a folder called docs (disable if not applicable)"
        return len([p for p in root.iterdir() if "doc" in p.name]) > 0


class PY005(General):
    "Has tests folder"

    @staticmethod
    def check(package: Traversable) -> bool:
        "Projects must have a folder called tests"
        return len([p for p in package.iterdir() if "test" in p.name]) > 0


class PY006(General):
    "Has pre-commit config"

    @staticmethod
    def check(root: Traversable) -> bool:
        "Projects must have a `.pre-commit-config.yaml` file"
        return root.joinpath(".pre-commit-config.yaml").is_file()


class PyProject:
    family = "pyproject"


class PP002(PyProject):
    "Has a proper build-system table"

    requires = frozenset(("PY001",))
    url = "https://packaging.python.org/en/latest/specifications/declaring-build-dependencies"

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """
        Must have `build-system.requires` *and* `build-system.backend`. Both
        should be present in all modern packages.
        """

        match pyproject:
            case {"build-system": {"requires": list(), "build-backend": str()}}:
                return True
            case _:
                return False


class PP003(PyProject):
    "Does not list wheel as a build-dep"

    requires = frozenset(("PY001",))

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """
        Do not include `"wheel"` in your `build-system.requires`, setuptools
        does this via PEP 517 already. Setuptools will also only require this
        for actual wheel builds, and might have version limits.
        """

        match pyproject:
            case {"build-system": {"requires": list(req)}}:
                return all(not r.startswith("wheel") for r in req)
            case _:
                return False


class PP301(PyProject):
    "Has pytest in pyproject"

    requires = frozenset(("PY001",))

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """
        Must have a pytest configuration section in pyproject.toml. If you must
        have it somewhere else (such as to support `pytest<6`), ignore this
        check.
        """

        match pyproject:
            case {"tool": {"pytest": {"ini_options": {}}}}:
                return True
            case _:
                return False


class PP302(PyProject):
    "Sets a minimum pytest to at least 6"
    requires = frozenset(("PP301",))

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """
        Must have a `minversion=`, and must be at least 6 (first version to
        support `pyproject.toml` configuration).
        """
        options = pyproject["tool"]["pytest"]["ini_options"]
        return "minversion" in options and float(options["minversion"]) >= 6


def repo_review_checks() -> dict[str, PyProject | General]:
    return {p.__name__: p() for p in PyProject.__subclasses__()} | {
        p.__name__: p() for p in General.__subclasses__()
    }
