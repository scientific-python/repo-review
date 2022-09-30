from __future__ import annotations

import dataclasses
import importlib.metadata
import inspect
import textwrap
from collections.abc import Callable, Iterable
from graphlib import TopologicalSorter
from importlib.abc import Traversable
from typing import Any

from markdown_it import MarkdownIt

from .ratings import Rating

# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())

md = MarkdownIt()


@dataclasses.dataclass(frozen=True, kw_only=True)
class Result:
    name: str
    description: str
    result: bool | None
    err_msg: str = ""

    def err_markdown(self) -> str:
        result: str = md.render(self.err_msg)
        return result


def build(
    check: type[Rating],
    package: Traversable,
    fixtures: Iterable[Callable[[Traversable], Any]],
) -> bool | None:
    kwargs: dict[str, Any] = {}
    signature = inspect.signature(check.check)  # type: ignore[attr-defined]
    if "package" in signature.parameters:
        kwargs["package"] = package

    for func in fixtures:
        if func.__name__ in signature.parameters:
            kwargs[func.__name__] = func(package)

    return check.check(**kwargs)  # type: ignore[attr-defined, no-any-return]


def process(package: Traversable) -> dict[str, list[Result]]:
    modules: list[str] = [
        ep.load()
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.ratings"
        )
    ]

    ratings = [
        getattr(mod, rat)
        for mod in modules
        for rat in getattr(mod, "repo_review_checks", ())
    ]

    fixtures = [
        getattr(mod, fixt)
        for mod in modules
        for fixt in getattr(mod, "repo_review_fixtures", ())
    ]

    tasks = {t.__name__: t for t in ratings}
    graph: dict[str, set[str]] = {
        n: getattr(t, "requires", set()) for n, t in tasks.items()
    }
    completed: dict[str, bool | None] = {}

    # A few families are here to make sure they print first
    families: dict[str, set[str]] = {"general": set(), "pyproject": set()}
    for name, task in tasks.items():
        families.setdefault(task.family, set()).add(name)

    ts = TopologicalSorter(graph)
    for name in ts.static_order():
        if all(completed.get(n, False) for n in graph[name]):
            completed[name] = build(tasks[name], package, fixtures)
        else:
            completed[name] = None

    results_dict = {}
    for family, ftasks in families.items():
        result_list = []
        for task_name in sorted(ftasks):
            check = tasks[task_name]
            result = completed[task_name]

            result_list.append(
                Result(
                    name=task_name,
                    description=check.__doc__,
                    result=result,
                    err_msg=textwrap.dedent(check.check.__doc__.format(cls=check)),
                )
            )
        results_dict[family] = result_list

    return results_dict
