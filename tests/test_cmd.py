import subprocess

import pytest

pytest.importorskip("rich")


def test_cmd_help():
    subprocess.run(["scikit-hep-repo-review", "--help"], check=True)


def test_cmd_basic():
    subprocess.run(["scikit-hep-repo-review", "."], check=True)


def test_cmd_html():
    subprocess.run(["scikit-hep-repo-review", ".", "--format", "html"], check=True)


def test_cmd_json():
    subprocess.run(["scikit-hep-repo-review", ".", "--format", "json"], check=True)
