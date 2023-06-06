from __future__ import annotations

import builtins
import functools
import io
import itertools
import json
import typing
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

if typing.TYPE_CHECKING:
    import click
else:
    import rich_click as click

import markdown_it
import rich.console
import rich.markdown
import rich.terminal_theme
import rich.text
import rich.traceback
import rich.tree

from ._compat.importlib.resources.abc import Traversable
from .families import Family
from .ghpath import GHPath
from .processor import Result, _collect_all, as_simple_dict, process

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)

# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())


def rich_printer(
    families: Mapping[str, Family], processed: list[Result], *, output: Path | None
) -> None:
    console = rich.console.Console(record=True)

    for family, results_list in itertools.groupby(processed, lambda r: r.family):
        family_name = families[family].get("name", family)
        tree = rich.tree.Tree(f"[bold]{family_name}[/bold]:")
        for result in results_list:
            color = (
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
            msg.append(rich.text.Text.from_markup(description, style=color))
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

    if output is not None:
        console.save_svg(str(output), theme=rich.terminal_theme.DEFAULT_TERMINAL_THEME)


def to_html(families: Mapping[str, Family], processed: list[Result]) -> str:
    out = io.StringIO()
    print = functools.partial(builtins.print, file=out)
    md = markdown_it.MarkdownIt()

    for family, results_list in itertools.groupby(processed, lambda r: r.family):
        family_name = families[family].get("name", family)
        print(f"<h2>{family_name}</h2>")
        print("<table>")
        print("<tr><th>?</th><th>Name</th><th>Description</th></tr>")
        for result in results_list:
            color = (
                "orange"
                if result.result is None
                else "green"
                if result.result
                else "red"
            )
            icon = "⚠️" if result.result is None else "✅" if result.result else "❌"
            result_txt = (
                "Skipped"
                if result.result is None
                else "Passed"
                if result.result
                else "Failed"
            )
            description = (
                f'<a href="{result.url}">{result.description}</a>'
                if result.url
                else result.description
            )
            print(f'<tr style="color: {color};">')
            print(f'<td><span role="img" aria-label="{result_txt}">{icon}</span></td>')
            print(f"<td>{result.name}</td>")
            if result.result is None or result.result:
                print(f"<td>{description}</td>")
            else:
                print("<td>")
                print(description)
                print("<br/>")
                print(md.render(result.err_msg))
                print("</td>")
            print("</tr>")
        print("</table>")

    if len(processed) == 0:
        print('<span style="color: red;">No checks ran.</span>')

    return out.getvalue()


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(file_okay=True, exists=False, path_type=Path),
    default=None,
    help="Write out file. Writes SVG if format is rich.",
)
@click.option(
    "--format",
    "format_opt",
    type=click.Choice(["rich", "json", "html"]),
    default="rich",
    help="Select output format.",
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
    "--list/--no-list",
    "list_opt",
    help="List all checks and exit",
    default=False,
)
def main(
    package: Traversable,
    output: Path | None,
    format_opt: Literal["rich", "json", "html"],
    select: str,
    ignore: str,
    package_dir: str,
    list_opt: bool,
) -> None:
    """
    Pass in a local Path or gh:org/repo@branch.
    """
    ignore_list = {x.strip() for x in ignore.split(",") if x}
    select_list = {x.strip() for x in select.split(",") if x}

    _, checks, families = _collect_all(package, subdir=package_dir)
    if len(checks) == 0:
        msg = "No checks registered. Please install a repo-review plugin."
        raise click.ClickException(msg)

    if list_opt:
        for family, grp in itertools.groupby(checks.items(), key=lambda x: x[1].family):
            rich.print(f'  [dim]# {families[family].get("name", family)}')
            for code, check in grp:
                rich.print(f'  "{code}",  [dim]# {check.__doc__}')

        raise SystemExit(0)

    if str(package).startswith("gh:"):
        _, org_repo_branch, *p = str(package).split(":", maxsplit=2)
        org_repo, branch = org_repo_branch.split("@", maxsplit=1)
        package = GHPath(repo=org_repo, branch=branch, path=p[0] if p else "")
        if format_opt == "rich":
            rich.print(f"[bold]Processing [blue]{package}[/blue] from GitHub\n")

    families, processed = process(
        package, select=select_list, ignore=ignore_list, subdir=package_dir
    )

    if format_opt == "rich":
        rich_printer(families, processed, output=output)
        if len(processed) == 0:
            rich.print("[bold red]No checks ran[/bold red]")
    elif format_opt == "json":
        j = json.dumps(
            {"families": families, "checks": as_simple_dict(processed)}, indent=2
        )
        if output:
            output.write_text(j)
        else:
            rich.print_json(j)
    elif format_opt == "html":
        html = to_html(families, processed)
        if output:
            output.write_text(html)
        else:
            rich.print(html)

    if any(p.result is False for p in processed):
        raise SystemExit(2)
    if len(processed) == 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
