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


@pytest.mark.parametrize("cmd", list(cli.EIGEN))
def test_eigen_commando_help(cmd, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dq", cmd, "--help"])
    with pytest.raises(SystemExit) as e:
        cli.main()
    assert e.value.code == 0


def test_doctor_libreoffice_tip(monkeypatch):
    from dutchquill import doctor, export
    monkeypatch.setattr(doctor.shutil, "which", lambda naam: None)
    monkeypatch.setattr(export, "_browser", lambda: "/pad/naar/chrome")
    via, tips = doctor.pdf_route()
    assert via.startswith("browser") and "LibreOffice" in tips[0]
    monkeypatch.setattr(doctor.shutil, "which", lambda naam: "/usr/bin/soffice" if naam == "soffice" else None)
    via, tips = doctor.pdf_route()
    assert via.startswith("libreoffice") and tips == []
