# PC: Pre-commit
## PC0xx: pre-commit-hooks

from __future__ import annotations

from typing import Any


class PreCommit:
    pass


class PC101(PreCommit):
    "Has pre-commit-hooks"

    @staticmethod
    def check(precommit: dict[str, Any]) -> bool:
        "Must have pre-commit hooks repo"
        for repo in precommit["repos"]:
            match repo:
                case {"repo": "https://github.com/pre-commit/pre-commit-hooks"}:
                    return True
        return False
