from __future__ import annotations

from pathlib import Path

import pytest

import scikit_hep_repo_review as m
from scikit_hep_repo_review.ghpath import GHPath
from scikit_hep_repo_review.processor import process

DIR = Path(__file__).parent.resolve()


def test_version():
    assert m.__version__


@pytest.mark.skip
def test_pyodide():
    package = GHPath(repo="scikit-hep/repo-review", branch="main")
    results = process(package)
    assert results
