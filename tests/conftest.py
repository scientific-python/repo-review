import importlib.metadata

import pytest


@pytest.fixture(autouse=True)
def nocolor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NOCOLOR", raising=False)
    monkeypatch.delenv("FORCE_COLOR", raising=False)


@pytest.fixture()
def no_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        importlib.metadata,
        "entry_points",
        lambda group: [],  # noqa: ARG005
    )


@pytest.fixture()
def local_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    orig_ep = importlib.metadata.entry_points
    ep1 = importlib.metadata.EntryPoint(
        name="pyproject",
        group="repo_review.checks",
        value="pyproject:repo_review_checks",
    )
    ep2 = importlib.metadata.EntryPoint(
        name="pyproject",
        group="repo_review.families",
        value="pyproject:repo_review_families",
    )

    def new_ep(*, group: str) -> list[importlib.metadata.EntryPoint]:
        if group == "repo_review.checks":
            return [ep1]
        if group == "repo_review.families":
            return [ep2]
        if group == "repo_review.fixtures":
            return [
                e for e in orig_ep(group=group) if e.module.startswith("repo_review.")
            ]
        return orig_ep(group=group)

    monkeypatch.setattr(importlib.metadata, "entry_points", new_ep)
