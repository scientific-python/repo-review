from __future__ import annotations

import copy
import dataclasses
import graphlib
import textwrap
import typing
import warnings
from collections.abc import Mapping, Set
from typing import Any, TypeVar

import markdown_it

from ._compat.importlib.resources.abc import Traversable
from .checks import (
    Check,
    collect_checks,
    get_check_url,
    is_allowed,
    process_result_bool,
)
from .families import Family, collect_families
from .fixtures import apply_fixtures, collect_fixtures, compute_fixtures, pyproject
from .ghpath import EmptyTraversable

__all__ = [
    "CollectionReturn",
    "ProcessReturn",
    "Result",
    "ResultDict",
    "as_simple_dict",
    "collect_all",
    "md_as_html",
    "process",
]


def __dir__() -> list[str]:
    return __all__


md = markdown_it.MarkdownIt()


def md_as_html(md_text: str) -> str:
    """
    Heler function that converts markdown text to HTML. Strips paragraph tags from the result.

    :param md_text: The markdown text to convert.
    """
    result: str = md.render(md_text).strip()
    return result.removeprefix("<p>").removesuffix("</p>").strip()


class ResultDict(typing.TypedDict):
    """
    Helper to get the type in the JSON style returns. Basically identical to
    :class:`Result` but in dict form and without the name.
    """

    family: str  #: The family string
    description: str  #: The short description of what the check looks for
    result: bool | None  #: The result, None means skip
    err_msg: str  #: The error message if the result is false, in markdown format
    url: str  #: An optional URL (empty string if missing)


@dataclasses.dataclass(frozen=True, kw_only=True)
class Result:
    """
    This is the returned value from a processed check.
    """

    family: str  #: The family string
    name: str  #: The name of the check
    description: str  #: The short description of what the check looks for
    result: bool | None  #: The result, None means skip
    err_msg: str = ""  #: The error message if the result is false, in markdown format
    url: str = ""  #: An optional URL (empty string if missing)

    def err_as_html(self) -> str:
        """
        Produces HTML from the error message, assuming it is in markdown.
        """
        return md_as_html(self.err_msg)


class ProcessReturn(typing.NamedTuple):
    """
    Return type for :func:`process`.
    """

    families: dict[
        str, Family
    ]  #: A mapping of family strings to :class:`.Family` info dicts
    results: list[Result]  #: The results list


class CollectionReturn(typing.NamedTuple):
    """
    Return type for :func:`collect_all`.

    .. versionadded:: 0.8
    """

    fixtures: dict[str, Any]  #: The computed fixtures, as a :class:`dict`
    checks: dict[str, Check]  #: The checks dict, sorted by :class:`.Family`.
    families: dict[
        str, Family
    ]  #: A mapping of family strings to :class:`.Family` info dicts


class HasFamily(typing.Protocol):
    """
    Simple :class:`~typing.Protocol` to see if family property is present.
    """

    @property
    def family(self) -> str: ...


T = TypeVar("T", bound=HasFamily)


def _sort_by_family(
    families: Mapping[str, Family], dict_has_family: Mapping[str, T]
) -> dict[str, T]:
    return dict(
        sorted(
            dict_has_family.items(),
            key=lambda x: (families[x[1].family].get("order", 0), x[1].family, x[0]),
        )
    )


def collect_all(
    root: Traversable = EmptyTraversable(),  # noqa: B008 (frozen dataclass OK)
    subdir: str = "",
) -> CollectionReturn:
    """
    Collect all checks. If ``root`` is not passed, then checks are collected
    with a :class:`~repo_review.ghpath.EmptyTraversable`. Any checks that are
    returned conditionally based on fixture results might not be collected
    unless :func:`~repo_review.fixtures.list_all` is used.

    :param root: If passed, this is the root of the repo (for fixture computation).
    :param subdir: The subdirectory (for fixture computation).

    :return: The collected fixtures, checks, and families. Families is
             guaranteed to include all families and be in order.

    .. versionadded:: 0.8
    """
    package = root.joinpath(subdir) if subdir else root

    # Collect the fixtures
    fixture_functions = collect_fixtures()
    fixtures = compute_fixtures(root, package, fixture_functions)

    # Collect the checks
    checks = collect_checks(fixtures)

    # Collect families.
    families = collect_families(fixtures)

    # These are optional, so fill in missing families.
    for name in {c.family for c in checks.values()}:
        if name not in families:
            families[name] = Family()

    # Sort results
    checks = _sort_by_family(families, checks)

    return CollectionReturn(fixtures, checks, families)


def process(
    root: Traversable,
    *,
    select: Set[str] = frozenset(),
    ignore: Set[str] = frozenset(),
    subdir: str = "",
) -> ProcessReturn:
    """
    Process the package and return a dictionary of results.

    :param root: The Traversable to the repository to process.
    :param select: A list of checks to select. All checks selected if empty.
    :param ignore: A list of checks to ignore.
    :param subdir: The path to the package in the subdirectory, if not at the
                   root of the repository.

    :return: The families and a list of checks. Families is guaranteed to
             include all families and be in order.
    """
    package = root.joinpath(subdir) if subdir else root

    fixtures, tasks, families = collect_all(root, subdir)

    # Collect our own config
    config = pyproject(package).get("tool", {}).get("repo-review", {})
    select_checks = select if select else frozenset(config.get("select", ()))
    skip_checks = ignore if ignore else frozenset(config.get("ignore", ()))

    # Make a graph of the check's interdependencies
    graph: dict[str, Set[str]] = {
        n: getattr(t, "requires", frozenset()) for n, t in tasks.items()
    }
    for name, s in graph.items():
        if not isinstance(s, Set):
            msg = f"requires must be a set, got {s!r} for {name!r}"  # type: ignore[unreachable]
            raise TypeError(msg)

    # Keep track of which checks have been completed
    completed: dict[str, str | None] = {}
    fixtures_copy = copy.deepcopy(fixtures)

    # Run all the checks in topological order based on their dependencies
    ts = graphlib.TopologicalSorter(graph)
    for name in ts.static_order():
        if all(completed.get(n, "") == "" for n in graph[name]):
            result = apply_fixtures({"name": name, **fixtures_copy}, tasks[name].check)
            completed[name] = process_result_bool(result, tasks[name], name)
            if fixtures != fixtures_copy:
                fixtures_copy = copy.deepcopy(fixtures)
                msg = f"{name} modified the input fixtures! Making a deepcopy to fix and continue."
                warnings.warn(msg, stacklevel=1)
        else:
            completed[name] = None

    # Collect the results
    result_list = []
    for task_name, check in _sort_by_family(families, tasks).items():
        result = None if completed[task_name] is None else not completed[task_name]
        doc = check.__doc__ or ""
        err_msg = completed[task_name] or ""

        if not is_allowed(select_checks, skip_checks, task_name):
            continue

        result_list.append(
            Result(
                family=check.family,
                name=task_name,
                description=doc.format(self=check, name=task_name).strip(),
                result=result,
                err_msg=textwrap.dedent(err_msg),
                url=get_check_url(task_name, check),
            )
        )

    return ProcessReturn(families, result_list)


def as_simple_dict(results: list[Result]) -> dict[str, ResultDict]:
    """
    Convert a results list into a simple dict of dicts structure. The name of
    the result turns into the key of the outer dict.

    :param results: The list of results.
    """
    return {
        result.name: typing.cast(
            ResultDict,
            {k: v for k, v in dataclasses.asdict(result).items() if k != "name"},
        )
        for result in results
    }
