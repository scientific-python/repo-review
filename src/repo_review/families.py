from __future__ import annotations

import importlib.metadata
import typing
from collections.abc import Mapping

__all__ = ["Family", "collect_families", "get_family_name"]


def __dir__() -> list[str]:
    return __all__


class Family(typing.TypedDict, total=False):
    """
    A typed Dict that is used to customize the display of families in reports.
    """

    #: Optional nice name to display instead of family key. Treated like family
    #: key if missing.
    name: str

    #: Checks are first sorted by this integer order, then alphabetically by
    #: family key. Treated like 0 if missing.
    order: int


def collect_families() -> dict[str, Family]:
    """
    Produces a dict mapping family keys to :class:`Family` dicts based on installed
    entry points. Unlike other similar functions, this one currently does not
    expect a dict of fixtures; dynamic listing is not usually needed for
    :class:`Family`'s.
    """
    return {
        name: family
        for ep in importlib.metadata.entry_points(group="repo_review.families")
        for name, family in ep.load()().items()
    }


def get_family_name(families: Mapping[str, Family], family: str) -> str:
    """
    Returns the "nice" family name if there is one, otherwise the (input)
    family short name.

    :param families: A dict of family short names to :class:`.Family`'s.
    :param family: The short name of a family.
    :return: The nice family name if there is one, otherwise the short name is returned.

    .. versionadded:: 0.8
    """
    return families.get(family, {}).get("name", family)
