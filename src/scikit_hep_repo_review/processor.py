from __future__ import annotations

import dataclasses
import importlib.metadata
import inspect
import textwrap
import typing
from collections.abc import Callable, Mapping, Sequence
from graphlib import TopologicalSorter
from typing import Any, TypeVar

from markdown_it import MarkdownIt

from ._compat.importlib.resources.abc import Traversable
from .checks import Check
from .families import Family
from .fixtures import pyproject

__all__ = ["Result", "ResultDict", "ProcessReturn", "process", "as_simple_dict"]


def __dir__() -> list[str]:
    return __all__


T = TypeVar("T")

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


class ProcessReturn(typing.NamedTuple):
    families: dict[str, Family]
    results: list[Result]


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


def compute_fixtures(
    package: Traversable, fixtures: Mapping[str, Callable[..., Any]]
) -> dict[str, Any]:
    results: dict[str, Any] = {"package": package}
    graph = {
        name: set() if name == "package" else inspect.signature(fix).parameters.keys()
        for name, fix in fixtures.items()
    }
    ts = TopologicalSorter(graph)
    for fixture_name in ts.static_order():
        if fixture_name == "package":
            continue
        func = fixtures[fixture_name]
        signature = inspect.signature(func)
        kwargs = {name: results[name] for name in signature.parameters}
        results[fixture_name] = fixtures[fixture_name](**kwargs)
    return results


def apply_fixtures(computed_fixtures: Mapping[str, Any], func: Callable[..., T]) -> T:
    signature = inspect.signature(func)
    kwargs = {
        name: value
        for name, value in computed_fixtures.items()
        if name in signature.parameters
    }
    return func(**kwargs)


def collect_fixtures() -> dict[str, Callable[[Traversable], Any]]:
    return {
        ep.name: ep.load()
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.fixtures"
        )
    }


def collect_checks(fixtures: Mapping[str, Any]) -> dict[str, Check]:
    check_functions = (
        ep.load()
        for ep in importlib.metadata.entry_points(group="scikit_hep_repo_review.checks")
    )

    return {
        k: v
        for func in check_functions
        for k, v in apply_fixtures(fixtures, func).items()
    }


def collect_families() -> dict[str, Family]:
    return {
        name: family
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.families"
        )
        for name, family in ep.load()().items()
    }


def process(package: Traversable, *, ignore: Sequence[str] = ()) -> ProcessReturn:
    """
    Process the package and return a dictionary of results.

    Parameters
    ----------
    package: Traversable | Path
        The Path(like) package to process

    ignore: Sequence[str]
        A list of checks to ignore
    """
    # Collect the fixtures
    fixture_functions = collect_fixtures()
    fixtures = compute_fixtures(package, fixture_functions)

    # Collect the checks
    checks = collect_checks(fixtures)

    # Collect families.
    families = collect_families()

    # These are optional, so fill in missing families.
    for name in {c.family for c in checks.values()}:
        if name not in families:
            families[name] = Family()

    # Collect our own config
    config = pyproject(package).get("tool", {}).get("repo-review", {})
    skip_checks = set(ignore) | set(config.get("ignore", ()))

    tasks: dict[str, Check] = {
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
            completed[name] = apply_fixtures(fixtures, tasks[name].check)
        else:
            completed[name] = None

    # Collect the results
    result_list = []
    for task_name, check in sorted(
        tasks.items(),
        key=lambda x: (families[x[1].family].get("order", 0), x[1].family, x[0]),
    ):
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

    return ProcessReturn(families, result_list)


def as_simple_dict(results: list[Result]) -> dict[str, ResultDict]:
    return {
        result.name: typing.cast(
            ResultDict,
            {k: v for k, v in dataclasses.asdict(result).items() if k != "name"},
        )
        for result in results
    }
