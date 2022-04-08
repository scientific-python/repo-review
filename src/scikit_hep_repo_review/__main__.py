from __future__ import annotations

from pathlib import Path

import click
import rich.console
import rich.markdown
import rich.terminal_theme
import rich.text
import rich.traceback
import rich.tree

from .processor import process

rich.traceback.install(suppress=[click, rich], show_locals=True, width=None)

# Use module-level entry names
# repo_review_fixtures = {"pyproject"}
# repo_review_checks = set(p.__name___ for p in General.__subclasses__())


@click.command()
@click.argument("package", type=click.Path(dir_okay=True, path_type=Path))
@click.option(
    "--output",
    type=click.Path(file_okay=True, exists=False, path_type=Path),
    default=None,
)
def main(package: Path, output: Path | None) -> None:

    console = rich.console.Console(record=True)

    processed = process(package)
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


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
