from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Literal

import click
import rich.console
import rich.markdown
import rich.terminal_theme
import rich.text
import rich.traceback
import rich.tree

from .ghpath import GHPath
from .processor import Result, as_simple_dict, process

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)

# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())


def rich_printer(processed: list[Result], *, output: Path | None) -> None:
    console = rich.console.Console(record=True)

    for family, results_list in itertools.groupby(processed, lambda r: r.family):
        tree = rich.tree.Tree(f"[bold]{family}[/bold]:")
        for result in results_list:
            msg = rich.text.Text()
            msg.append(result.name, style="bold")
            msg.append(" ")
            if result.result is None:
                msg.append(result.description, style="yellow")
                msg.append(" [skipped]", style="yellow bold")
                tree.add(msg)
            elif result.result:
                msg.append(f"{result.description}? ", style="green")
                msg.append(rich.text.Text.from_markup(":white_check_mark:"))
                tree.add(msg)
            else:
                msg.append(f"{result.description}? ", style="red")
                msg.append(rich.text.Text.from_markup(":x:"))
                detail = rich.markdown.Markdown(result.err_msg)
                msg_grp = rich.console.Group(msg, detail)
                tree.add(msg_grp)

        console.print(tree)
        console.print()

    if output is not None:
        console.save_svg(str(output), theme=rich.terminal_theme.DEFAULT_TERMINAL_THEME)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "package",
    type=click.Path(dir_okay=True, path_type=Path),
)
@click.option(
    "--output",
    type=click.Path(file_okay=True, exists=False, path_type=Path),
    default=None,
    help="Write out file. Writes SVG if format is rich.",
)
@click.option(
    "--format",
    type=click.Choice(["rich", "json"]),
    default="rich",
    help="Select output format.",
)
@click.option(
    "--ignore",
    help="Ignore a check or checks, comma separated.",
    default="",
)
def main(
    package: Path, output: Path | None, format: Literal["rich", "json"], ignore: str
) -> None:
    """
    Pass in a local Path or gh:org/repo@branch[:root].
    """
    ignore_list = [x.strip() for x in ignore.split(",")]

    if str(package).startswith("gh:"):
        _, org_repo_branch, *p = str(package).split(":", maxsplit=2)
        org_repo, branch = org_repo_branch.split("@", maxsplit=1)
        ghpackage = GHPath(repo=org_repo, branch=branch, path=p[0] if p else "")
        if format == "rich":
            rich.print(f"[bold]Processing [blue]{package}[/blue] from GitHub\n")
        processed = process(ghpackage, ignore=ignore_list)
    else:
        processed = process(package, ignore=ignore_list)

    if format == "rich":
        rich_printer(processed, output=output)
    elif format == "json":
        j = json.dumps(as_simple_dict(processed), indent=2)
        if output:
            output.write_text(j)
        else:
            rich.print_json(j)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
