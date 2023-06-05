import dataclasses
import importlib.metadata
import sys
from pathlib import Path
from types import ModuleType
from typing import ClassVar

import pytest

import repo_review.processor
from repo_review._compat.importlib.resources.abc import Traversable
from repo_review.checks import collect_checks


class D100:
    "Was passed correctly"
    family = "pyproject"
    url = "https://example.com"

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


@dataclasses.dataclass(frozen=True, kw_only=True)
class C100:
    "Can compute custom output strings"
    fail: bool
    family: ClassVar[str] = "custom"

    def check(self) -> str:
        "Never see me"
        return "I'm a custom error message" if self.fail else ""


def test_no_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: []  # noqa: ARG005
    )

    _, results = repo_review.processor.process(Path("."))
    assert len(results) == 0


def test_load_entry_point(monkeypatch: pytest.MonkeyPatch) -> None:
    ep = importlib.metadata.EntryPoint(name="x", group="y", value="test_module:f")
    sys.modules["test_module"] = ModuleType("test_module")
    sys.modules["test_module"].f = lambda: {"D100": D100, "D200": D200}  # type: ignore[attr-defined]
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: [ep]  # noqa: ARG005
    )
    checks = collect_checks({"package": Path(".")})

    assert len(checks) == 2
    assert "D100" in checks
    assert "D200" in checks
    assert checks["D200"] == D200  # type: ignore[comparison-overlap]


def test_custom_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"D100": D100, "D200": D200},
    )
    _, results = repo_review.processor.process(Path("."))

    assert len(results) == 2
    assert results[0].name == "D100"
    assert results[0].result
    assert results[0].url == "https://example.com"
    assert results[1].name == "D200"
    assert results[1].result
    assert not results[1].url
    assert len(results) == 2


def test_ignore_filter_single(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"D100": D100, "D200": D200},
    )
    _, results = repo_review.processor.process(Path("."), ignore={"D100"})

    assert len(results) == 1
    assert results[0].name == "D200"
    assert results[0].result


def test_ignore_filter_letter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"D100": D100(), "D200": D200()},
    )
    _, results = repo_review.processor.process(Path("."), ignore={"D"})

    assert not results


def test_select_filter_letter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"D100": D100(), "D200": D200(), "C100": C100(fail=True)},
    )
    _, results = repo_review.processor.process(Path("."), select={"D"})

    assert len(results) == 2


def test_select_filter_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"D100": D100(), "D200": D200()},
    )
    _, results = repo_review.processor.process(Path("."), select={"D100"})

    assert len(results) == 1


def test_string_result(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        repo_review.processor,
        "collect_checks",
        lambda _: {"C100": C100(fail=False), "C101": C100(fail=True)},
    )
    _, results = repo_review.processor.process(Path("."))

    assert len(results) == 2
    check_c100 = results[0]
    check_c101 = results[1]

    assert check_c100.name == "C100"
    assert check_c100.result is True
    assert not check_c100.err_msg

    assert check_c101.name == "C101"
    assert check_c101.result is False
    assert check_c101.err_msg == "I'm a custom error message"
