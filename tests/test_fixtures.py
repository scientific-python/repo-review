import importlib.metadata
import sys
from pathlib import Path
from types import ModuleType

import pytest

from repo_review._compat.importlib.resources.abc import Traversable
from repo_review.checks import collect_checks
from repo_review.fixtures import apply_fixtures, compute_fixtures


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


def nothing() -> int:
    return 42


def simple(package: Traversable) -> str:
    return str(package)


def not_simple(simple: str, package: Traversable) -> str:
    return f"{simple} {package}"


def get_checks(some_bool: bool) -> dict[str, type]:
    return {"D100": D100, "D200": D200} if some_bool else {"D100": D100}


def test_process_fixtures() -> None:
    fixtures = compute_fixtures(
        Path("."),
        Path("."),
        {"simple": simple, "nothing": nothing, "not_simple": not_simple},
    )

    assert apply_fixtures(fixtures, nothing) == 42
    assert apply_fixtures(fixtures, simple) == "."
    assert apply_fixtures(fixtures, not_simple) == ". ."


def test_process_fixtures_with_package() -> None:
    fixtures = compute_fixtures(
        Path("."),
        Path("."),
        {
            "simple": simple,
            "nothing": nothing,
            "not_simple": not_simple,
        },
    )

    assert apply_fixtures(fixtures, nothing) == 42
    assert apply_fixtures(fixtures, simple) == "."
    assert apply_fixtures(fixtures, lambda package: package) == Path(".")
    assert apply_fixtures(fixtures, not_simple) == ". ."


@pytest.mark.parametrize("some_bool", [True, False])
def test_process_checks(monkeypatch: pytest.MonkeyPatch, some_bool: bool) -> None:
    ep = importlib.metadata.EntryPoint(name="x", group="y", value="test_module:f")
    sys.modules["test_module"] = ModuleType("test_module")
    sys.modules["test_module"].f = get_checks  # type: ignore[attr-defined]
    monkeypatch.setattr(
        importlib.metadata, "entry_points", lambda group: [ep]  # noqa: ARG005
    )
    checks = collect_checks({"package": Path("."), "some_bool": some_bool})
    assert len(checks) == 1 + some_bool
