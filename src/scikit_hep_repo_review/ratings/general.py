from __future__ import annotations

from pathlib import Path

from . import Rating

# PY: Python Project
## 0xx: File existence


class PY001(Rating):
    "Has a pyproject.toml"

    @staticmethod
    def check(package: Path) -> bool:
        """
        All projects should have a pyproject.toml file to support a modern
        build system and support wheel installs properly.
        """
        return package.joinpath("pyproject.toml").exists()


class PY002(Rating):
    "Has a README.(md|rst) file"

    @staticmethod
    def check(package: Path) -> bool:
        "Projects must have a readme file"
        return (
            package.joinpath("README.md").exists()
            or package.joinpath("README.rst").exists()
        )


class PY003(Rating):
    "Has a LICENSE* file"

    @staticmethod
    def check(package: Path) -> bool:
        "Projects must have a license"
        return len(list(package.glob("LICENSE*"))) > 0


class PY004(Rating):
    "Has docs folder"

    @staticmethod
    def check(package: Path) -> bool:
        "Projects must have documentation in a folder called docs (disable if not applicable)"
        return package.joinpath("docs").exists()


class PY005(Rating):
    "Has tests folder"

    @staticmethod
    def check(package: Path) -> bool:
        "Projects must have a folder called tests"
        return package.joinpath("tests").exists()


class PY006(Rating):
    "Has pre-commit config"

    @staticmethod
    def check(package: Path) -> bool:
        "Projects must have a .pre-commit-config.yaml file"
        return package.joinpath(".pre-commit-config.yaml").exists()
