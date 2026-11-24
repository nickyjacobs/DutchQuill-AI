import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def omgeving(tmp_path, monkeypatch):
    """Elke test een eigen datamap en werkmap-wijzer; nooit de echte plugin-data of werkmap."""
    data = tmp_path / "data"
    monkeypatch.setenv("DUTCHQUILL_ROOT", str(ROOT))
    monkeypatch.setenv("DUTCHQUILL_DATA", str(data))
    monkeypatch.delenv("CLAUDE_PLUGIN_DATA", raising=False)
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.chdir(project)
    yield
    os.chdir(ROOT)


@pytest.fixture
def werkmap(tmp_path):
    from dutchquill import werkmap as wm
    pad = tmp_path / "DutchQuill"
    wm.init(pad, taal="nl", profiel="zakelijk")
    return pad
