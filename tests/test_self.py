from pathlib import Path

import pytest

import repo_review.processor


@pytest.fixture(autouse=True)
def patch_entry_points(local_entry_points: object) -> None:  # noqa: ARG001
    pass


def test_pyproject() -> None:
    families, results = repo_review.processor.process(Path())

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
    families, results = repo_review.processor.process(Path("tests"))

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
    }
    assert len(results) == 9

    assert (
        sum(result.result is None for result in results if result.family == "pyproject")
        == 1
    )
    assert (
        sum(result.result for result in results if isinstance(result.result, bool)) == 6
    )
    assert (
        sum(result.result is None for result in results if result.family == "general")
        == 0
    )
