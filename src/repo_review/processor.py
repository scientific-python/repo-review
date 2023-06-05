from __future__ import annotations

import dataclasses
import graphlib
import textwrap
import typing
from collections.abc import Set
from typing import Any

import markdown_it

from ._compat.importlib.resources.abc import Traversable
from .checks import Check, collect_checks, is_allowed
from .families import Family, collect_families
from .fixtures import apply_fixtures, collect_fixtures, compute_fixtures, pyproject

__all__ = [
    "Result",
    "ResultDict",
    "ProcessReturn",
    "process",
    "as_simple_dict",
    "_collect_all",
]


def __dir__() -> list[str]:
    return __all__


md = markdown_it.MarkdownIt()


# Helper to get the type in the JSON style returns
class ResultDict(typing.TypedDict):
    family: str
    description: str
    result: bool | None
    err_msg: str
    url: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class Result:
    family: str
    name: str
    description: str
    result: bool | None
    err_msg: str = ""
    url: str = ""

    def err_markdown(self) -> str:
        result: str = md.render(self.err_msg).strip()
        return result.removeprefix("<p>").removesuffix("</p>").strip()


class ProcessReturn(typing.NamedTuple):
    families: dict[str, Family]
    results: list[Result]


def _collect_all(
    root: Traversable, subdir: str = ""
) -> tuple[dict[str, Any], dict[str, Check], dict[str, Family]]:
    package = root.joinpath(subdir) if subdir else root

    # Collect the fixtures
    fixture_functions = collect_fixtures()
    fixtures = compute_fixtures(root, package, fixture_functions)

    # Collect the checks
    checks = collect_checks(fixtures)

    # Collect families.
    families = collect_families()

    # These are optional, so fill in missing families.
    for name in {c.family for c in checks.values()}:
        if name not in families:
            families[name] = Family()

    return fixtures, checks, families


def process(
    root: Traversable,
    *,
    select: Set[str] = frozenset(),
    ignore: Set[str] = frozenset(),
    subdir: str = "",
) -> ProcessReturn:
    """
    Process the package and return a dictionary of results.

    Parameters
    ----------
    root: Traversable | Path
        The Path(like) to the repository to process

    ignore: Sequence[str]
        A list of checks to ignore

    subidr: str
        The path to the package in the subdirectory, if not at the root of the repository.
    """
    package = root.joinpath(subdir) if subdir else root

    fixtures, tasks, families = _collect_all(root, subdir)

    # Collect our own config
    config = pyproject(package).get("tool", {}).get("repo-review", {})
    select_checks = select if select else set(config.get("select", ()))
    skip_checks = ignore if ignore else set(config.get("ignore", ()))

    # Make a graph of the check's interdependencies
    graph: dict[str, set[str]] = {
        n: getattr(t, "requires", set()) for n, t in tasks.items()
    }
    # Keep track of which checks have been completed
    completed: dict[str, str | None] = {}

    # Run all the checks in topological order based on their dependencies
    ts = graphlib.TopologicalSorter(graph)
    for name in ts.static_order():
        if all(completed.get(n, "") == "" for n in graph[name]):  # noqa: PLC1901
            result = apply_fixtures(fixtures, tasks[name].check)
            if isinstance(result, bool):
                completed[name] = "" if result else tasks[name].check.__doc__
            else:
                completed[name] = result
        else:
            completed[name] = None

    # Collect the results
    result_list = []
    for task_name, check in sorted(
        tasks.items(),
        key=lambda x: (families[x[1].family].get("order", 0), x[1].family, x[0]),
    ):
        result = None if completed[task_name] is None else not completed[task_name]
        doc = check.__doc__ or ""
        err_msg = completed[task_name] or ""

        if not is_allowed(select_checks, skip_checks, task_name):
            continue

        result_list.append(
            Result(
                family=check.family,
                name=task_name,
                description=doc.format(self=check, name=task_name),
                result=result,
                err_msg=textwrap.dedent(err_msg.format(self=check, name=task_name)),
                url=getattr(check, "url", "").format(self=check, name=task_name),
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
