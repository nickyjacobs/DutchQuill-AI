import pytest
from dutchquill import config, gidsen
from dutchquill.config import ConfigFout


def namen(r):
    return [g["naam"] for g in r["gidsen"]]


def test_standaard_zonder_werkmap():
    r = gidsen.voor("mail")
    assert namen(r) == ["werkwijze/basis", "werkwijze/taalronde", "toon", "nl/kern", "nl/taal", "nl/humaniseren",
                        "genres/mail"]


def test_student_krijgt_apa_en_academisch(werkmap):
    config.profiel_kies("student")
    n = namen(gidsen.voor("rapport"))
    assert {"nl/apa", "nl/ai-gebruik", "nl/academische-stijl"} <= set(n)


def test_engels_en_set(werkmap):
    n = namen(gidsen.voor("readme", sets=["taal=en", "controles.humaniseren=false"]))
    assert "en/style" in n and "en/humanize" not in n and "nl/taal" not in n
    assert "werkwijze/taalronde" in n  # de taalronde geldt altijd, ook in het Engels


def test_taalronde_ook_zonder_taalregels(werkmap):
    n = namen(gidsen.voor("mail", sets=["controles.taalregels=false"]))
    assert "werkwijze/taalronde" in n and "nl/taal" not in n


def test_eigen_genresjabloon_en_bijgewerkte_gids(werkmap, tmp_path):
    from dutchquill import paden
    eigen = werkmap / "templates" / "genres"
    eigen.mkdir(parents=True)
    (eigen / "mail.md").write_text("# Mijn mailsjabloon")
    assert gidsen.pad("genres/mail") == eigen / "mail.md"
    nieuw = paden.data() / "gidsen" / "toon.md"
    nieuw.parent.mkdir(parents=True)
    nieuw.write_text("---\ngecontroleerd: 2099-01-01\n---\n# Toon (bijgewerkt)")
    assert gidsen.pad("toon") == nieuw
    oud = paden.data() / "gidsen" / "nl" / "kern.md"
    oud.parent.mkdir(parents=True)
    oud.write_text("---\ngecontroleerd: 2000-01-01\n---\n# oud")
    assert gidsen.pad("nl/kern") != oud  # de plugin heeft een nieuwere basis


def test_onbekend():
    with pytest.raises(ConfigFout):
        gidsen.pad("genres/roman")
