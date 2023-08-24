import json
import textwrap
import xml.etree.ElementTree as ET
from collections.abc import Sequence
from pathlib import Path

import pytest
from click.testing import CliRunner

from repo_review.__main__ import main


@pytest.fixture()
def multiple_packages(tmp_path: Path) -> tuple[str, str]:
    packages = (tmp_path / "package_1", tmp_path / "package_2")

    for package in packages:
        package.mkdir()

        basic_toml = textwrap.dedent(
            """\
            [build-system]
            requires = ["somepackage"]
            build-backend="somebackend"

            [tool.pytest.ini_options]
            minversion = "6.0"
            """
        )

        package.joinpath("pyproject.toml").write_text(basic_toml)
        package.joinpath(".pre-commit-config.yaml").touch()
        package.joinpath("README.md").touch()

        package.joinpath("docs").mkdir()
        package.joinpath("tests").mkdir()

    return (str(packages[0]), str(packages[1]))


@pytest.mark.usefixtures("local_entry_points")
def test_multiple_packages_rich(multiple_packages: Sequence[str]) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [*multiple_packages])
    assert result.exit_code == 0
    assert "package_1" in result.output
    assert "package_2" in result.output
    assert "Has somebackend backend" in result.output


@pytest.mark.usefixtures("local_entry_points")
def test_multiple_packages_json(multiple_packages: Sequence[str]) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [*multiple_packages, "--format", "json"])
    assert result.exit_code == 0
    output = json.loads(result.output)
    assert len(output) == 2
    assert "package_1" in output
    assert "package_2" in output


@pytest.mark.usefixtures("local_entry_points")
def test_multiple_packages_html(multiple_packages: Sequence[str]) -> None:
    runner = CliRunner()
    result = runner.invoke(main, [*multiple_packages, "--format", "html"])
    assert result.exit_code == 0
    tree = ET.fromstring(f"<body>{result.output}</body>")
    assert len(tree) == 2
    assert tree[0].tag == "details"
    assert tree[0][0][0].text == "package_1"
    assert tree[0][0][0].tail == ": (all passed)"
    assert tree[1][0][0].text == "package_2"
