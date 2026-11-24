from pathlib import Path

import pytest
from dutchquill import versies
from dutchquill.config import ConfigFout


def test_volgende_en_laatste(werkmap):
    a = versies.volgende("schrijven", "Mijn rapport: deel 1?")
    assert a["versie"] == 1 and a["titel"] == "Mijn rapport deel 1"
    b = versies.volgende("schrijven", "Mijn rapport: deel 1?")
    assert b["versie"] == 2 and b["vorige"].endswith("v1")
    (werkmap / "2-output" / "schrijven" / "Mijn rapport deel 1" / "v2" / "x.md").write_text("x")
    assert versies.laatste("schrijven", "Mijn rapport: deel 1?")["bestanden"] == ["x.md"]
    assert versies.lijst() == [{"actie": "schrijven", "titel": "Mijn rapport deel 1", "versies": 2, "laatste": "v2"}]


def test_zonder_werkmap_duidelijke_fout():
    with pytest.raises(ConfigFout, match="instellen"):
        versies.volgende("schrijven", "x")


def test_lege_titel():
    assert versies.veilige_titel("  ///  ") == "zonder titel"


def test_nieuwe_ronde_op_eerdere_output(werkmap):
    v1 = versies.volgende("schrijven", "Studio instellen")
    bron = f"{v1['map']}/bron.md"
    # herschrijven op een eerdere output: v2 in dezelfde titelmap, niet herschrijven/.../v1
    v2 = versies.volgende("herschrijven", "iets anders", van=bron)
    assert v2["actie"] == "schrijven" and v2["versie"] == 2
    assert Path(v2["map"]).parts[-3:] == ("schrijven", "Studio instellen", "v2")
    # een pad buiten 2-output: gewoon de opgegeven actie
    los = versies.volgende("herschrijven", "Los", van=str(werkmap / "1-input" / "rapporten" / "x.md"))
    assert los["actie"] == "herschrijven" and los["versie"] == 1
    with pytest.raises(ConfigFout):
        versies.volgende(None, None, van=str(werkmap / "elders.md"))


def test_vervolgronde_neemt_formaten_over(werkmap):
    v1 = versies.volgende("schrijven", "Rapport")
    for ext in ("docx", "pdf"):
        (Path(v1["map"]) / f"Rapport.{ext}").write_text("x")
    (Path(v1["map"]) / "bron.md").write_text("x")
    v2 = versies.volgende(None, None, van=v1["map"] + "/bron.md")
    assert v2["versie"] == 2 and v2["vorige_formaten"] == ["docx", "pdf"]
    assert versies.volgende("schrijven", "Nieuw")["vorige_formaten"] == []


def test_versies_uit_overschrijft_v1(werkmap):
    from dutchquill import config
    config.zet("versies", False)
    a = versies.volgende("schrijven", "Memo")
    b = versies.volgende("schrijven", "Memo")
    assert a["versie"] == b["versie"] == 1 and a["map"] == b["map"]
