import importlib.metadata
import sys
from importlib.abc import Traversable
from pathlib import Path
from types import ModuleType

import pytest

from scikit_hep_repo_review.processor import process


class D1:
    "Was passed correctly"
    family = "pyproject"

    @staticmethod
    def check(package: Traversable) -> bool:
        """
        Requires Path(".") to be passed
        """

        return package == Path(".")


def test_no_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: []  # noqa: ARG005
    )

    results = process(Path("."))
    assert not results["general"]
    assert not results["pyproject"]
    assert len(results) == 2


def test_custom_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = importlib.metadata.EntryPoint(name="x", group="y", value="test_module")
    sys.modules["test_module"] = ModuleType("test_module")
    sys.modules["test_module"].D1 = D1  # type: ignore[attr-defined]
    sys.modules["test_module"].repo_review_checks = {"D1"}  # type: ignore[attr-defined]
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: [mod]  # noqa: ARG005
    )

    results = process(Path("."))

    assert not results["general"]
    assert len(results["pyproject"]) == 1
    assert results["pyproject"][0].name == "D1"
    assert results["pyproject"][0].result
    assert len(results) == 2
