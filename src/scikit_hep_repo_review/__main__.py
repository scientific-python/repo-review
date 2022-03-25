from __future__ import annotations

import functools
import importlib.metadata
import inspect
import textwrap
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Any

import click
import rich.traceback
import tomli as tomllib
from rich import print

from .ratings import Rating

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)


@functools.cache
def pyproject(package: Path) -> dict[str, Any]:
    pyproject_path = package.joinpath("pyproject.toml")
    if pyproject_path.exists():
        with pyproject_path.open("rb") as f:
            return tomllib.load(f)
    return {}


def build(
    check: type[Rating],
    *,
    package: Path,
) -> bool | None:
    kwargs: dict[str, Any] = {}
    signature = inspect.signature(check.check)  # type: ignore[attr-defined]
    if "package" in signature.parameters:
        kwargs["package"] = package
    if "pyproject" in signature.parameters:
        kwargs["pyproject"] = pyproject(package)

    for arg in getattr(check, "provides", set()):
        kwargs[arg] = getattr(check, arg)(package)

    return check.check(**kwargs)  # type: ignore[attr-defined, no-any-return]


# Supported arguments:
# package: Path
# pyproject: Dict[str, Any]


@click.command()
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
def main(package: Path) -> None:

    ratings = (
        rat
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.ratings"  # type: ignore[call-arg]
        )
        for rat in ep.load().__subclasses__()  # type: ignore[attr-defined]
    )

    tasks = {t.__name__: t for t in ratings}
    graph: dict[str, set[str]] = {
        n: getattr(t, "requires", set()) for n, t in tasks.items()
    }
    completed: dict[str, Any] = {}

    ts = TopologicalSorter(graph)
    for task_name in ts.static_order():
        print(f"[bold]{task_name}", end=" ")

        check = tasks[task_name]
        if not all(completed.get(n, False) for n in graph[task_name]):
            print(rf"[yellow]{check.__doc__} [bold]\[skipped]")
            continue

        completed[task_name] = build(check, package=package)
        if completed[task_name]:
            print(f"[green]{check.__doc__}?... :white_check_mark:")
        else:
            print(f"[red]{check.__doc__}?... :x:")
            print(
                "      "
                + " ".join(
                    textwrap.dedent(check.check.__doc__.format(cls=check))
                    .strip()
                    .splitlines()
                )
            )


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
