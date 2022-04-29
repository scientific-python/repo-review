from __future__ import annotations

import configparser
import functools
from importlib.abc import Traversable
from typing import Any

import tomli as tomllib


@functools.cache
def flake8(package: Traversable) -> dict[str, Any]:
    pyproject_path = package / "pyproject.toml"
    if pyproject_path.is_file():
        with pyproject_path.open("rb") as f:
            pyproject = tomllib.load(f)
            if "flake8" in pyproject.get("tool", {}):
                return pyproject["tool"]["flake8"]  # type: ignore[no-any-return]
    flake8_ini_path = package / ".flake8"
    flake8_setup_cfg = package / "setup.cfg"
    flake8_tox_ini = package / "tox.ini"

    for flake8_path in [flake8_ini_path, flake8_setup_cfg, flake8_tox_ini]:
        if flake8_path.is_file():
            config = configparser.ConfigParser()
            config.read_string(flake8_path.read_text())
            if "flake8" in config:
                return dict(config["flake8"])

    return {}


# FK: Flake8


class Flake8:
    family = "flake8"


class FK001(Flake8):
    "Has Flake8 config"

    @staticmethod
    def check(flake8: dict[str, Any]) -> bool:
        """
        Should have some form of flake8 config (`.flake8`, `setup.cfg`, or `pyproject.toml` + pflake8).
        """
        return bool(flake8)


class FK002(Flake8):
    "Uses extend ignore"
    requires = {"FK001"}

    @staticmethod
    def check(flake8: dict[str, Any]) -> bool:
        """
        `extend-ignore` should be used instead of `ignore`, it is a shorter list
        that doesn't wipe defaults.
        """
        return "ignore" not in flake8 or "extend-ignore" in flake8


class FK003(Flake8):
    "Uses extend select"
    requires = {"FK001", "PC131"}

    @staticmethod
    def check(flake8: dict[str, Any]) -> bool:
        """
        `extend-select` should be used instead of `select`, it is a shorter list
        that doesn't wipe defaults.
        """
        return "select" not in flake8 or "extend-select" in flake8


repo_review_fixtures = {"flake8"}
repo_review_checks = {p.__name__ for p in Flake8.__subclasses__()}
