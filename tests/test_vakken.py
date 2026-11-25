from dutchquill import config, vakken

QS = """---
vak: Testvak
---
# Quick scan

## Hoe in te vullen

- [ ] Dit is uitleg, geen eis

## Rapportage

- [ ] Titelpagina met naam en datum
- [ ] Voorbeeld: dit is een voorbeeldregel
- [x] Literatuurlijst volgens APA 7

## Praktijk

- [ ] Praktijkopdracht ingeleverd
"""

RUBRIC = """## Rapportage

### Structuur
- [ ] Rode draad herkenbaar

### Taal
- [ ] Foutloos Nederlands

## Praktijk
- [ ] Demo gegeven
"""


def _vak(werkmap, code, qs=None, rubric=None):
    d = werkmap / "templates" / "vakken" / code
    d.mkdir(parents=True, exist_ok=True)
    if qs is not None:
        (d / "quick-scan.md").write_text(qs, encoding="utf-8")
    if rubric is not None:
        (d / "beoordelingscriteria.md").write_text(rubric, encoding="utf-8")


def test_alleen_rapportage(werkmap):
    items, kop = vakken.rapportage(QS)
    assert kop
    assert [i["eis"] for i in items] == ["Titelpagina met naam en datum", "Literatuurlijst volgens APA 7"]


def test_kop_met_toevoeging():
    items, kop = vakken.rapportage("## Rapportage (verplicht)\n- [ ] Eis\n## Praktijk\n- [ ] Niet\n")
    assert kop and [i["eis"] for i in items] == ["Eis"]


def test_zonder_kop_hele_bestand():
    items, kop = vakken.rapportage("1. Eerste eis\n2. Tweede eis\n")
    assert not kop and len(items) == 2


def test_een_vak_in_profiel_gaat_vanzelf(werkmap):
    config.zet("student.vakken", [{"naam": "Testvak", "code": "tv1"}])
    _vak(werkmap, "TV1", QS, RUBRIC)
    r = vakken.kies()
    assert r["status"] == "geladen" and r["vak"] == {"code": "TV1", "naam": "Testvak"}
    assert len(r["quick_scan"]["items"]) == 2
    assert [i["groep"] for i in r["beoordelingscriteria"]["items"]] == ["Structuur", "Taal"]
    assert "Criteria geladen voor TV1 (Testvak)" in r["melding"]


def test_meer_vakken_vraagt(werkmap):
    config.zet("student.vakken", [{"naam": "A", "code": "AAA"}, {"naam": "B", "code": "BBB"}])
    r = vakken.kies()
    assert r["status"] == "kies" and {o["code"] for o in r["opties"]} == {"AAA", "BBB"}
    _vak(werkmap, "BBB", qs=QS)
    r = vakken.kies("bbb")
    assert r["status"] == "geladen" and r["ontbreekt"] == ["beoordelingscriteria"]


def test_zonder_profiel_enige_vakmap(werkmap):
    _vak(werkmap, "XYZ", rubric=RUBRIC)
    r = vakken.kies()
    assert r["vak"]["code"] == "XYZ" and r["geladen"] == ["beoordelingscriteria"]


def test_geen_vakken(werkmap):
    assert vakken.kies()["status"] == "geen"
    assert vakken.kies("ONB")["status"] == "leeg"
