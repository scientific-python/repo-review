from pathlib import Path

import pytest

import repo_review.processor
from repo_review._compat.importlib.resources.abc import Traversable


class E100:
    "Was passed correctly"

    family = "example"

    @staticmethod
    def check(package: Traversable) -> bool:
        """
        Requires Path(".") to be passed
        """

        return package == Path()


class E200:
    "Always true"

    family = "example"
    requires = frozenset(["E100"])

    @staticmethod
    def check() -> bool:
        """
        Can't be false.
        """

        return True


def test_ignore_filter_single(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"E100": E100, "E200": E200},
    )
    _, results = repo_review.processor.process(Path(), ignore={"E100"})

    assert len(results) == 1
    assert results[0].name == "E200"
    assert results[0].result


def test_select_filter_single(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"E100": E100, "E200": E200},
    )
    _, results = repo_review.processor.process(Path(), select={"E200"})

    assert len(results) == 1
    assert results[0].name == "E200"
    assert results[0].result
