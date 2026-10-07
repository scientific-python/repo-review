import json
import logging

import pytest

pytest.importorskip("rich")
pytest.importorskip("sp_repo_review")

from repo_review.__main__ import main


def test_log_output_does_not_corrupt_stdout(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    logger = logging.getLogger("repo_review")
    monkeypatch.setattr(logger, "handlers", [])
    monkeypatch.setattr(logger, "propagate", True)
    monkeypatch.setattr(logger, "level", logger.level)

    main([".", "--format", "json", "--log-level", "DEBUG"])

    out, err = capsys.readouterr()
    json.loads(out)
    assert "Processing checks" in err
