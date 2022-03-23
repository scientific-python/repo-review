# PC: Pre-commit
## PC0xx: pre-commit-hooks

from __future__ import annotations

from typing import Any


class PreCommit:
    requires = {"PY006"}

    @classmethod
    def check(cls, precommit: dict[str, Any]) -> bool:
        "Must have {cls.repo} repo in pre-commit config"
        for repo in precommit["repos"]:
            match repo:
                case {"repo": cls.repo}:  # type: ignore[attr-defined]
                    return True
        return False


class PC100(PreCommit):
    "Has pre-commit-hooks"
    repo = "https://github.com/pre-commit/pre-commit-hooks"


class PC110(PreCommit):
    "Uses black"
    repo = "https://github.com/psf/black"


class PC120(PreCommit):
    "Uses isort"
    repo = "https://github.com/PyCQA/isort"
