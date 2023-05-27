from __future__ import annotations

from pathlib import Path
import json

import click
import rich.console
import rich.markdown
import rich.terminal_theme
import rich.text
import rich.traceback
import rich.tree

from .processor import process, Result, as_simple_dict

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)

# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())


def rich_printer(processed: dict[str, dict[str, Result]], *, output: Path | None) -> None:
    console = rich.console.Console(record=True)

    for family, results_list in processed.items():
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

@click.command()
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(file_okay=True, exists=False, path_type=Path),
    default=None,
)
@click.option(
    "--format",
    type=click.Choice(["rich", "json"]),
    default="rich",
)
def main(package: Path, output: Path | None, format: str) -> None:
    processed = process(package)

    if format == "rich":
        rich_printer(processed, output=output)
    elif format == "json":
        j = json.dumps(as_simple_dict(processed), indent=2)
        if output:
            output.write_text(j)
        else:
            rich.print(j)
        


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
