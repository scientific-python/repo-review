from __future__ import annotations

__lazy_modules__ = [
    "argparse",
    "importlib",
    "importlib.metadata",
    "itertools",
    "json",
    "os",
    "pathlib",
    "repo_review._compat",
    "repo_review._compat.typing",
    "repo_review.checks",
    "repo_review.families",
    "repo_review.ghpath",
    "repo_review.html",
    "repo_review.processor",
    "rich",
    "rich.console",
    "rich.markdown",
    "rich.syntax",
    "rich.terminal_theme",
    "rich.text",
    "rich.tree",
    "sys",
    "urllib",
    "urllib.error",
]

import argparse
import asyncio
import functools
import importlib.metadata
import importlib.util
import itertools
import json
import logging
import os
import sys
import urllib.error
from pathlib import Path
from typing import Any, Literal

import rich
import rich.console
import rich.markdown
import rich.syntax
import rich.terminal_theme
import rich.text
import rich.tree
from rich.logging import RichHandler

from repo_review import __version__
from repo_review._compat.typing import assert_never
from repo_review.checks import get_check_description, get_check_url
from repo_review.families import Family, get_family_description, get_family_name
from repo_review.files import collect_prefetch_files, process_prefetch_files
from repo_review.ghpath import GHPath
from repo_review.html import to_html
from repo_review.processor import (
    Result,
    as_simple_dict,
    collect_all,
    process,
)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Mapping

    from ._compat.importlib.resources.abc import Traversable

__all__ = ["Formats", "Show", "Status", "main"]

CODE_THEME = "ansi_light"


def __dir__() -> list[str]:
    return __all__


Status = Literal["empty", "passed", "skips", "errors"]
Formats = Literal["rich", "json", "html", "svg"]
Show = Literal["all", "err", "errskip"]


def _list_all() -> None:
    collected = collect_all()
    if len(collected.checks) == 0:
        msg = "No checks registered. Please install a repo-review plugin."
        print(f"Error: {msg}", file=sys.stderr)
        raise SystemExit(1)

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


def _all_versions() -> None:
    groups = ["repo_review.checks", "repo_review.families", "repo_review.fixtures"]
    packages = {
        dist.name: dist.version
        for group in groups
        for ep in importlib.metadata.entry_points(group=group)
        if (dist := ep.dist) is not None
    }
    deps = ["rich", "markdown-it-py", "pyyaml"]
    rich.print("Repo-review's dependencies:")
    for name in deps:
        rich.print(
            f"  [bold]{name}[/bold]: [magenta]{importlib.metadata.version(name)}[/magenta]"
        )
    rich.print("Packages providing repo-review plugins:")
    for name, version in sorted(packages.items()):
        rich.print(f"  [bold]{name}[/bold]: [green]{version}[/green]")


@functools.cache
def _ensure_unicode_streams() -> None:
    # Before Python 3.15, this isn't always unicode
    if (
        sys.version_info < (3, 15)
        and "PYTHONIOENCODING" not in os.environ
        and "PYTHONUTF8" not in os.environ
    ):
        if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure") and sys.stderr.encoding != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")


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
        string = console.export_svg(theme=rich.terminal_theme.DEFAULT_TERMINAL_THEME)
        if color:
            rich.print(
                rich.syntax.Syntax(string, lexer="xml"),
                file=sys.stderr if stderr else sys.stdout,
            )
        else:
            print(string, file=sys.stderr if stderr else sys.stdout)


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


def _remote_path_processor(package: Path) -> Path | GHPath:
    if not str(package).startswith("gh:"):
        return package

    _, org_repo_branch, *p = str(package).split(":", maxsplit=2)
    if "@" in org_repo_branch:
        org_repo, branch = org_repo_branch.split("@", maxsplit=1)
    else:
        org_repo = org_repo_branch
        branch = "HEAD"
    try:
        return GHPath(repo=org_repo, branch=branch, path=p[0] if p else "")
    except urllib.error.HTTPError as e:
        rich.print(f"[red][bold]Error[/bold] accessing {e.url}", file=sys.stderr)
        rich.print(f"[red]{e}", file=sys.stderr)
        raise SystemExit(1) from None


def main(args: list[str] | None = None) -> None:
    """
    Pass in a local Path or gh:org/repo[@branch][:path]. Will run on the current
    directory if no path passed.
    """
    _ensure_unicode_streams()

    parser = argparse.ArgumentParser(
        prog="repo-review",
        description="Pass in a local Path or gh:org/repo[@branch][:path]. Will run on the current directory if no path passed.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--versions",
        action="store_true",
        help="List all plugin versions and exit",
    )
    parser.add_argument(
        "--log-level",
        help="Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).",
        metavar="LEVEL",
    )
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all checks and exit",
    )
    parser.add_argument(
        "packages",
        type=Path,
        nargs="*",
        help="Local path or gh:org/repo[@branch][:path]",
    )
    parser.add_argument(
        "--format",
        dest="format_opt",
        choices=["rich", "json", "html", "svg"],
        default="rich",
        help="Select output format.",
    )
    parser.add_argument(
        "--stderr",
        dest="stderr_fmt",
        choices=["rich", "json", "html", "svg"],
        help="Select additional output format for stderr. Will disable terminal escape codes for stdout for easy redirection.",
    )
    parser.add_argument(
        "--show",
        choices=["all", "err", "errskip"],
        default="all",
        help="Show all (default), or just errors, or errors and skips",
    )
    parser.add_argument(
        "--select",
        default="",
        help="Only run certain checks, comma separated. All checks run if empty.",
    )
    parser.add_argument(
        "--ignore",
        default="",
        help="Ignore a check or checks, comma separated.",
    )
    parser.add_argument(
        "--extend-select",
        default="",
        help="Checks to run in addition to the ones selected.",
    )
    parser.add_argument(
        "--extend-ignore",
        default="",
        help="Checks to ignore in addition to the ones ignored.",
    )
    parser.add_argument(
        "--package-dir",
        "-p",
        default="",
        help="Path to python package.",
    )

    parsed = parser.parse_args(args)

    # Configure logging (Rich handler) for only our package if requested
    lvl = parsed.log_level or os.getenv("REPO_REVIEW_LOG_LEVEL")
    if lvl:
        level = getattr(logging, lvl.upper(), logging.INFO)
        handler = RichHandler()
        # Configure only the `repo_review` logger to avoid enabling global logging
        repo_logger = logging.getLogger("repo_review")
        repo_logger.setLevel(level)
        repo_logger.addHandler(handler)
        repo_logger.propagate = False

    if parsed.versions:
        _all_versions()
        return

    if parsed.list_all:
        _list_all()
        return

    packages: list[Path | GHPath] = [_remote_path_processor(p) for p in parsed.packages]

    if not packages:
        packages = [Path()]

    format_opt: Formats = parsed.format_opt
    stderr_fmt: Formats | None = parsed.stderr_fmt

    if len(packages) > 1:
        if format_opt == "json":
            print("{")
        if stderr_fmt == "json":
            print("{", file=sys.stderr)

    supports_async = importlib.util.find_spec("httpx") is not None
    result = 0
    for n, package in enumerate(packages):
        if supports_async and isinstance(package, GHPath):
            prefetch_files = collect_prefetch_files()
            asyncio.run(
                process_prefetch_files(
                    package, prefetch_files, subdir=parsed.package_dir
                )
            )

        result |= on_each(
            package,
            format_opt,
            stderr_fmt,
            parsed.select,
            parsed.ignore,
            parsed.extend_select,
            parsed.extend_ignore,
            parsed.package_dir,
            add_header=len(packages) > 1,
            show=parsed.show,
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

    # Local paths support pointing at pyproject.toml as a special case
    match package:
        case GHPath(repo=header) as base_package:
            if format_opt == "rich":
                rich.print(f"[bold]Processing [blue]{package}[/blue] from GitHub\n")
        case object(parent=base_package, name="pyproject.toml") if package.is_file():
            # Special case for passing a path to a pyproject.toml
            header = base_package.name
        case base_package:
            header = getattr(package, "name", str(package))

    collected = collect_all(base_package, subdir=package_dir)
    if len(collected.checks) == 0:
        msg = "No checks registered. Please install a repo-review plugin."
        print(f"Error: {msg}", file=sys.stderr)
        raise SystemExit(1)

    families, processed = process(
        base_package,
        select=select_list,
        ignore=ignore_list,
        extend_select=extend_select_list,
        extend_ignore=extend_ignore_list,
        subdir=package_dir,
        collected=collected,
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
