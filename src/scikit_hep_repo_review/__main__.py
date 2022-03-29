from __future__ import annotations

import importlib.metadata
import inspect
import textwrap
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Any, Callable, Iterable

import click
import rich.traceback
import rich.tree
from rich import print

from .ratings import Rating

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)

# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())


def build(
    check: type[Rating], package: Path, fixtures: Iterable[Callable[[Path], Any]]
) -> bool | None:
    kwargs: dict[str, Any] = {}
    signature = inspect.signature(check.check)  # type: ignore[attr-defined]
    if "package" in signature.parameters:
        kwargs["package"] = package

    for func in fixtures:
        if func.__name__ in signature.parameters:
            kwargs[func.__name__] = func(package)

    return check.check(**kwargs)  # type: ignore[attr-defined, no-any-return]


@click.command()
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
def main(package: Path) -> None:

    modules: list[str] = [
        ep.load()  # type: ignore[attr-defined]
        for ep in importlib.metadata.entry_points(
            group="scikit_hep_repo_review.ratings"  # type: ignore[call-arg]
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
    completed: dict[str, Any] = {}

    # A few families are here to make sure they print first
    families = {"general": set(), "pyproject": set()}
    for name, task in tasks.items():
        families.setdefault(task.family, set()).add(name)

    ts = TopologicalSorter(graph)
    completed = {
        name: build(tasks[name], package, fixtures) for name in ts.static_order()
    }

    print() 
    for family, ftasks in families.items():
        tree = rich.tree.Tree(f"[bold]{family}[/bold]:")
        for task_name in sorted(ftasks):
            check = tasks[task_name]

            msg = f"[bold]{task_name}[/bold] "
            if not all(completed.get(n, False) for n in graph[task_name]):
                msg += f"[yellow]{check.__doc__} [bold]\\[skipped]"
            elif completed[task_name]:
                msg += f"[green]{check.__doc__}? :white_check_mark:"
            else:
                msg += f"[red]{check.__doc__}? :x:[/red]\n"
                msg += (
                    "[dim]"
                    + " ".join(
                        textwrap.dedent(check.check.__doc__.format(cls=check))
                        .strip()
                        .splitlines()
                    )
                )
            tree.add(msg)
        print(tree)
        print()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
