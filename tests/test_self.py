from pathlib import Path

import pytest

import repo_review.processor


@pytest.fixture(autouse=True)
def patch_entry_points(local_entry_points: object) -> None:
    pass


def test_pyproject() -> None:
    families, results = repo_review.processor.process(
        Path(), extend_ignore={"X", "PP303"}
    )

    assert families == {
        "general": {},
        "pyproject": {
            "description": "Has hatchling.build backend",
            "name": "PyProject",
        },
    }
    assert len(results) == 9

    assert all(result.result for result in results)


def test_no_pyproject() -> None:
    families, results = repo_review.processor.process(
        Path("tests"), extend_ignore={"X", "PP303"}
    )

    assert families == {
        "general": {},
        "pyproject": {"description": "Has unknown backend", "name": "PyProject"},
    }
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
        Path(), subdir="tests/test_utilities"
    )

    assert families == {
        "general": {},
        "pyproject": {
            "description": "Has flit_core.buildapi backend",
            "name": "PyProject",
        },
        "skipped": {},
    }
    assert len(results) == 12

    assert (
        sum(result.result is None for result in results if result.family == "pyproject")
        == 2
    )
    assert (
        sum(result.result for result in results if isinstance(result.result, bool)) == 6
    )
    assert (
        sum(result.result is None for result in results if result.family == "general")
        == 0
    )
    assert sum(1 for result in results if result.skip_reason) == 3
    assert sum(1 for result in results if result.skip_reason == "One skip") == 1
    assert sum(1 for result in results if result.skip_reason == "Group skip") == 2
