import json
from pathlib import Path

import pytest

pytest.importorskip("rich")

from repo_review.__main__ import _remote_path_processor, main  # noqa: E402
from repo_review.ghpath import GHPath  # noqa: E402


@pytest.fixture
def fake_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_open(url: str) -> str:  # noqa: ARG001
        return json.dumps({"tree": []})

    monkeypatch.setattr(GHPath, "open_url", staticmethod(fake_open))


@pytest.mark.usefixtures("fake_tree")
@pytest.mark.parametrize(
    ("spec", "branch", "path"),
    [
        ("gh:org/repo", "HEAD", ""),
        ("gh:org/repo@main", "main", ""),
        ("gh:org/repo:src/pkg", "HEAD", "src/pkg"),
        ("gh:org/repo@main:src/pkg", "main", "src/pkg"),
        ("gh:org/repo@feat/x:src/pkg", "feat/x", "src/pkg"),
    ],
)
def test_remote_path_processor(spec: str, branch: str, path: str) -> None:
    result = _remote_path_processor(spec)
    assert isinstance(result, GHPath)
    assert result.repo == "org/repo"
    assert result.branch == branch
    assert result.path == path


def test_local_path_processor() -> None:
    result = _remote_path_processor("some/dir")
    assert result == Path("some/dir")


def test_main_passes_raw_string(monkeypatch: pytest.MonkeyPatch) -> None:
    # pathlib rewrites "/" on Windows, so the gh: spec must stay a string
    seen: list[object] = []

    def spy(package: object) -> object:
        seen.append(package)
        raise SystemExit(0)

    monkeypatch.setattr("repo_review.__main__._remote_path_processor", spy)
    with pytest.raises(SystemExit):
        main(["gh:org/repo@main:src/pkg"])

    assert seen == ["gh:org/repo@main:src/pkg"]
    assert isinstance(seen[0], str)
