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
