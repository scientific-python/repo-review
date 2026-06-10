from __future__ import annotations

import pytest

from repo_review.ghpath import GHPath

INFO = [
    {"path": "pyproject.toml", "type": "blob"},
    {"path": "README.md", "type": "blob"},
    {"path": "docs", "type": "tree"},
    {"path": "docs/pyproject.toml", "type": "blob"},
    {"path": "docs/conf.py", "type": "blob"},
    {"path": "src", "type": "tree"},
    {"path": "src/a.py", "type": "blob"},
    {"path": "src/sub", "type": "tree"},
    {"path": "src/sub/b.py", "type": "blob"},
    {"path": "src2", "type": "tree"},
    {"path": "src2/c.py", "type": "blob"},
]


@pytest.fixture
def root() -> GHPath:
    return GHPath(repo="org/repo", branch="main", _info=INFO)


def test_iterdir_root(root: GHPath) -> None:
    assert {p.path for p in root.iterdir()} == {
        "pyproject.toml",
        "README.md",
        "docs",
        "src",
        "src2",
    }


def test_iterdir_subdir_with_prefix_sibling(root: GHPath) -> None:
    src = root / "src"
    assert {p.path for p in src.iterdir()} == {"src/a.py", "src/sub"}


def test_iterdir_nested_subdir(root: GHPath) -> None:
    sub = root / "src" / "sub"
    assert {p.path for p in sub.iterdir()} == {"src/sub/b.py"}


def test_glob_is_anchored(root: GHPath) -> None:
    assert {p.path for p in root.glob("pyproject.toml")} == {"pyproject.toml"}


def test_glob_recursive(root: GHPath) -> None:
    assert {p.path for p in root.glob("**/*.py")} == {
        "docs/conf.py",
        "src/a.py",
        "src/sub/b.py",
        "src2/c.py",
    }


def test_glob_single_star(root: GHPath) -> None:
    assert {p.path for p in root.glob("*.py")} == set()
    assert {p.path for p in root.glob("*/*.py")} == {
        "docs/conf.py",
        "src/a.py",
        "src2/c.py",
    }


def test_glob_from_subdir(root: GHPath) -> None:
    src = root / "src"
    assert {p.path for p in src.glob("*.py")} == {"src/a.py"}
    assert {p.path for p in src.glob("**/*.py")} == {"src/a.py", "src/sub/b.py"}
    assert {p.path for p in src.glob("pyproject.toml")} == set()


def test_joinpath_and_truediv(root: GHPath) -> None:
    joined = root.joinpath("src")
    divided = root / "src"
    assert joined.path == "src"
    assert divided.path == "src"
    assert (divided / "sub").path == "src/sub"
    assert joined.name == "src"


def test_is_dir(root: GHPath) -> None:
    assert root.is_dir()
    assert (root / "src").is_dir()
    assert (root / "src/sub").is_dir()
    assert not (root / "src/a.py").is_dir()
    assert not (root / "missing").is_dir()


def test_is_file(root: GHPath) -> None:
    assert not root.is_file()
    assert (root / "pyproject.toml").is_file()
    assert (root / "src/a.py").is_file()
    assert not (root / "src").is_file()
    assert not (root / "missing").is_file()
