from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

import repo_review as m
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
        assert result.result


def test_broken_validate_pyproject(tmp_path: Path) -> None:
    pytest.importorskip("validate_pyproject")
    tmp_path.joinpath("pyproject.toml").write_text(
        textwrap.dedent(
            """\
                [tool.repo-review]
                ignore = ["a2"]
            """
        )
    )

    results = process(tmp_path)

    (result,) = (r for r in results.results if r.name == "VPP001")
    assert "must match pattern" in result.err_msg
    assert not result.result
