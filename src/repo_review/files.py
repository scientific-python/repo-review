from __future__ import annotations

import asyncio
import importlib.metadata
import logging
import os
import sys

from ._timer import log_timer

logger = logging.getLogger(__name__)

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Set as AbstractSet

    from .ghpath import GHPath

__all__ = [
    "collect_prefetch_files",
    "prefetch_package",
    "prefetch_root",
    "process_prefetch_files",
]


def __dir__() -> list[str]:
    return __all__


def prefetch_root() -> set[str]:
    """
    This entry-point lists files that should be prefetched. This is a suggestion
    for async loading.
    """

    # Temporary way to test async loading
    if "REPO_REVIEW_PREFETCH_SP_DEBUG" in os.environ:
        return {
            "pyproject.toml",
            "setup.cfg",
        }

    return {"pyproject.toml"}


def prefetch_package() -> set[str]:
    """
    This entry-point lists files that should be prefetched. This is a suggestion
    for async loading.
    """

    # Temporary way to test async loading
    if "REPO_REVIEW_PREFETCH_SP_DEBUG" in os.environ:
        return {
            ".github/dependabot.yml",
            ".github/dependabot.yaml",
            ".github/workflows/*.yml",
            ".github/workflows/*.yaml",
            ".pre-commit-config.yaml",
            ".readthedocs.yml",
            "noxfile.py",
            "ruff.toml",
            ".ruff.toml",
        }

    return set()


def collect_prefetch_files() -> dict[str, set[str]]:
    """
    Produces a mapping with keys ``"root"`` and/or ``"package"`` to sets of
    files that should be prefetched.

    Entry-points whose name is ``"package"`` are collected under the
    ``"package"`` key (resolved relative to the package directory). All other
    entry-points (name ``"root"`` or empty) are collected under ``"root"``
    (resolved relative to the repository root).

    :return: A mapping with keys ``"root"`` and/or ``"package"``.
    """
    result: dict[str, set[str]] = {}
    for ep in importlib.metadata.entry_points(group="repo_review.prefetch_files"):
        vals = ep.load()()
        key = ep.name
        if key in {"root", "package"}:
            result.setdefault(key, set()).update(vals)
        else:
            logger.warning(
                "Only 'root' and 'package' supported for repo_review.prefetch_files, got %r",
                key,
            )
    return result


async def process_prefetch_files(
    start: GHPath, /, files: Mapping[str, AbstractSet[str]], *, subdir: str = ""
) -> None:
    """
    Process pre-fetch files. This runs in parallel with async loading.

    ``files`` is a mapping with keys ``"root"`` and/or ``"package"``.
    Patterns under ``"root"`` are resolved relative to the repository root
    (``start``); patterns under ``"package"`` are resolved relative to the
    package directory (``start / subdir``, or ``start`` when *subdir* is
    empty).
    """
    if sys.version_info >= (3, 11):
        with log_timer(logger, "Prefetching files for %s", start):
            async with asyncio.TaskGroup() as tg:
                for key, patterns in files.items():
                    base = (
                        start.joinpath(subdir) if key == "package" and subdir else start
                    )
                    for f in patterns:
                        for p in base.glob(f):
                            tg.create_task(p.prefetch())
