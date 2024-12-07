"""
Helpers for testing repo-review plugins.
"""

from __future__ import annotations

import importlib.metadata
import textwrap
from typing import Any

from ._compat import tomllib
from .checks import Check, get_check_url, process_result_bool
from .fixtures import apply_fixtures
from .processor import Result

__all__ = ["compute_check", "toml_loads"]


def __dir__() -> list[str]:
    return __all__


def toml_loads(contents: str, /) -> Any:
    """
    A helper function to quickly load a TOML string for Python 3.10+.

    :param contents: The TOML string to load.
    :return: The loaded TOML.

    .. versionadded:: 0.10.6
    """
    return tomllib.loads(contents)


def compute_check(name: str, /, **fixtures: Any) -> Result:
    """
    A helper function to compute a check given fixtures, intended for testing.
    Currently, all fixtures are required to be passed in as keyword arguments,
    transitive fixtures are not supported.

    :param name: The name of the check to compute.
    :param fixtures: The fixtures to use when computing the check.
    :return: The computed result.

    .. versionadded:: 0.10.5
    """

    check_functions = (
        ep.load() for ep in importlib.metadata.entry_points(group="repo_review.checks")
    )
    checks = {
        k: v
        for func in check_functions
        for k, v in apply_fixtures(fixtures, func).items()
    }
    check: Check = checks[name]
    completed_raw = apply_fixtures({"name": name, **fixtures}, check.check)
    completed = process_result_bool(completed_raw, check, name)
    result = None if completed is None else not completed
    doc = check.__doc__ or ""
    err_msg = completed or ""

    return Result(
        family=check.family,
        name=name,
        description=doc.format(self=check, name=name).strip(),
        result=result,
        err_msg=textwrap.dedent(err_msg),
        url=get_check_url(name, check),
    )
