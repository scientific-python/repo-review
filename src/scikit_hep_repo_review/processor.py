from __future__ import annotations

import dataclasses
import importlib.metadata
import inspect
import textwrap
import typing
from collections.abc import Callable, Mapping, Sequence
from graphlib import TopologicalSorter
from importlib.abc import Traversable
from typing import Any

from markdown_it import MarkdownIt

from .checks import Check
from .fixtures import pyproject

__all__ = ["Result", "ResultDict", "build", "process", "as_simple_dict"]


def __dir__() -> list[str]:
    return __all__


md = MarkdownIt()


# Helper to get the type in the JSON style returns
class ResultDict(typing.TypedDict):
    family: str
    description: str
    result: bool | None
    err_msg: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class Result:
    family: str
    name: str
    description: str
    result: bool | None
    err_msg: str = ""

    def err_markdown(self) -> str:
        result: str = md.render(self.err_msg)
        return result


def build(
    check: type[Check],
    package: Traversable,
    fixtures: Mapping[str, Callable[[Traversable], Any]],
) -> bool | None:
    kwargs: dict[str, Any] = {}
    signature = inspect.signature(check.check)

    # Built-in fixture
    if "package" in signature.parameters:
        kwargs["package"] = package

    for name, func in fixtures.items():
        if name in signature.parameters:
            kwargs[name] = func(package)

    return check.check(**kwargs)


def is_allowed(ignore_list: set[str], name: str) -> bool:
    """
    Skips the check if the name is in the ignore list or if the name without
    the number is in the ignore list.
    """
    if name in ignore_list:
        return False
    if name.rstrip("0123456789") in ignore_list:
        return False
    return True


def collect_checks() -> dict[str, type[Check]]:
    return {
        k: v
        for ep in importlib.metadata.entry_points(group="scikit_hep_repo_review.checks")
        for k, v in ep.load()().items()
    }


def collect_fixtures() -> dict[str, Callable[[Traversable], Any]]:
    return {
        ep.name: ep.load()
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.fixtures"
        )
    }


def process(package: Traversable, *, ignore: Sequence[str] = ()) -> list[Result]:
    """
    Process the package and return a dictionary of results.

    Parameters
    ----------
    package: Traversable | Path
        The Path(like) package to process

    ignore: Sequence[str]
        A list of checks to ignore
    """
    # Collect the checks
    checks = collect_checks()

    # Collect the fixtures
    fixtures = collect_fixtures()

    # Collect our own config
    config = pyproject(package).get("tool", {}).get("repo-review", {})  # type: ignore[arg-type]
    skip_checks = set(ignore) | set(config.get("ignore", ()))

    tasks: dict[str, type[Check]] = {
        n: r for n, r in checks.items() if is_allowed(skip_checks, n)
    }
    graph: dict[str, set[str]] = {
        n: getattr(t, "requires", set()) for n, t in tasks.items()
    }
    completed: dict[str, bool | None] = {}

    # Run all the checks in topological order
    ts = TopologicalSorter(graph)
    for name in ts.static_order():
        if all(completed.get(n, False) for n in graph[name]):
            completed[name] = build(tasks[name], package, fixtures)
        else:
            completed[name] = None

    # Collect the results
    result_list = []
    for task_name, check in sorted(tasks.items(), key=lambda x: (x[1].family, x[0])):
        result = completed[task_name]
        doc = check.__doc__ or ""

        result_list.append(
            Result(
                family=check.family,
                name=task_name,
                description=doc,
                result=result,
                err_msg=textwrap.dedent(doc.format(cls=check)),
            )
        )

    return result_list


def as_simple_dict(results: list[Result]) -> dict[str, ResultDict]:
    return {
        result.name: typing.cast(
            ResultDict,
            {k: v for k, v in dataclasses.asdict(result).items() if k != "name"},
        )
        for result in results
    }
