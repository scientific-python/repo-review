from __future__ import annotations

import builtins
import functools
import io
import typing
from collections.abc import Mapping, Sequence

from .families import Family, get_family_description, get_family_name
from .processor import Result, md_as_html

if typing.TYPE_CHECKING:
    from .__main__ import Status

__all__ = ["to_html"]


def __dir__() -> list[str]:
    return __all__


def to_html(
    families: Mapping[str, Family],
    processed: Sequence[Result],
    status: Status = "empty",
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

    for family in families:
        family_name = get_family_name(families, family)
        family_description = get_family_description(families, family)
        family_results = [r.md_as_html() for r in processed if r.family == family]
        if family_results or family_description:
            print(f"<h3>{family_name}</h3>")
        if family_description:
            print("<p>", md_as_html(family_description), "</p>")
        if family_results:
            print("<table>")
            print(
                '<tr><th>?</th><th nowrap="nowrap">Name</th><th>Description</th></tr>'
            )
        for result in family_results:
            color = (
                "orange"
                if result.result is None
                else "green"
                if result.result
                else "red"
            )
            icon = (
                ("&#128311;" if result.skip_reason else "&#9888;&#65039;")
                if result.result is None
                else "&#9989;"
                if result.result
                else "&#10060;"
            )
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
            if result.skip_reason:
                description += (
                    f'<br/><span style="color:DarkKhaki;"><b>Skipped:</b> '
                    f"<em>{result.skip_reason}</em></span>"
                )
            print(f'<tr style="color: {color};">')
            print(f'<td><span role="img" aria-label="{result_txt}">{icon}</span></td>')
            print(f'<td nowrap="nowrap">{result.name}</td>')
            if result.result is None or result.result:
                print(f"<td>{description}</td>")
            else:
                print("<td>")
                print(description)
                print("<br/>")
                print(result.err_msg)
                print("</td>")
            print("</tr>")
        if family_results:
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
