from __future__ import annotations

import dataclasses
import importlib.metadata
import inspect
import textwrap
import typing
from collections.abc import Callable, Iterable, Sequence
from graphlib import TopologicalSorter
from importlib.abc import Traversable
from typing import Any

from markdown_it import MarkdownIt

from .fixtures import pyproject
from .ratings import Rating

__all__ = ["Result", "ResultDict", "build", "process", "as_simple_dict"]


def __dir__() -> list[str]:
    return __all__


# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())

md = MarkdownIt()


# Helper to get the type in the JSON style returns
class ResultDict(typing.TypedDict):
    description: str
    result: bool | None
    err_msg: str


@dataclasses.dataclass(frozen=True, kw_only=True)
class Result:
    name: str
    description: str
    result: bool | None
    err_msg: str = ""

    def err_markdown(self) -> str:
        result: str = md.render(self.err_msg)
        return result

    def _without_name_dict(self) -> ResultDict:
        return ResultDict(
            description=self.description, result=self.result, err_msg=self.err_msg
        )


def build(
    check: type[Rating],
    package: Traversable,
    fixtures: Iterable[Callable[[Traversable], Any]],
) -> bool | None:
    kwargs: dict[str, Any] = {}
    signature = inspect.signature(check.check)
    if "package" in signature.parameters:
        kwargs["package"] = package

    for func in fixtures:
        if func.__name__ in signature.parameters:
            kwargs[func.__name__] = func(package)

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


def process(
    package: Traversable, *, ignore: Sequence[str] = ()
) -> dict[str, list[Result]]:
    """
    Process the package and return a dictionary of results.

    Parameters
    ----------
    package: Traversable | Path
        The Path(like) package to process

    ignore: Sequence[str]
        A list of checks to ignore
    """
    # Collect all installed plugins
    modules: list[str] = [
        ep.load()
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.ratings"
        )
    ]

    # Collect the checks
    ratings = [
        getattr(mod, rat)
        for mod in modules
        for rat in getattr(mod, "repo_review_checks", ())
    ]

    # Collect the fixtures
    fixtures = [pyproject] + [
        getattr(mod, fixt)
        for mod in modules
        for fixt in getattr(mod, "repo_review_fixtures", ())
    ]

    # Collect our own config
    config = pyproject(package).get("tool", {}).get("repo-review", {})  # type: ignore[arg-type]
    skip_checks = set(ignore) | set(config.get("ignore", ()))

    tasks: dict[str, type[Rating]] = {
        t.__name__: t for t in ratings if is_allowed(skip_checks, t.__name__)
    }
    graph: dict[str, set[str]] = {
        n: getattr(t, "requires", set()) for n, t in tasks.items()
    }
    completed: dict[str, bool | None] = {}

    # A few families are here to make sure they print first
    families: dict[str, set[str]] = {"general": set(), "pyproject": set()}
    for name, task in tasks.items():
        families.setdefault(task.family, set()).add(name)

    # Run all the checks in topological order
    ts = TopologicalSorter(graph)
    for name in ts.static_order():
        if all(completed.get(n, False) for n in graph[name]):
            completed[name] = build(tasks[name], package, fixtures)
        else:
            completed[name] = None

    # Collect the results
    results_dict = {}
    for family, ftasks in families.items():
        result_list = []
        for task_name in sorted(ftasks):
            check = tasks[task_name]
            result = completed[task_name]
            doc = check.__doc__ or ""

            result_list.append(
                Result(
                    name=task_name,
                    description=doc,
                    result=result,
                    err_msg=textwrap.dedent(doc.format(cls=check)),
                )
            )
        results_dict[family] = result_list

    return results_dict


def as_simple_dict(
    results_dict: dict[str, list[Result]]
) -> dict[str, dict[str, ResultDict]]:
    return {
        # pylint: disable-next=protected-access
        family: {result.name: result._without_name_dict() for result in results}
        for family, results in results_dict.items()
    }
