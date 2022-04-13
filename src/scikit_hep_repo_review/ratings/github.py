# GH: GitHub Actions
## GH1xx: Normal actions

from __future__ import annotations

import functools
from importlib.abc import Traversable
from pathlib import Path
from typing import Any

import yaml


@functools.cache
def workflows(package: Traversable) -> dict[str, Any]:
    workflows_base_path = package.joinpath(".github/workflows")
    workflows_dict: dict[str, Any] = {}
    if workflows_base_path.is_dir():
        for workflow_path in workflows_base_path.iterdir():
            if workflow_path.name.endswith(".yml"):
                with workflow_path.open("rb") as f:
                    workflows_dict[Path(workflow_path.name).stem] = yaml.safe_load(f)

    return workflows_dict


@functools.cache
def dependabot(package: Traversable) -> dict[str, Any]:
    dependabot_path = package.joinpath(".github/dependabot.yml")
    if dependabot_path.is_file():
        with dependabot_path.open("rb") as f:
            result: dict[str, Any] = yaml.safe_load(f)
            return result

    return {}


class GitHub:
    family = "github"


class GH100(GitHub):
    "Has GitHub Actions config"

    @staticmethod
    def check(workflows: dict[str, Any]) -> bool:
        """
        All projects should have GitHub Actions config for this series of checks.
        """
        return bool(workflows)


class GH101(GitHub):
    "Has nice names"
    requires = {"GH100"}

    @staticmethod
    def check(workflows: dict[str, Any]) -> bool:
        """
        All workflows should have a nice readable `name:` field.
        """
        return all("name" in w for w in workflows)


class GH102(GitHub):
    "Auto-cancel on repeated PRs"
    requires = {"GH100"}

    @staticmethod
    def check(workflows: dict[str, Any]) -> bool:
        """
        At least one workflow should auto-cancel.

        ```yaml
        concurrency:
          group: tests-${{ github.head_ref }}
          cancel-in-progress: true
        ```
        """
        return any("concurrency" in w for w in workflows.values())


class GH103(GitHub):
    "At least one workflow has manual dispatch"
    requires = {"GH100"}

    @staticmethod
    def check(workflows: dict[str, Any]) -> bool:
        "One workflow at least should have a workflow_displatch trigger"
        return any("workflow_dispatch" in w.get(True, {}) for w in workflows.values())


class GH200(GitHub):
    "Maintained by Dependabot"

    @staticmethod
    def check(dependabot: dict[str, Any]) -> bool:
        """
        All projects should have a `.github/dependabot.yml` file to support at least
        GitHub Actions updates.

        ```yaml
        version: 2
        updates:
        # Maintain dependencies for GitHub Actions
          - package-ecosystem: "github-actions"
            directory: "/"
            schedule:
            interval: "weekly"
            ignore:
              - dependency-name: "actions/*"
                update-types: ["version-update:semver-minor", "version-update:semver-patch"]
        ```
        """
        return bool(dependabot)


class GH210(GitHub):
    "Has dependabot ecosystem"

    @staticmethod
    def check(dependabot: dict[str, Any]) -> bool:
        """
        All projects should maintain the GH Actions with dependabot.

        ```yaml
        version: 2
        updates:
        # Maintain dependencies for GitHub Actions
          - package-ecosystem: "github-actions"
            directory: "/"
            schedule:
            interval: "weekly"
            ignore:
              - dependency-name: "actions/*"
                update-types: ["version-update:semver-minor", "version-update:semver-patch"]
        ```
        """
        for ecosystem in dependabot.get("updates", []):
            if ecosystem.get("package-ecosystem", "") == "github-actions":
                return True
        return False


class GH211(GitHub):
    "Core actions should be pinned as major versions"

    requires = {"GH210"}

    @staticmethod
    def check(dependabot: dict[str, Any]) -> bool:
        """
        Projects should only pin to major versions for official actions.

        ```yaml
        ignore:
          - dependency-name: "actions/*"
            update-types: ["version-update:semver-minor", "version-update:semver-patch"]
        ```
        """
        for ecosystem in dependabot.get("updates", []):
            if ecosystem.get("package-ecosystem", "") == "github-actions":
                for ignore in ecosystem.get("ignore", []):
                    if "actions/*" in ignore.get("dependency-name", ""):
                        return set(ignore.get("update-types", [])) == {
                            "version-update:semver-minor",
                            "version-update:semver-patch",
                        }
        return False


repo_review_fixtures = {"workflows", "dependabot"}
repo_review_checks = {p.__name__ for p in GitHub.__subclasses__()}
