import importlib.metadata
from pathlib import Path

import pytest

import repo_review.processor


@pytest.fixture(autouse=True)
def patch_entry_points(monkeypatch: pytest.MonkeyPatch) -> None:
    orig_ep = importlib.metadata.entry_points
    ep = importlib.metadata.EntryPoint(
        name="pyproject",
        group="repo_review.checks",
        value="pyproject:repo_review_checks",
    )
    monkeypatch.setattr(
        importlib.metadata,
        "entry_points",
        lambda group: [ep] if group == "repo_review.checks" else orig_ep(group=group),
    )


def test_pyproject() -> None:
    families, results = repo_review.processor.process(Path("."))

    assert families == {"general": {}, "pyproject": {}}
    assert len(results) == 9

    assert all(result.result for result in results)


def test_no_pyproject() -> None:
    families, results = repo_review.processor.process(Path("tests"))

    assert families == {"general": {}, "pyproject": {}}
    assert len(results) == 9

    assert (
        sum(result.result is None for result in results if result.family == "pyproject")
        == 4
    )
    assert (
        sum(result.result for result in results if isinstance(result.result, bool)) == 1
    )
    assert (
        sum(result.result is None for result in results if result.family == "general")
        == 0
    )


def test_empty_pyproject() -> None:
    families, results = repo_review.processor.process(
        Path("."), subdir="tests/test_utilities"
    )

    assert families == {"general": {}, "pyproject": {}}
    assert len(results) == 9

    assert (
        sum(result.result is None for result in results if result.family == "pyproject")
        == 1
    )
    assert (
        sum(result.result for result in results if isinstance(result.result, bool)) == 4
    )
    assert (
        sum(result.result is None for result in results if result.family == "general")
        == 0
    )