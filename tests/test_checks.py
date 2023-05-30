import importlib.metadata
import sys
from importlib.abc import Traversable
from pathlib import Path
from types import ModuleType

import pytest

import scikit_hep_repo_review.processor


class D100:
    "Was passed correctly"
    family = "pyproject"

    @staticmethod
    def check(package: Traversable) -> bool:
        """
        Requires Path(".") to be passed
        """

        return package == Path(".")


class D200:
    "Always true"
    family = "pyproject"

    @staticmethod
    def check() -> bool:
        """
        Can't be false.
        """

        return True


def test_no_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: []  # noqa: ARG005
    )

    results = scikit_hep_repo_review.processor.process(Path("."))
    assert len(results) == 0


def test_load_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    ep = importlib.metadata.EntryPoint(name="x", group="y", value="test_module:f")
    sys.modules["test_module"] = ModuleType("test_module")
    sys.modules["test_module"].f = lambda: {"D100": D100, "D200": D200}  # type: ignore[attr-defined]
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: [ep]  # noqa: ARG005
    )
    ratings = scikit_hep_repo_review.processor.collect_ratings()

    assert len(ratings) == 2
    assert "D100" in ratings
    assert "D200" in ratings
    assert ratings["D200"] == D200  # type: ignore[comparison-overlap]


def test_custom_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        scikit_hep_repo_review.processor,
        "collect_ratings",
        lambda: {"D100": D100, "D200": D200},
    )
    results = scikit_hep_repo_review.processor.process(Path("."))

    assert len(results) == 2
    assert results[0].name == "D100"
    assert results[0].result
    assert results[1].name == "D200"
    assert results[1].result
    assert len(results) == 2


def test_ignore_filter_single(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        scikit_hep_repo_review.processor,
        "collect_ratings",
        lambda: {"D100": D100, "D200": D200},
    )
    results = scikit_hep_repo_review.processor.process(Path("."), ignore=["D100"])

    assert len(results) == 1
    assert results[0].name == "D200"
    assert results[0].result


def test_ignore_filter_letter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        scikit_hep_repo_review.processor,
        "collect_ratings",
        lambda: {"D100": D100, "D200": D200},
    )
    results = scikit_hep_repo_review.processor.process(Path("."), ignore=["D"])

    assert not results
