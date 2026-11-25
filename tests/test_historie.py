import json

import pytest
from dutchquill import config, historie


def test_log_zonder_tekst(werkmap):
    r = historie.log("schrijven", "Plan", ["2-output/schrijven/plan/v1/Plan.docx"], {"genre": "memo"})
    assert "tekst" not in r and historie.toon()[-1]["titel"] == "Plan"


def test_log_met_tekst_bewaart_kopie(werkmap):
    r = historie.log("humaniseren", "Post over / werk?", [], {"modus": "scan", "uitvoer": "chat"}, "Dit is de post.")
    kopie = werkmap / ".dutchquill" / r["tekst"]
    assert kopie.read_text(encoding="utf-8") == "Dit is de post."
    assert r["tekst"].startswith("historie/") and "humaniseren-post-over-werk" in r["tekst"]
    assert r["woorden"] == 4
    regel = json.loads((werkmap / ".dutchquill" / "historie.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert regel["tekst"] == r["tekst"] and regel["meta"]["modus"] == "scan"


def test_twee_keer_dezelfde_seconde(werkmap):
    a = historie.log("reviewen", "Mail", [], {}, "een")
    b = historie.log("reviewen", "Mail", [], {}, "twee")
    assert a["tekst"] != b["tekst"]


def test_tekst_bewaren_uit(werkmap):
    config.zet("historie.tekst_bewaren", False)
    r = historie.log("schrijven", "Geheim", [], {}, "Vertrouwelijke tekst")
    assert "tekst" not in r and not (werkmap / ".dutchquill" / "historie").exists()


def test_cli_tekst_uit_bestand(werkmap, tmp_path, capsys):
    bron = tmp_path / "concept.md"
    bron.write_text("Hallo wereld", encoding="utf-8")
    historie.main(["log", "--actie", "reviewen", "--titel", "Hallo", "--tekst", str(bron)])
    assert "met de tekst in historie/" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        historie.main(["log", "--actie", "reviewen", "--titel", "X", "--tekst", str(tmp_path / "weg.md")])
