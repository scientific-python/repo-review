from __future__ import annotations

import importlib.metadata
import typing
from collections.abc import Mapping
from typing import Any

from .fixtures import apply_fixtures

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

    #: An optional description that shows up under the family name.
    description: str


def collect_families(fixtures: Mapping[str, Any]) -> dict[str, Family]:
    """
    Produces a dict mapping family keys to :class:`Family` dicts based on
    installed entry points. You must provide the evaluated fixtures so that the
    family functions have access to the fixtures when they are running, usually
    used for descriptions.

    :param fixtures: Fully evaluated dict of fixtures.
    """

    family_functions = (
        ep.load()
        for ep in importlib.metadata.entry_points(group="repo_review.families")
    )

    return {
        k: v
        for func in family_functions
        for k, v in apply_fixtures(fixtures, func).items()
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


def get_family_description(families: Mapping[str, Family], family: str) -> str:
    """
    Returns the description if there is one, otherwise returns an empty string.

    :param families: A dict of family short names to :class:`.Family`'s.
    :param family: The short name of a family.
    :return: The de-intended description if there is one, otherwise an empty string.

    .. versionadded:: 0.9
    """
    return families.get(family, {}).get("description", "")
