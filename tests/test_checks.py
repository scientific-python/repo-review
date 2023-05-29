import importlib.metadata
import sys
from importlib.abc import Traversable
from pathlib import Path
from types import ModuleType

import pytest

from scikit_hep_repo_review.processor import process


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

    results = process(Path("."))
    assert not results["general"]
    assert not results["pyproject"]
    assert len(results) == 2


@pytest.fixture()
def load_test_module(monkeypatch: pytest.MonkeyPatch) -> None:
    mod = importlib.metadata.EntryPoint(name="x", group="y", value="test_module")
    sys.modules["test_module"] = ModuleType("test_module")
    sys.modules["test_module"].D100 = D100  # type: ignore[attr-defined]
    sys.modules["test_module"].D200 = D200  # type: ignore[attr-defined]
    sys.modules["test_module"].repo_review_checks = {"D100", "D200"}  # type: ignore[attr-defined]
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: [mod]  # noqa: ARG005
    )


@pytest.mark.usefixtures("load_test_module")
def test_custom_checks() -> None:
    results = process(Path("."))

    assert not results["general"]
    assert len(results["pyproject"]) == 2
    assert results["pyproject"][0].name == "D100"
    assert results["pyproject"][0].result
    assert results["pyproject"][1].name == "D200"
    assert results["pyproject"][1].result
    assert len(results) == 2


@pytest.mark.usefixtures("load_test_module")
def test_ignore_filter_single() -> None:
    results = process(Path("."), ignore=["D100"])

    assert not results["general"]
    assert len(results["pyproject"]) == 1
    assert results["pyproject"][0].name == "D200"
    assert results["pyproject"][0].result
    assert len(results) == 2


@pytest.mark.usefixtures("load_test_module")
def test_ignore_filter_letter() -> None:
    results = process(Path("."), ignore=["D"])

    assert not results["general"]
    assert len(results["pyproject"]) == 0
    assert len(results) == 2
