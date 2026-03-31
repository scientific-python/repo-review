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
    from .ghpath import GHPath

__all__ = [
    "collect_prefetch_files",
    "prefetch_files",
    "process_prefetch_files",
]


def __dir__() -> list[str]:
    return __all__


def prefetch_files() -> set[str]:
    """
    This entry-point lists files that should be prefetched. This is a suggestion
    for async loading.
    """

    # Temporary way to test async loading
    if "REPO_REVIEW_PREFETCH_SP_DEBUG" in os.environ:
        return {
            "pyproject.toml",
            "setup.cfg",
            ".github/dependabot.yml",
            ".github/workflows/*.yml",
            "noxfile.py",
            ".pre-commit-config.yaml",
            ".readthedocs.yml",
        }

    return {"pyproject.toml"}


def collect_prefetch_files() -> set[str]:
    """
    Produces a set of files that should be prefetched.

    :return: A set of relative file paths.
    """
    return {
        val
        for ep in importlib.metadata.entry_points(group="repo_review.prefetch_files")
        for val in ep.load()()
    }


async def process_prefetch_files(start: GHPath, /, files: set[str]) -> None:
    """
    Process pre-fetch files. This runs in parallel with async loading.
    """
    if sys.version_info >= (3, 11):
        with log_timer(logger, "Prefetching files for %s", start):
            async with asyncio.TaskGroup() as tg:
                for f in files:
                    for p in start.glob(f):
                        tg.create_task(p.prefetch())
