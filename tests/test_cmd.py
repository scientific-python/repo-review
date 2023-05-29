import subprocess

import pytest

pytest.importorskip("rich")


def test_cmd_help():
    subprocess.run(["scikit-hep-repo-review", "--help"], check=True)


def test_cmd_basic():
    subprocess.run(["scikit-hep-repo-review", "."], check=True)
