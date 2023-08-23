from __future__ import annotations

import builtins
import functools
import io
import itertools
import typing
from collections.abc import Mapping

import markdown_it

from .families import Family, get_family_description, get_family_name
from .processor import Result

if typing.TYPE_CHECKING:
    from .__main__ import Status

__all__ = ["to_html"]


def __dir__() -> list[str]:
    return __all__


def to_html(
    families: Mapping[str, Family], processed: list[Result], status: Status = "empty"
) -> str:
    """
    Convert the results of a repo review (``families``, ``processed``) to HTML.

    :param families: The family mapping.
    :param processed: The list of processed results.
    :param status: A string indicating the reason behind being empty. Will
                   assume no checks ran if not given. This is only needed if
                   you are filtering the results before calling this function.
    """
    out = io.StringIO()
    print = functools.partial(builtins.print, file=out)
    md = markdown_it.MarkdownIt()

    for family, results_list in itertools.groupby(processed, lambda r: r.family):
        family_name = get_family_name(families, family)
        print(f"<h2>{family_name}</h2>")
        if description := get_family_description(families, family):
            print(md.render(description))
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
        if status == "empty":
            print('<span style="color: red;">No checks ran.</span>')
        elif status == "passed":
            print('<span style="color: red;">All checks passed.</span>')
        elif status == "skips":
            print(
                '<span style="color: red;">All checks passed.</span> <span style="color: yellow;">(some checks skipped)</span>'
            )

    return out.getvalue()
