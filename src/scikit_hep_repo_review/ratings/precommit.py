# PC: Pre-commit
## PC0xx: pre-commit-hooks

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import yaml


@functools.cache
def precommit(package: Path) -> dict[str, Any]:
    precommit_path = package.joinpath(".pre-commit-config.yaml")
    precommit: dict[str, Any]
    if precommit_path.exists():
        with precommit_path.open("rb") as f:
            return yaml.safe_load(f)  # type: ignore[no-any-return]

    return {}


class PreCommit:
    family = "pre-commit"
    requires = {"PY006"}

    @classmethod
    def check(cls, precommit: dict[str, Any]) -> bool:
        "Must have {cls.repo} repo in pre-commit config"
        for repo in precommit["repos"]:
            if "repo" in repo and repo["repo"].lower() == cls.repo:  # type: ignore[attr-defined]
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
    repo = "https://github.com/pycqa/isort"


class PC130(PreCommit):
    "Uses flake8"
    repo = "https://github.com/pycqa/flake8"


class PC131(PreCommit):
    "Adds flake8-bugbear"
    requires = {"PC130"}

    @staticmethod
    def check(precommit: dict[str, Any]) -> bool:
        "Must have flake8-bugbear in additional_dependencies"
        for repo in precommit["repos"]:
            if (
                "repo" in repo
                and repo["repo"].lower() == "https://github.com/pycqa/flake8"
            ):
                for hook in repo["hooks"]:
                    match hook:
                        case {"additional_dependencies": list(x)}:
                            return "flake8-bugbear" in x
        return False


class PC140(PreCommit):
    "Uses mypy"
    repo = "https://github.com/pre-commit/mirrors-mypy"


class PC150(PreCommit):
    "Uses PyUpgrade"
    repo = "https://github.com/asottile/pyupgrade"


class PC160(PreCommit):
    "Uses codespell"
    repo = "https://github.com/codespell-project/codespell"


class PC170(PreCommit):
    "Uses PyGrep hooks"
    repo = "https://github.com/pre-commit/pygrep-hooks"


class PC901(PreCommit):
    "Custom pre-commit CI message"
    
    def check(precommit: dict[str, Any]) -> bool:
        "Should have [bold]ci: autoupdate_commit_msg: 'chore: update pre-commit hooks'[/bold] or similar in pre-commit config"

        return "autoupdate_commit_msg" in precommit.get("ci", {})

repo_review_fixtures = {"precommit"}
repo_review_checks = {p.__name__ for p in PreCommit.__subclasses__()}
