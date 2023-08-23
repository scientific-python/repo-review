import subprocess

import pytest

pytest.importorskip("rich")
pytest.importorskip("sp_repo_review")


def test_cmd_help():
    subprocess.run(["repo-review", "--help"], check=True)


def test_cmd_help_short():
    subprocess.run(["repo-review", "-h"], check=True)


def test_cmd_version():
    subprocess.run(["repo-review", "--version"], check=True)


def test_cmd_list_all():
    subprocess.run(["repo-review", "--list-all"], check=True)


def test_cmd_basic():
    subprocess.run(["repo-review", "."], check=True)


def test_cmd_pyproject():
    subprocess.run(["repo-review", "pyproject.toml"], check=True)


def test_cmd_dual():
    subprocess.run(["repo-review", "../repo-review", "../repo-review"], check=True)


def test_cmd_html():
    subprocess.run(
        ["repo-review", ".", "--format", "html", "--stderr", "html"], check=True
    )


def test_cmd_json():
    subprocess.run(
        ["repo-review", ".", "--format", "json", "--stderr", "json"], check=True
    )


def test_cmd_svg():
    subprocess.run(
        ["repo-review", ".", "--format", "svg", "--stderr", "svg"], check=True
    )


def test_cmd_show_only_err():
    subprocess.run(["repo-review", ".", "--show", "err"], check=True)


def test_cmd_show_only_errskip():
    subprocess.run(["repo-review", ".", "--show", "errskip"], check=True)
