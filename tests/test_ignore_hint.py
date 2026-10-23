import pytest

pytest.importorskip("rich")

from repo_review.__main__ import rich_printer
from repo_review.processor import Result


def _results() -> list[Result]:
    return [
        Result(family="a", name="A100", description="Passes", result=True),
        Result(family="a", name="A101", description="Fails", result=False),
        Result(family="b", name="B200", description="Also fails", result=False),
        Result(family="b", name="B201", description="Skipped", result=None),
    ]


def test_ignore_hint(capsys: pytest.CaptureFixture[str]) -> None:
    rich_printer({}, _results(), color=False, status="errors")
    out = capsys.readouterr().out
    assert "[tool.repo-review]" in out
    assert 'ignore = ["A101", "B200"]' in out


def test_no_ignore_hint_without_failures(capsys: pytest.CaptureFixture[str]) -> None:
    results = [r for r in _results() if r.result is not False]
    rich_printer({}, results, color=False, status="skips")
    assert "tool.repo-review" not in capsys.readouterr().out
