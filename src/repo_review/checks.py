from __future__ import annotations

import importlib.metadata
from collections.abc import Mapping, Set
from typing import Any, Protocol

from .fixtures import apply_fixtures

__all__ = ["Check", "collect_checks", "is_allowed", "get_check_url"]


class Check(Protocol):
    """
    This is the check Protocol. Since Python doesn't support optional Protocol
    members, the two optional members are required if you want to use this
    Protocol in a type checker. The members can be specified as class
    properties if you want.
    """

    @property
    def family(self) -> str:
        """
        The family is a string that the checks will be grouped by.
        """

    @property
    def requires(self) -> Set[str]:  # Optional
        """
        Requires is an (optional) set of checks that must pass for this check
        to run. Omitting this is like returning `set()`.
        """

    @property
    def url(self) -> str:  # Optional
        """
        This is an (optional) URL to link to for this check. An empty string is
        identical to omitting this member.
        """

    def check(self) -> bool | None | str:
        """
        This is a check. The docstring is used as the failure message if
        `False` is returned. Returning None is a skip. Returning `True` (or an
        empty string) is a pass. Can be a :func:`classmethod` or
        :func:`staticmethod`. Can take fixtures.
        """
        ...


def collect_checks(fixtures: Mapping[str, Any]) -> dict[str, Check]:
    """
    Produces a list of checks based on installed entry points. You must provide
    the evaluated fixtures so that the check functions have access to the
    fixtures when they are running.

    :param fixtures: Fully evaluated dict of fixtures.
    """
    check_functions = (
        ep.load() for ep in importlib.metadata.entry_points(group="repo_review.checks")
    )

    return {
        k: v
        for func in check_functions
        for k, v in apply_fixtures(fixtures, func).items()
    }


def is_allowed(select: Set[str], ignore: Set[str], name: str) -> bool:
    """
    Skips the check if the name is in the ignore list or if the name without the
    number is in the ignore list. If the select list is not empty, only runs the
    check if the name or name without the number is in the select list.

    :param select: A set of names or prefixes to include.
    :param ignore: A set of names or prefixes to exclude.
    :param name: The check to test.

    :return: True if this check is allowed, False otherwise.
    """
    if select and name not in select and name.rstrip("0123456789") not in select:
        return False
    if name in ignore or name.rstrip("0123456789") in ignore:
        return False
    return True


def get_check_url(name: str, check: Check) -> str:
    """
    Get the url from a check instance. Will return an empty string if missing.
    Will process string via format.

    :param name: The name of the check (letters and number)
    :param check: The check to process.
    :return: The final URL.

    .. versionadded:: 0.8
    """
    return getattr(check, "url", "").format(self=check, name=name)


def get_check_description(name: str, check: Check) -> str:
    """
    Get the doc from a check instance. Will return an empty string if missing.
    Will process string via format.

    :param name: The name of the check (letters and number)
    :param check: The check to process.
    :return: The final doc.

    .. versionadded:: 0.8
    """
    return (check.__doc__ or "").format(self=check, name=name)
