import asyncio
import json

import pytest

from repo_review.ghpath import GHPath


def test_async_from_repo_monkeypatched(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_open(url: str) -> str:  # noqa: ARG001
        # Return a simple tree with one file
        return json.dumps({"tree": [{"path": "pyproject.toml", "type": "blob"}]})

    monkeypatch.setattr(GHPath, "open_url_async", staticmethod(fake_open))

    gh = asyncio.run(GHPath.async_from_repo("org/repo", "main"))
    assert isinstance(gh, GHPath)
    assert any(d["path"] == "pyproject.toml" for d in gh._info)


def test_prefetch_populates_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    # Prepare a GHPath with a single file in _info
    info = [{"path": "pyproject.toml", "type": "blob"}]
    gh = GHPath(repo="org/repo", branch="main", path="pyproject.toml", _info=info)

    async def fake_open(url: str) -> str:  # noqa: ARG001
        return "[tool.poetry]\nname = 'x'\n"

    monkeypatch.setattr(GHPath, "open_url_async", staticmethod(fake_open))

    # Ensure cache empty
    assert gh._url not in gh._fetched

    asyncio.run(gh.prefetch())

    # After prefetch, cache should contain fetched text
    assert gh._url in gh._fetched
    assert "tool.poetry" in gh._fetched[gh._url]
