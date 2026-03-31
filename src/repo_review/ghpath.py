# pylint: disable=arguments-differ
# pylint: disable=unused-argument
# ruff: noqa: ARG002

from __future__ import annotations

__lazy_modules__ = ["io", "json", "sys", "typing"]

import dataclasses
import io
import json
import logging
import sys
import typing
from pathlib import PurePosixPath
from typing import Literal

from ._compat.importlib.resources.abc import Traversable
from ._compat.typing import Self, assert_never
from ._timer import log_timer

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterator

__all__ = ["EmptyTraversable", "GHPath"]


def __dir__() -> list[str]:
    return __all__


# Module-level logger
logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True, kw_only=True)
class GHPath(Traversable):
    """
    This is a Traversable that can be used to navigate a GitHub repo without
    downloading it.

    :param repo: The repo name, in "org/repo" style.
    :param branch: The branch name. "HEAD" works too.
    :param path: A sub-path inside the repo. Defaults to the repo root.
    :param _info: Some internal info stored to keep accesses fast.

    Making new paths from this path will propagate a copy of the `_fetched`
    dict.
    """

    #: The repository name, in `"org/repo"` style.
    repo: str

    #: The branch name.
    branch: str

    #: A path inside the repo
    path: str = ""

    # Stores the directory info
    _info: list[dict[str, str]] = dataclasses.field(
        hash=False, default_factory=list, repr=False
    )

    # Can keep a copy of loaded files
    _fetched: dict[str, str] = dataclasses.field(
        hash=False, default_factory=dict, repr=False
    )

    @staticmethod
    async def open_url_async(url: str) -> str:
        """This method can be overridden manually for WASM. Supports pyodide currently."""
        if sys.platform == "emscripten":
            import pyodide.http  # noqa: PLC0415

            result = await pyodide.http.pyfetch(url)
            return result.text()

        import httpx  # noqa: PLC0415

        with log_timer(logger, "Fetching %s - async", url):
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.text

    @staticmethod
    def open_url(url: str) -> str:
        """This method can be overridden manually for WASM. Supports pyodide currently."""
        if sys.platform == "emscripten":
            import pyodide.http  # noqa: PLC0415

            with log_timer(logger, "Fetching %s", url):
                return pyodide.http.open_url(url).read()

        import urllib.request  # noqa: PLC0415

        with (
            log_timer(logger, "Fetching %s", url),
            urllib.request.urlopen(url) as response,
        ):
            ret: bytes = response.read()

        return ret.decode("utf-8")

    def __post_init__(self) -> None:
        if not self._info:
            url = f"https://api.github.com/repos/{self.repo}/git/trees/{self.branch}?recursive=1"
            val: str = self.open_url(url)
            vals = json.loads(val)
            try:
                object.__setattr__(self, "_info", vals["tree"])
            except KeyError:
                print("Failed to find tree. Result:")  # noqa: T201
                print(vals)  # noqa: T201
                raise

    @classmethod
    async def async_from_repo(cls, repo: str, branch: str, path: str = "") -> Self:
        """
        Async constructor that populates `_info` by fetching the GitHub tree
        using `open_url_async` instead of performing synchronous network IO
        in `__post_init__`.

        :param repo: repository name in "org/repo" form
        :param branch: branch or ref to inspect
        :param path: optional path inside the repo
        :return: A `GHPath` instance with `_info` populated
        """
        url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
        txt = await cls.open_url_async(url)
        vals = json.loads(txt)
        _info = vals.get("tree", [])
        return cls(repo=repo, branch=branch, path=path, _info=_info)

    def __str__(self) -> str:
        return f"gh:{self.repo}@{self.branch}:{self.path or '.'}"

    @property
    def name(self) -> str:
        """
        The final element of the path or the repo name.
        """
        return (self.path or self.repo).split("/")[-1]

    @typing.overload  # type: ignore[override]
    def open(self, mode: Literal["r"], encoding: str | None = ...) -> io.StringIO: ...

    @typing.overload
    def open(self, mode: Literal["rb"]) -> io.BytesIO: ...

    def open(
        self, mode: Literal["r", "rb"] = "r", encoding: str | None = "utf-8"
    ) -> io.IOBase:
        """
        Open the repo. This doesn't support the full collection of options,
        only utf-8 and binary.

        :param mode: The mode, only ``"r"`` or ``"rb"`` supported.
        :param encoding: The encoding, only ``"utf-8"`` or ``None`` supported.
        """
        assert encoding is None or encoding == "utf-8", "Only utf-8 is supported"
        url = f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{self.path}"
        if url not in self._fetched:
            logger.warning("Cache miss for %r Refetching.", url)
            self._fetched[url] = self.open_url(url)

        if mode == "r":
            return io.StringIO(self._fetched[url])
        if mode == "rb":
            return io.BytesIO(self._fetched[url].encode("utf-8"))

        assert_never(mode)

    def _with_path(self, path: str) -> GHPath:
        return GHPath(
            repo=self.repo,
            branch=self.branch,
            path=path.lstrip("/"),
            _info=self._info,
            _fetched=self._fetched,
        )

    def joinpath(self, child: str) -> GHPath:
        return self._with_path(f"{self.path}/{child}")

    def __truediv__(self, child: str) -> GHPath:
        return self._with_path(f"{self.path}/{child}")

    def iterdir(self) -> Iterator[GHPath]:
        if self.path:
            yield from (
                self._with_path(d["path"])
                for d in self._info
                if d["path"].startswith(self.path)
            )
        else:
            yield from (
                self._with_path(d["path"]) for d in self._info if "/" not in d["path"]
            )

    def glob(self, pattern: str) -> Iterator[GHPath]:
        """
        Yield paths matching the given glob-style `pattern` relative to this
        `GHPath`. Patterns support `**` recursion via PurePosixPath.match.

        :param pattern: A glob pattern (e.g. "**/*.py" or "subdir/*.md").
        :return: An iterator of `GHPath` instances matching the pattern.
        """

        base = self.path.rstrip("/")
        combined = f"{base}/{pattern}" if base else pattern

        for entry in self._info:
            entry_path = entry.get("path", "")
            if PurePosixPath(entry_path).match(combined):
                yield self._with_path(entry_path)

    def is_dir(self) -> bool:
        return self.path in {d["path"] for d in self._info if d["type"] == "tree"}

    def is_file(self) -> bool:
        return self.path in {d["path"] for d in self._info if d["type"] == "blob"}

    def read_text(self, encoding: str | None = "utf-8") -> str:
        return self.open("r", encoding=encoding).read()

    def read_bytes(self) -> bytes:
        return self.open("rb").read()

    @property
    def _url(self) -> str:
        return (
            f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{self.path}"
        )

    async def prefetch(self) -> None:
        """
        Prefetch a file. If the file doesn't exist, this does nothing.
        """
        if self._url not in self._fetched and self.is_file():
            result = await self.open_url_async(self._url)
            self._fetched[self._url] = result


@dataclasses.dataclass(frozen=True, kw_only=True)
class EmptyTraversable(Traversable):
    """
    This is a Traversable representing an empty directory or a non-existent
    file.

    :param is_a_dir: True to treat this like an empty dir.
    :param _fake_name: A customisable fake name.
    """

    #: True if this is supposed to be a directory
    is_a_dir: bool = True

    #: Customizable fake name
    _fake_name: str = "not-a-real-path"

    def __str__(self) -> str:
        return self._fake_name

    @property
    def name(self) -> str:
        """
        Return a dummy name.
        """
        return self._fake_name

    @typing.overload  # type: ignore[override]
    def open(self, mode: Literal["r"], encoding: str | None = ...) -> io.StringIO: ...

    @typing.overload
    def open(self, mode: Literal["rb"]) -> io.BytesIO: ...

    def open(
        self, mode: Literal["r", "rb"] = "r", encoding: str | None = "utf-8"
    ) -> io.IOBase:
        raise FileNotFoundError(self._fake_name)

    def joinpath(self, child: str) -> EmptyTraversable:
        return self.__class__(is_a_dir=False)

    def __truediv__(self, child: str) -> EmptyTraversable:
        return self.__class__(is_a_dir=False)

    def iterdir(self) -> Iterator[EmptyTraversable]:
        yield from ()

    def is_dir(self) -> bool:
        return self.is_a_dir

    def is_file(self) -> bool:
        return False

    def read_text(self, encoding: str | None = "utf-8") -> str:
        raise FileNotFoundError(self._fake_name)

    def read_bytes(self) -> bytes:
        raise FileNotFoundError(self._fake_name)
