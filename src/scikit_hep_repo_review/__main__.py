from __future__ import annotations

import inspect
import textwrap
from graphlib import TopologicalSorter
from pathlib import Path
from typing import Any

import click
import rich.traceback
import tomli as tomllib
import yaml
from rich import print

from .ratings import Rating, general, mypy, precommit, pyproject

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)


def build(
    check: type[Rating],
    *,
    package: Path,
    pyproject: dict[str, Any],
    precommit: dict[str, Any],
) -> bool | None:
    kwargs: dict[str, Any] = {}
    signature = inspect.signature(check.check)  # type: ignore[attr-defined]
    if "package" in signature.parameters:
        kwargs["package"] = package
    if "pyproject" in signature.parameters:
        kwargs["pyproject"] = pyproject
    if "precommit" in signature.parameters:
        kwargs["precommit"] = precommit
    return check.check(**kwargs)  # type: ignore[attr-defined, no-any-return]


# Supported arguments:
# package: Path
# pyproject: Dict[str, Any]


@click.command()
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
def main(package: Path) -> None:
    pyproject_path = package.joinpath("pyproject.toml")
    pyproject: dict[str, Any]
    if pyproject_path.exists():
        with pyproject_path.open("rb") as f:
            pyproject = tomllib.load(f)
    else:
        pyproject = {}

    precommit_path = package.joinpath(".pre-commit-config.yaml")
    precommit: dict[str, Any]
    if precommit_path.exists():
        with precommit_path.open("rb") as f:
            precommit = yaml.safe_load(f)
    else:
        precommit = {}

    tasks = {t.__name__: t for t in Rating.__subclasses__()}
    graph = {n: t.requires for n, t in tasks.items()}
    completed: dict[str, Any] = {}

    ts = TopologicalSorter(graph)
    for task_name in ts.static_order():
        print(f"[bold]{task_name}", end=" ")

        check = tasks[task_name]
        if not all(completed.get(n, False) for n in check.requires):
            print(rf"[yellow]{check.__doc__} [bold]\[skipped]")
            continue

        print(f"[green]{check.__doc__}?...", end=" ")

        completed[task_name] = build(
            check, package=package, pyproject=pyproject, precommit=precommit
        )
        if completed[task_name]:
            print(":white_check_mark:")
        else:
            print(":x:")
            print(
                "      "
                + " ".join(textwrap.dedent(check.check.__doc__).strip().splitlines())  # type: ignore[attr-defined]
            )


if __name__ == "__main__":
    main()
