from __future__ import annotations

import graphlib
import importlib.metadata
import inspect
import typing
from collections.abc import Callable, Mapping, Set
from typing import Any

from ._compat import tomllib
from ._compat.importlib.resources.abc import Traversable
from .ghpath import EmptyTraversable

__all__ = [
    "pyproject",
    "list_all",
    "compute_fixtures",
    "apply_fixtures",
    "collect_fixtures",
]


def __dir__() -> list[str]:
    return __all__


def pyproject(package: Traversable) -> dict[str, Any]:
    """
    Fixture: The ``pyproject.toml`` structure from the package. Returned an
    empty dict if no pyproject.toml found.

    :param package: The package fixture.

    :return: The pyproject.toml dict or an empty dict if no file found.
    """
    pyproject_path = package.joinpath("pyproject.toml")
    if pyproject_path.is_file():
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    return {}


def list_all(root: Traversable) -> bool:
    """
    Fixture: Is True when this is trying to produce a list of all checks.

    :param root: The root fixture.

    :return: True only if trying to make a list of all checks/fixtures/families.

    .. versionadded:: 0.8
    """

    return isinstance(root, EmptyTraversable)


def compute_fixtures(
    root: Traversable,
    package: Traversable,
    unevaluated_fixtures: Mapping[str, Callable[..., Any]],
) -> dict[str, Any]:
    """
    Given the repo ``root`` Traversable, the ``package`` Traversable, and the dict
    of all fixture callables, compute the dict of fixture results.

    :param root: The root of the repository
    :param package: The path to the package (``root / subdir``)
    :param unevaluated_fixtures: The unevaluated mapping of fixture names to
                                 callables.

    :return: The fully evaluated dict of fixtures.
    """
    fixtures: dict[str, Any] = {"root": root, "package": package}
    graph: dict[str, Set[str]] = {"root": set(), "package": set()}
    graph |= {
        name: inspect.signature(fix).parameters.keys()
        for name, fix in unevaluated_fixtures.items()
    }
    ts = graphlib.TopologicalSorter(graph)
    for fixture_name in ts.static_order():
        if fixture_name in {"package", "root"}:
            continue
        func = unevaluated_fixtures[fixture_name]
        signature = inspect.signature(func)
        kwargs = {name: fixtures[name] for name in signature.parameters}
        fixtures[fixture_name] = unevaluated_fixtures[fixture_name](**kwargs)
    return fixtures


T = typing.TypeVar("T")


def apply_fixtures(fixtures: Mapping[str, Any], func: Callable[..., T]) -> T:
    """
    Given the pre-computed dict of fixtures and a function, fill in any
    fixtures from that dict that it requests and return the result.

    :param fixtures: Fully evaluated dict of fixtures.
    :param func: Some callable that can take fixtures.
    """
    signature = inspect.signature(func)
    kwargs = {
        name: value for name, value in fixtures.items() if name in signature.parameters
    }
    return func(**kwargs)


def collect_fixtures() -> dict[str, Callable[[Traversable], Any]]:
    """
    Produces a dict of fixture callables based on installed entry points. You
    should call :func:`compute_fixtures` on the result to get the standard dict of
    fixture results that most other functions in repo-review expect.

    :return: A dict of unevaluated fixtures.
    """
    return {
        ep.name: ep.load()
        for ep in importlib.metadata.entry_points(group="repo_review.fixtures")
    }
