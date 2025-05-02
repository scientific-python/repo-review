from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import repo_review as m
import repo_review.testing
from repo_review.processor import process

DIR = Path(__file__).parent.resolve()


def test_version():
    assert m.__version__


def test_local():
    pytest.importorskip("sp_repo_review")
    pytest.importorskip("validate_pyproject")
    package = DIR.parent
    results = process(package)
    assert "hatchling.build" in results.families["general"]["description"]
    assert "BSD License" in results.families["general"]["description"]
    assert "[tool.repo-review]" in results.families["validate-pyproject"]["description"]
    for result in results.results:
        if result.result is not None:
            assert result.result


def test_broken_validate_pyproject(tmp_path: Path) -> None:
    pytest.importorskip("validate_pyproject")
    tmp_path.joinpath("pyproject.toml").write_text(
        textwrap.dedent(
            """\
                [tool.repo-review]
                ignore = ["a2"]
            """
        ),
        encoding="utf-8",
    )

    results = process(tmp_path)

    (result,) = (r for r in results.results if r.name == "VPP001")
    assert "must be valid exactly by one definition" in result.err_msg
    assert not result.result


def test_broken_validate_pyproject_object(tmp_path: Path) -> None:
    pytest.importorskip("validate_pyproject")
    tmp_path.joinpath("pyproject.toml").write_text(
        textwrap.dedent(
            """\
                [tool.repo-review.ignore]
                a2 = "some message"
            """
        ),
        encoding="utf-8",
    )

    results = process(tmp_path)

    (result,) = (r for r in results.results if r.name == "VPP001")
    assert "must be valid exactly by one definition" in result.err_msg
    assert not result.result


def test_working_validate_pyproject_object(tmp_path: Path) -> None:
    pytest.importorskip("validate_pyproject")
    tmp_path.joinpath("pyproject.toml").write_text(
        textwrap.dedent(
            """\
                [tool.repo-review.ignore]
                PP102 = "some message"
            """
        ),
        encoding="utf-8",
    )

    results = process(tmp_path)

    (result,) = (r for r in results.results if r.name == "VPP001")
    assert result.result


def test_testing_function():
    pytest.importorskip("sp_repo_review")

    assert repo_review.testing.compute_check("RF001", ruff={}).result
    assert not repo_review.testing.compute_check("RF001", ruff=None).result


def test_toml_function():
    pyproject = repo_review.testing.toml_loads("one.two = 3")
    assert pyproject == {"one": {"two": 3}}
