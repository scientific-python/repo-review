from __future__ import annotations

import builtins
import functools
import io
import itertools
from collections.abc import Mapping

import markdown_it

from .families import Family
from .processor import Result

__all__ = ["to_html"]


def __dir__() -> list[str]:
    return __all__


def to_html(families: Mapping[str, Family], processed: list[Result]) -> str:
    """
    Convert the results of a repo review to HTML.
    """
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
