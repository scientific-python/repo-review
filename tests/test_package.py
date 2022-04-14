from __future__ import annotations

import io
import sys
import urllib.request
from pathlib import Path
from types import ModuleType

import scikit_hep_repo_review as m
from scikit_hep_repo_review.processor import process

DIR = Path(__file__).parent.resolve()


def test_version():
    assert m.__version__


def open_url(url: str) -> io.StringIO:
    with urllib.request.urlopen(url) as response:
        return io.StringIO(response.read().decode("utf-8"))


def test_pyodide():
    mod1 = ModuleType("pyodide")
    mod2 = ModuleType("pyodide.http")
    mod1.http = mod2
    mod2.open_url = open_url

    sys.modules["pyodide"] = mod1
    sys.modules["pyodide.http"] = mod2

    sys.path.append(str(DIR / "../docs"))

    import ghpath

    package = ghpath.GHPath(repo="henryiii/scikit-hep-repo-review", branch="main")
    results = process(package)
    assert results
