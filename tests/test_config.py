import pytest
from dutchquill import config
from dutchquill.config import ConfigFout


def test_zonder_werkmap_standaardwaarden():
    e = config.effectief()
    assert e["ingesteld"] is False
    assert e["profiel"] == "zakelijk"
    assert e["controles"]["apa"] is False
    assert e["mappen"] == {}


def test_init_maakt_structuur(werkmap):
    assert (werkmap / "dutchquill.yaml").is_file()
    for sub in ("1-input/notities", "1-input/beeld", "1-input/mijn-stijl", "2-output/schrijven", "templates"):
        assert (werkmap / sub).is_dir()
    e = config.effectief()
    assert e["ingesteld"] and e["werkmap"] == str(werkmap)
    assert e["mappen"]["beeld"].endswith("1-input/beeld")


def test_init_overschrijft_niets(werkmap):
    from dutchquill import werkmap as wm
    (werkmap / "eigen-regels.md").write_text("mijn tekst")
    wm.init(werkmap, taal="en", profiel="student")
    assert (werkmap / "eigen-regels.md").read_text() == "mijn tekst"
    assert config.effectief()["profiel"] == "zakelijk"


def test_engelse_mapnamen(tmp_path):
    from dutchquill import werkmap as wm
    wm.init(tmp_path / "DQ", taal="en")
    assert (tmp_path / "DQ" / "1-input" / "notes").is_dir()
    assert (tmp_path / "DQ" / "README.md").is_file()


def test_zet_op_meegeleverd_profiel_maakt_eigen_kopie(werkmap):
    melding = config.zet("controles.apa", True)
    assert "zakelijk-eigen" in melding
    e = config.effectief()
    assert e["profiel"] == "zakelijk-eigen"
    assert e["profiel_keten"] == ["zakelijk", "zakelijk-eigen"]
    assert e["controles"]["apa"] is True
    assert e["controles"]["humaniseren"] is True  # rest komt uit de basis


def test_zet_bewaart_commentaar(werkmap):
    config.zet("versies", False)
    tekst = (werkmap / "dutchquill.yaml").read_text()
    assert "# Elke nieuwe ronde over dezelfde titel" in tekst
    assert (werkmap / "dutchquill.yaml.bak").is_file()


def test_ongeldige_waarde_wordt_niet_opgeslagen(werkmap):
    voor = (werkmap / "dutchquill.yaml").read_text()
    with pytest.raises(ConfigFout, match="geen geldige keuze"):
        config.zet("toon.niveau", "superformeel")
    assert (werkmap / "dutchquill.yaml").read_text() == voor


def test_eigen_profiel_met_basis_en_genre(werkmap):
    config.profiel_nieuw("linkedin-nicky", basis="social", beschrijving="Mijn posts")
    config.profiel_kies("linkedin-nicky")
    config.zet("toon.niveau", "luchtig")
    config.profiel_kies("student")
    config.zet("genre_profielen.linkedin", "linkedin-nicky")
    assert config.effectief()["toon"]["niveau"] == "formeel"
    e = config.effectief(genre="linkedin")
    assert e["profiel"] == "linkedin-nicky"
    assert e["toon"]["niveau"] == "luchtig"
    assert e["controles"]["apa"] is False


def test_profiel_kring_en_onbekend():
    with pytest.raises(ConfigFout, match="kring"):
        config.profiel_keten("a", {"a": {"basis": "b"}, "b": {"basis": "a"}}, {})
    with pytest.raises(ConfigFout, match="Onbekend profiel"):
        config.profiel_keten("bestaat-niet", {}, config.ingebouwde_profielen())


def test_verwijder_actief_profiel_valt_terug_op_basis(werkmap):
    config.profiel_nieuw("tijdelijk", basis="techniek", beschrijving=None)
    config.profiel_kies("tijdelijk")
    config.profiel_verwijder("tijdelijk")
    assert config.effectief()["profiel"] == "techniek"
    with pytest.raises(ConfigFout):
        config.profiel_verwijder("student")


def test_projectconfig_en_set_winnen(werkmap, tmp_path):
    (tmp_path / "project" / ".dutchquill.yaml").write_text("toon:\n  niveau: luchtig\ntaal: en\n")
    e = config.effectief()
    assert e["toon"]["niveau"] == "luchtig"
    assert e["taal"] == "en"
    e = config.effectief(sets=["toon.niveau=formeel", "uitvoer.formaten=[md, pdf]"])
    assert e["toon"]["niveau"] == "formeel"
    assert e["uitvoer"]["formaten"] == ["md", "pdf"]


def test_waarschuwing_apa_met_luchtige_toon(werkmap):
    e = config.effectief(sets=["controles.apa=true", "toon.niveau=luchtig"])
    assert any("APA" in w for w in e["waarschuwingen"])


def test_naam_van_meegeleverd_profiel_niet_als_eigen(werkmap):
    with pytest.raises(ConfigFout):
        config.profiel_nieuw("student", basis=None, beschrijving=None)


def test_hook_json_wordt_bijgewerkt(werkmap):
    import json

    from dutchquill import paden
    config.zet("bijwerken.herinnering_dagen", 45)
    assert json.loads((paden.data() / "hook.json").read_text())["herinnering_dagen"] == 45
