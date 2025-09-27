from __future__ import annotations

import functools
import importlib.metadata
import itertools
import json
import os
import sys
import typing
import urllib.error
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import click as orig_click

if typing.TYPE_CHECKING:
    import click  # pylint: disable=reimported
else:
    import rich_click as click

import rich
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
from .families import Family, get_family_description, get_family_name
from .ghpath import GHPath
from .html import to_html
from .processor import Result, as_simple_dict, collect_all, process

__all__ = ["Formats", "Show", "Status", "main"]

CODE_THEME = "ansi_light"


def __dir__() -> list[str]:
    return __all__


rich.traceback.install(
    suppress=[click, rich, orig_click], show_locals=False, width=None
)

Status = Literal["empty", "passed", "skips", "errors"]
Formats = Literal["rich", "json", "html", "svg"]
Show = Literal["all", "err", "errskip"]


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


def all_versions(ctx: click.Context, _param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return

    groups = ["repo_review.checks", "repo_review.families", "repo_review.fixtures"]
    packages = {
        dist.name: dist.version
        for group in groups
        for ep in importlib.metadata.entry_points(group=group)
        if (dist := ep.dist) is not None
    }
    deps = ["rich", "rich-click", "click", "markdown-it-py", "pyyaml"]
    rich.print("Repo-review's dependencies:")
    for name in deps:
        rich.print(
            f"  [bold]{name}[/bold]: [magenta]{importlib.metadata.version(name)}[/magenta]"
        )
    rich.print("Packages providing repo-review plugins:")
    for name, version in sorted(packages.items()):
        rich.print(f"  [bold]{name}[/bold]: [green]{version}[/green]")
    ctx.exit()


@functools.cache
def _ensure_unicode_streams() -> None:
    # Before Python 3.15, this isn't always unicode
    if (
        sys.version_info < (3, 15)
        and "PYTHONIOENCODING" not in os.environ
        and "PYTHONUTF8" not in os.environ
    ):
        if sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
        if sys.stderr.encoding != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore[union-attr]


def rich_printer(
    families: Mapping[str, Family],
    processed: list[Result],
    *,
    svg: bool = False,
    stderr: bool = False,
    color: bool = True,
    status: Status,
    header: str = "",
) -> None:
    _ensure_unicode_streams()

    console = rich.console.Console(
        record=svg, quiet=svg, stderr=stderr, color_system="auto" if color else None
    )

    if header:
        console.print(rich.markdown.Markdown(f"# {header}"))

    for family in families:
        family_name = get_family_name(families, family)
        family_description = get_family_description(families, family)
        family_results = [r for r in processed if r.family == family]

        # Compute the family name and optional description
        rich_family_name = rich.text.Text.from_markup(f"[bold]{family_name}[/bold]:")
        if family_description:
            rich_description = rich.markdown.Markdown(
                family_description, code_theme=CODE_THEME
            )
            rich_family = rich.console.Group(
                rich_family_name, rich_description, rich.console.NewLine()
            )
            tree = rich.tree.Tree(rich_family)
        else:
            tree = rich.tree.Tree(rich_family_name)

        for result in family_results:
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
                if result.skip_reason:
                    sr_style = "yellow"
                    msg.append(" (", style=sr_style)
                    msg.append(
                        rich.text.Text.from_markup(result.skip_reason, style=sr_style)
                    )
                    msg.append(")", style=sr_style)
                tree.add(msg)
            elif result.result:
                msg.append(rich.text.Text.from_markup(" :white_check_mark:"))
                tree.add(msg)
            else:
                msg.append(rich.text.Text.from_markup(" :x:"))
                detail = rich.markdown.Markdown(result.err_msg, code_theme=CODE_THEME)
                msg_grp = rich.console.Group(msg, detail)
                tree.add(msg_grp)

        if family_results or family_description:
            console.print(tree)
            console.print()

    if header:
        console.print()

    if len(processed) == 0:
        if status == "empty":
            console.print("[bold red]No checks ran")
        elif status == "passed":
            console.print("[bold green]All checks passed")
        elif status == "skips":
            console.print("[bold green]All checks passed [yellow](with some skips)")

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
    format_opt: Formats,
    stderr: bool,
    color: bool,
    status: Status,
    header: str,
) -> None:
    output = sys.stderr if stderr else sys.stdout
    match format_opt:
        case "rich" | "svg":
            rich_printer(
                families,
                processed,
                svg=format_opt == "svg",
                stderr=stderr,
                color=color,
                status=status,
                header=header,
            )
        case "json":
            d: dict[str, Any] = {
                "status": status,
                "families": families,
                "checks": as_simple_dict(processed),
            }
            if header:
                print(json.dumps({header: d}, indent=2)[2:-2], end="", file=output)
            else:
                print(json.dumps(d, indent=2), file=output)

        case "html":
            html = to_html(families, processed, status)
            if header:
                failures = sum(r.result is False for r in processed)
                status_msg = f"({failures} failed)" if failures else "(all passed)"
                html = f"<details><summary><h2>{header}</h2>: {status_msg}</summary>\n{html}</details>\n"
            print(html, file=output)
        case _:
            assert_never(format_opt)


def remote_path_support(
    _ctx: click.Context, _param: str, value: Sequence[Path]
) -> list[Path | GHPath]:
    return [_remote_path_processor(package) for package in value]


def _remote_path_processor(package: Path) -> Path | GHPath:
    if not str(package).startswith("gh:"):
        return package

    _, org_repo_branch, *p = str(package).split(":", maxsplit=2)
    if "@" not in org_repo_branch:
        msg = "online repo must be of the form 'gh:org/repo@branch[:path]' (:branch missing)"
        raise click.BadParameter(msg)
    org_repo, branch = org_repo_branch.split("@", maxsplit=1)
    try:
        return GHPath(repo=org_repo, branch=branch, path=p[0] if p else "")
    except urllib.error.HTTPError as e:
        rich.print(f"[red][bold]Error[/bold] accessing {e.url}", file=sys.stderr)
        rich.print(f"[red]{e}", file=sys.stderr)
        raise SystemExit(1) from None


class UnicodeHelpCommand(click.Command):
    def get_help(self, ctx: click.Context) -> str:
        _ensure_unicode_streams()
        return super().get_help(ctx)


@click.command(
    cls=UnicodeHelpCommand, context_settings={"help_option_names": ["-h", "--help"]}
)
@click.version_option(version=__version__)
@click.argument(
    "packages",
    type=click.Path(dir_okay=True, path_type=Path),
    nargs=-1,
    required=False,
    callback=remote_path_support,
)
@click.option(
    "--versions",
    is_flag=True,
    callback=all_versions,
    expose_value=False,
    is_eager=True,
    help="List all plugin versions and exit",
)
@click.option(
    "--list-all",
    is_flag=True,
    callback=list_all,
    expose_value=False,
    is_eager=True,
    help="List all checks and exit",
)
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
    "--show",
    type=click.Choice(["all", "err", "errskip"]),
    default="all",
    help="Show all (default), or just errors, or errors and skips",
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
    "--extend-select",
    help="Checks to run in addition to the ones selected.",
    default="",
)
@click.option(
    "--extend-ignore",
    help="Checks to ignore in addition to the ones ignored.",
    default="",
)
@click.option(
    "--package-dir",
    "-p",
    help="Path to python package.",
    default="",
)
def main(
    packages: list[Path | GHPath],
    format_opt: Formats,
    stderr_fmt: Formats | None,
    select: str,
    ignore: str,
    extend_select: str,
    extend_ignore: str,
    package_dir: str,
    show: Show,
) -> None:
    """
    Pass in a local Path or gh:org/repo@branch. Will run on the current
    directory if no path passed.
    """
    if not packages:
        packages = [Path()]

    if len(packages) > 1:
        if format_opt == "json":
            print("{")
        if stderr_fmt == "json":
            print("{", file=sys.stderr)

    result = 0
    for n, package in enumerate(packages):
        result |= on_each(
            package,
            format_opt,
            stderr_fmt,
            select,
            ignore,
            extend_select,
            extend_ignore,
            package_dir,
            add_header=len(packages) > 1,
            show=show,
        )
        if len(packages) > 1:
            is_before_end = n < len(packages) - 1
            if format_opt == "json":
                print("," if is_before_end else "")
            if stderr_fmt == "json":
                print("," if is_before_end else "", file=sys.stderr)

    if len(packages) > 1:
        if format_opt == "json":
            print("}")
        if stderr_fmt == "json":
            print("}", file=sys.stderr)

    if result:
        raise SystemExit(result)


def on_each(
    package: Path | GHPath,
    format_opt: Literal["rich", "json", "html", "svg"],
    stderr_fmt: Literal["rich", "json", "html", "svg"] | None,
    select: str,
    ignore: str,
    extend_select: str,
    extend_ignore: str,
    package_dir: str,
    *,
    add_header: bool,
    show: Show,
) -> int:
    base_package: Traversable

    ignore_list = {x.strip() for x in ignore.split(",") if x}
    select_list = {x.strip() for x in select.split(",") if x}
    extend_ignore_list = {x.strip() for x in extend_ignore.split(",") if x}
    extend_select_list = {x.strip() for x in extend_select.split(",") if x}

    collected = collect_all(package, subdir=package_dir)
    if len(collected.checks) == 0:
        msg = "No checks registered. Please install a repo-review plugin."
        raise click.ClickException(msg)

    if isinstance(package, GHPath):
        if format_opt == "rich":
            rich.print(f"[bold]Processing [blue]{package}[/blue] from GitHub\n")
        base_package = package
        header = package.repo
    elif package.name == "pyproject.toml" and package.is_file():
        # Special case for passing a path to a pyproject.toml
        base_package = package.parent
        header = package.parent.name
    else:
        base_package = package
        header = package.name

    families, processed = process(
        base_package,
        select=select_list,
        ignore=ignore_list,
        extend_select=extend_select_list,
        extend_ignore=extend_ignore_list,
        subdir=package_dir,
    )

    status: Status = "passed" if processed else "empty"
    for result in processed:
        if result.result is False:
            status = "errors"
            break
        if result.result is None:
            status = "skips"

    if show != "all":
        processed = [r for r in processed if not r.result]
        if show == "err":
            processed = [r for r in processed if r.result is not None]
        known_families = {r.family for r in processed}
        families = {
            k: v
            for k, v in families.items()
            if k in known_families or v.get("description", "")
        }

    display_output(
        families,
        processed,
        format_opt=format_opt,
        stderr=False,
        color=stderr_fmt is None,
        status=status,
        header=header if add_header else "",
    )
    if stderr_fmt:
        display_output(
            families,
            processed,
            format_opt=stderr_fmt,
            stderr=True,
            color=True,
            status=status,
            header=header if add_header else "",
        )

    if status == "errors":
        return 3
    if status == "empty":
        return 2
    return 0


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
