import sys

import pytest
from dutchquill import cli


def test_hulp(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dq"])
    cli.main()
    assert "tells" in capsys.readouterr().out


@pytest.mark.parametrize("cmd", list(cli.TOOLS))
def test_elke_tool_laadt(cmd, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dq", cmd, "--help"])
    with pytest.raises(SystemExit) as e:
        cli.main()
    assert e.value.code == 0


@pytest.mark.parametrize("cmd", ["config", "werkmap", "versie", "historie", "doctor"])
def test_eigen_commando_help(cmd, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dq", cmd, "--help"])
    with pytest.raises(SystemExit) as e:
        cli.main()
    assert e.value.code == 0
