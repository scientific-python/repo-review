# pylint: disable=arguments-differ
# pylint: disable=unused-argument
# ruff: noqa: ARG002

from __future__ import annotations

import dataclasses
import io
import json
import typing
from collections.abc import Iterator
from typing import Literal

from ._compat.importlib.resources.abc import Traversable

__all__ = ["GHPath", "EmptyTraversable"]


def __dir__() -> list[str]:
    return __all__


@dataclasses.dataclass(frozen=True, kw_only=True)
class GHPath(Traversable):
    """
    This is a Traversable that can be used to navigate a GitHub repo without
    downloading it.

    :param repo: The repo name, in "org/repo" style.
    :param branch: The branch name. Required, even if using the default branch.
    :param path: A sub-path inside the repo. Defaults to the repo root.
    :param _info: Some internal info stored to keep accesses fast.
    """

    #: The repository name, in `"org/repo"` style.
    repo: str

    #: The branch name. Required, even if using the default branch.
    branch: str

    #: A path inside the repo
    path: str = ""

    _info: list[dict[str, str]] = dataclasses.field(
        hash=False, default_factory=list, repr=False
    )

    @staticmethod
    def open_url(url: str) -> io.StringIO:
        "This method can be overridden for pyodide with pyodide.open_url"
        import urllib.request  # pylint: disable=import-outside-toplevel

        with urllib.request.urlopen(url) as response:
            return io.StringIO(response.read().decode("utf-8"))

    def __post_init__(self) -> None:
        if not self._info:
            url = f"https://api.github.com/repos/{self.repo}/git/trees/{self.branch}?recursive=1"
            val: io.StringIO = self.open_url(url)
            vals = json.load(val)
            try:
                object.__setattr__(self, "_info", vals["tree"])
            except KeyError:
                print("Failed to find tree. Result:")  # noqa: T201
                print(vals)  # noqa: T201
                raise

    def __str__(self) -> str:
        return f"gh:{self.repo}@{self.branch}:{self.path or '.'}"

    @property
    def name(self) -> str:
        """
        The final element of the path or the repo name.
        """
        return (self.path or self.repo).split("/")[-1]

    @typing.overload  # type: ignore[override]
    def open(self, mode: Literal["r"], encoding: str | None = ...) -> io.StringIO:
        ...

    @typing.overload
    def open(self, mode: Literal["rb"]) -> io.BytesIO:
        ...

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
        val: io.StringIO = self.open_url(
            f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{self.path}"
        )
        if "b" in mode:
            return io.BytesIO(val.read().encode("utf-8"))
        return val

    def _with_path(self, path: str) -> GHPath:
        return GHPath(
            repo=self.repo, branch=self.branch, path=path.lstrip("/"), _info=self._info
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

    def is_dir(self) -> bool:
        return self.path in {d["path"] for d in self._info if d["type"] == "tree"}

    def is_file(self) -> bool:
        return self.path in {d["path"] for d in self._info if d["type"] == "blob"}

    def read_text(self, encoding: str | None = "utf-8") -> str:
        return self.open("r", encoding=encoding).read()

    def read_bytes(self) -> bytes:
        return self.open("rb").read()


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
    def open(self, mode: Literal["r"], encoding: str | None = ...) -> io.StringIO:
        ...

    @typing.overload
    def open(self, mode: Literal["rb"]) -> io.BytesIO:
        ...

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
