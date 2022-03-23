from __future__ import annotations

from typing import Any

## PP2xx: MyPy


class MyPy:
    pass


class PP200(MyPy):
    "Uses MyPy (pyproject config)"

    requires = {"PY001"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have tool.mypy"

        match pyproject:
            case {"tool": {"mypy": object()}}:
                return True
            case _:
                return False


class PP201(MyPy):
    "MyPy strict"

    requires = {"PP200"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have strict = true"

        match pyproject:
            case {"tool": {"mypy": {"strict": True}}}:
                return True
            case _:
                return False


class PP202(MyPy):
    "MyPy show error codes"

    requires = {"PP200"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have show_error_codes = true"

        match pyproject:
            case {"tool": {"mypy": {"show_error_codes": True}}}:
                return True
            case _:
                return False
