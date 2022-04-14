from __future__ import annotations

import dataclasses
import io
import json
from typing import Iterator, Literal

from pyodide.http import open_url


@dataclasses.dataclass(frozen=True, kw_only=True)
class GHPath:
    repo: str
    branch: str
    path: str = ""
    _info: list[dict[str, str]] = dataclasses.field(
        hash=False, default_factory=list, repr=False
    )

    def __post_init__(self):
        if not self._info:
            url = f"https://api.github.com/repos/{self.repo}/git/trees/{self.branch}?recursive=1"
            val: io.StringIO = open_url(url)
            vals = json.load(val)
            object.__setattr__(self, "_info", vals["tree"])

    @property
    def name(self) -> str:
        return (self.path or self.repo).split("/")[-1]

    def open(self, mode: Literal["r", "rb"] = "r") -> io.IOBase:
        val: io.StringIO = open_url(
            f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{self.path}"
        )
        if "b" in mode:
            return io.BytesIO(val.read().encode("utf-8"))
        return val

    def _with_path(self, path: str) -> GHPath:
        return GHPath(
            repo=self.repo, branch=self.branch, path=path.lstrip("/"), _info=self._info
        )

    def joinpath(self, path: str) -> GHPath:
        return self._with_path(f"{self.path}/{path}")

    __truediv__ = joinpath

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

    def read_text(self) -> str:
        return self.open("r").read()

    def read_bytes(self) -> bytes:
        return self.open("rb").read()
