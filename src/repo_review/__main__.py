from __future__ import annotations

import itertools
import json
import sys
import typing
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

import click as orig_click

if typing.TYPE_CHECKING:
    import click  # pylint: disable=reimported
else:
    import rich_click as click

import rich.console
import rich.markdown
import rich.syntax
import rich.terminal_theme
import rich.text
import rich.traceback
import rich.tree

from . import __version__
from ._compat.importlib.resources.abc import Traversable
from ._compat.typing import assert_never
from .checks import get_check_description, get_check_url
from .families import Family, get_family_name
from .ghpath import GHPath
from .html import to_html
from .processor import Result, as_simple_dict, collect_all, process

__all__ = ["main"]


def __dir__() -> list[str]:
    return __all__


rich.traceback.install(suppress=[click, rich, orig_click], show_locals=True, width=None)


def list_all(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return

    collected = collect_all()
    if len(collected.checks) == 0:
        msg = "No checks registered. Please install a repo-review plugin."
        raise click.ClickException(msg)

    for family, grp in itertools.groupby(
        collected.checks.items(), key=lambda x: x[1].family
    ):
        rich.print(f"  [dim]# {get_family_name(collected.families, family)}")
        for code, check in grp:
            url = get_check_url(code, check)
            doc = get_check_description(code, check)
            link = f"[link={url}]{code}[/link]" if url else code
            comment = f" [dim]# {doc}" if doc else ""
            rich.print(f'  "{link}",{comment}')

    ctx.exit()


def rich_printer(
    families: Mapping[str, Family],
    processed: list[Result],
    *,
    svg: bool = False,
    stderr: bool = False,
    color: bool = True,
) -> None:
    console = rich.console.Console(
        record=svg, quiet=svg, stderr=stderr, color_system="auto" if color else None
    )

    for family, results_list in itertools.groupby(processed, lambda r: r.family):
        family_name = get_family_name(families, family)
        tree = rich.tree.Tree(f"[bold]{family_name}[/bold]:")
        for result in results_list:
            style = (
                "yellow"
                if result.result is None
                else "green"
                if result.result
                else "red"
            )
            description = (
                f"[link={result.url}]{result.description}[/link]"
                if result.url
                else result.description
            )
            msg = rich.text.Text()
            msg.append(result.name, style="bold")
            msg.append(" ")
            msg.append(rich.text.Text.from_markup(description, style=style))
            if result.result is None:
                msg.append(" [skipped]", style="yellow bold")
                tree.add(msg)
            elif result.result:
                msg.append(rich.text.Text.from_markup(" :white_check_mark:"))
                tree.add(msg)
            else:
                msg.append(rich.text.Text.from_markup(" :x:"))
                detail = rich.markdown.Markdown(result.err_msg)
                msg_grp = rich.console.Group(msg, detail)
                tree.add(msg_grp)

        console.print(tree)
        console.print()

    if len(processed) == 0:
        console.print("[bold red]No checks ran")

    if svg:
        str = console.export_svg(theme=rich.terminal_theme.DEFAULT_TERMINAL_THEME)
        if color:
            rich.print(
                rich.syntax.Syntax(str, lexer="xml"),
                file=sys.stderr if stderr else sys.stdout,
            )
        else:
            print(str, file=sys.stderr if stderr else sys.stdout)


def display_output(
    families: Mapping[str, Family],
    processed: list[Result],
    *,
    format_opt: Literal["rich", "json", "html", "svg"],
    stderr: bool,
    color: bool,
) -> None:
    match format_opt:
        case "rich" | "svg":
            rich_printer(
                families, processed, svg=format_opt == "svg", stderr=stderr, color=color
            )
        case "json":
            j = json.dumps(
                {"families": families, "checks": as_simple_dict(processed)}, indent=2
            )
            console = rich.console.Console(
                stderr=stderr, color_system="auto" if color else None
            )
            console.print_json(j)
        case "html":
            html = to_html(families, processed)
            if color:
                rich.print(
                    rich.syntax.Syntax(html, lexer="html"),
                    file=sys.stderr if stderr else sys.stdout,
                )
            else:
                print(html, file=sys.stderr if stderr else sys.stdout)
        case _:
            assert_never(format_opt)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__)
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
@click.option(
    "--format",
    "format_opt",
    type=click.Choice(["rich", "json", "html", "svg"]),
    default="rich",
    help="Select output format.",
)
@click.option(
    "--stderr",
    "stderr_fmt",
    type=click.Choice(["rich", "json", "html", "svg"]),
    help="Select additional output format for stderr. Will disable terminal escape codes for stdout for easy redirection.",
)
@click.option(
    "--select",
    help="Only run certain checks, comma separated. All checks run if empty.",
    default="",
)
@click.option(
    "--ignore",
    help="Ignore a check or checks, comma separated.",
    default="",
)
@click.option(
    "--package-dir",
    "-p",
    help="Path to python package.",
    default="",
)
@click.option(
    "--list-all",
    is_flag=True,
    callback=list_all,
    expose_value=False,
    is_eager=True,
    help="List all checks and exit",
)
def main(
    package: Traversable,
    format_opt: Literal["rich", "json", "html"],
    stderr_fmt: Literal["rich", "json", "html"] | None,
    select: str,
    ignore: str,
    package_dir: str,
) -> None:
    """
    Pass in a local Path or gh:org/repo@branch.
    """
    ignore_list = {x.strip() for x in ignore.split(",") if x}
    select_list = {x.strip() for x in select.split(",") if x}

    collected = collect_all(package, subdir=package_dir)
    if len(collected.checks) == 0:
        msg = "No checks registered. Please install a repo-review plugin."
        raise click.ClickException(msg)

    if str(package).startswith("gh:"):
        _, org_repo_branch, *p = str(package).split(":", maxsplit=2)
        org_repo, branch = org_repo_branch.split("@", maxsplit=1)
        package = GHPath(repo=org_repo, branch=branch, path=p[0] if p else "")
        if format_opt == "rich":
            rich.print(f"[bold]Processing [blue]{package}[/blue] from GitHub\n")

    families, processed = process(
        package, select=select_list, ignore=ignore_list, subdir=package_dir
    )

    display_output(
        families,
        processed,
        format_opt=format_opt,
        stderr=False,
        color=stderr_fmt is None,
    )
    if stderr_fmt:
        display_output(
            families, processed, format_opt=stderr_fmt, stderr=True, color=True
        )

    if any(p.result is False for p in processed):
        raise SystemExit(2)
    if len(processed) == 0:
        raise SystemExit(3)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
