import json
from datetime import date

import sessie_start


def _root(tmp_path, gecontroleerd):
    r = tmp_path / "root"
    (r / "gidsen").mkdir(parents=True)
    (r / "gidsen" / "stand.json").write_text(json.dumps({"gecontroleerd": gecontroleerd}))
    return r


def test_niet_ingesteld_een_keer(tmp_path):
    root, data = _root(tmp_path, "2026-11-20"), tmp_path / "d"
    data.mkdir()
    m, status = sessie_start.bepaal(root, data, date(2026, 11, 24))
    assert len(m) == 1 and "nog niet ingesteld" in m[0]
    (data / "bijwerken.json").write_text(json.dumps(status))
    m, _ = sessie_start.bepaal(root, data, date(2026, 11, 25))
    assert m == []


def test_maandmelding_eens_per_periode(tmp_path):
    root, data = _root(tmp_path, "2026-10-01"), tmp_path / "d"
    data.mkdir()
    (data / "werkmap").write_text("/x")
    m, status = sessie_start.bepaal(root, data, date(2026, 10, 30))
    assert m == []
    m, status = sessie_start.bepaal(root, data, date(2026, 10, 31))
    assert len(m) == 1 and "/dutchquill:bijwerken" in m[0]
    (data / "bijwerken.json").write_text(json.dumps(status))
    for dag in (1, 15, 29):
        m, _ = sessie_start.bepaal(root, data, date(2026, 11, dag))
        assert m == [], dag
    m, _ = sessie_start.bepaal(root, data, date(2026, 11, 30))
    assert len(m) == 1


def test_eigen_controle_en_ingestelde_dagen(tmp_path):
    root, data = _root(tmp_path, "2026-01-01"), tmp_path / "d"
    data.mkdir()
    (data / "werkmap").write_text("/x")
    (data / "bijwerken.json").write_text(json.dumps({"laatst_gecontroleerd": "2026-11-01"}))
    (data / "hook.json").write_text(json.dumps({"herinnering_dagen": 10}))
    assert sessie_start.bepaal(root, data, date(2026, 11, 10))[0] == []
    assert len(sessie_start.bepaal(root, data, date(2026, 11, 11))[0]) == 1


def test_kapotte_bestanden_geen_crash(tmp_path):
    root, data = tmp_path / "leeg", tmp_path / "d"
    data.mkdir()
    (data / "werkmap").write_text("/x")
    (data / "bijwerken.json").write_text("{kapot")
    assert sessie_start.bepaal(root, data, date(2026, 11, 24))[0] == []
