from __future__ import annotations

from typing import Any

## PP2xx: MyPy


class MyPy:
    family = "mypy"


class PP200(MyPy):
    "Uses MyPy (pyproject config)"

    requires = {"PY001"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have `tool.mypy` section in `pyproject.toml`"

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
        "Must have `strict = true`"

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
        "Must have `show_error_codes = true`"

        match pyproject:
            case {"tool": {"mypy": {"show_error_codes": True}}}:
                return True
            case _:
                return False


class PP203(MyPy):
    "MyPy warn unreachable"

    requires = {"PP200"}

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        "Must have warn_unreachable = true"

        match pyproject:
            case {"tool": {"mypy": {"warn_unreachable": True}}}:
                return True
            case _:
                return False


class PP204(MyPy):
    "MyPy enables ignore-without-code"

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """Must have `"ignore-without-code"` in `enable_error_code`"""

        match pyproject:
            case {"tool": {"mypy": {"enable_error_code": list(codes)}}}:
                return "ignore-without-code" in codes
            case _:
                return False


class PP205(MyPy):
    "MyPy enables redundant-expr"

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """Must have `"redundant-expr"` in `enable_error_code`"""

        match pyproject:
            case {"tool": {"mypy": {"enable_error_code": list(codes)}}}:
                return "redundant-expr" in codes
            case _:
                return False


class PP206(MyPy):
    "MyPy enables truthy-bool"

    @staticmethod
    def check(pyproject: dict[str, Any]) -> bool:
        """Must have `"truthy-bool"` in `enable_error_code`"""

        match pyproject:
            case {"tool": {"mypy": {"enable_error_code": list(codes)}}}:
                return "truthy-bool" in codes
            case _:
                return False


repo_review_fixtures = set[str]()
repo_review_checks = {p.__name__ for p in MyPy.__subclasses__()}
