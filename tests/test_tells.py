from pathlib import Path

import pytest
from dutchquill import tells

F = Path(__file__).parent / "fixtures"


def lees(naam):
    return (F / naam).read_text(encoding="utf-8")


@pytest.mark.parametrize("naam,taal", [("ai_nl.md", "nl"), ("ai_en.md", "en")])
def test_ai_tekst_hoog(naam, taal):
    r = tells.analyseer(lees(naam))
    assert r["taal"] == taal and r["niveau"] == "hoog"
    assert r["per_categorie"].get("woord", 0) >= 4


@pytest.mark.parametrize("naam", ["mens_nl.md", "mens_en.md"])
def test_mensentekst_laag(naam):
    r = tells.analyseer(lees(naam))
    assert r["niveau"] == "laag", tells.rapport(r)


def test_herkent_kernpatronen_nl():
    cats = tells.analyseer(lees("ai_nl.md"))["per_categorie"]
    for c in ("frase_aanloop", "frase_afsluiter", "frase_vage_bron", "niet_x_maar_y", "retorische_aanloop",
              "connectoren", "title_case", "cluster"):
        assert c in cats, c


def test_herkent_kernpatronen_en():
    cats = tells.analyseer(lees("ai_en.md"))["per_categorie"]
    for c in ("frase_chatbot", "frase_afsluiter", "frase_vage_bron", "retorische_aanloop"):
        assert c in cats, c


def test_geen_dubbele_treffer_binnen_langere_term():
    r = tells.analyseer("Er is een breed scala aan opties voor de klant om uit te kiezen vandaag.", taal="nl")
    assert [b["match"].lower() for b in r["bevindingen"] if b["cat"] == "woord"] == ["een breed scala aan"]


def test_linkedin_formules_alleen_bij_linkedin():
    tekst = lees("ai_linkedin.md")
    met = tells.analyseer(tekst, genre="linkedin")["per_categorie"]
    zonder = tells.analyseer(tekst, genre="rapport")["per_categorie"]
    assert {"frase_linkedin", "hashtags", "broetry", "emoji"} <= set(met)
    assert "frase_linkedin" not in zonder and "hashtags" not in zonder


def test_mail_mag_laat_het_me_weten():
    r = tells.analyseer("Hoi Lisa, donderdag past mij goed. Laat het me weten als er iets verandert.",
                        taal="nl", genre="mail")
    assert r["punten"] == 0


def test_overcorrectie_korte_zinnen():
    zinnen = ["Dit werkt.", "Het is snel.", "Wij testen het.", "Iedereen doet mee.", "Dat is goed.",
              "We gaan door.", "De klant wil dit.", "Het team ook.", "Prima zo."]
    tekst = " ".join(zinnen) + " " + "Daarna kijken we in de volgende sprint opnieuw naar de cijfers van het project."
    r = tells.analyseer(tekst, taal="nl", genre="zakelijk-rapport")
    assert "ritme_overgecorrigeerd" in r["per_categorie"]
    r2 = tells.analyseer(tekst, taal="nl", genre="linkedin")
    assert "ritme_overgecorrigeerd" not in r2["per_categorie"]


def test_stem_wint_van_streepjesregel():
    tekst = "Het plan is klaar - eindelijk. We starten maandag - als alles meezit. " * 3
    zonder = tells.analyseer(tekst, taal="nl")
    met = tells.analyseer(tekst, taal="nl", stem={"streepjes_per_1000": 12})
    assert "streepje" in zonder["per_categorie"] and "streepje" not in met["per_categorie"]


def test_eigen_regels_en_whitelist():
    tekst = "We zoeken synergie in het team en een robuuste schatting van de kosten."
    r = tells.analyseer(tekst, taal="nl", nooit=["team"], wel=["synergie in het team"])
    cats = [b["cat"] for b in r["bevindingen"]]
    assert "eigen_regel" in cats
    assert not any(b["cat"] == "woord" and b["match"].lower() == "synergie" for b in r["bevindingen"])
    assert not any((b["match"] or "").lower() == "robuuste" for b in r["bevindingen"])  # vakterm-whitelist


def test_code_en_urls_tellen_niet():
    tekst = "Zie `cruciaal_config.yaml` en https://example.org/naadloos voor details over de installatie.\n" \
            "```\ncruciaal = True\n```\n"
    assert tells.analyseer(tekst, taal="nl")["punten"] == 0


def test_eigen_regels_uit_werkmap(werkmap):
    regels = "# Eigen regels\n\n## Nooit gebruiken\n- synergetisch\n\n## Juist wel\n- robuust\n"
    (werkmap / "eigen-regels.md").write_text(regels)
    nooit, wel = tells.eigen_regels()
    assert nooit == ["synergetisch"] and wel == ["robuust"]


def test_citaten_en_blokcitaten_tellen_niet():
    tekst = ('Hij schreef: "Dit is cruciaal en naadloos." Daarna gingen we verder met het plan.\n\n'
             '> In de huidige digitale wereld speelt AI een cruciale rol.\n')
    assert tells.analyseer(tekst, taal="nl")["punten"] == 0


def test_klinkt_als_ai_is_geen_chatbotrest():
    assert tells.analyseer("Een vage tekst klinkt als AI, en hij zegt ook minder.", taal="nl")["punten"] == 0
    assert tells.analyseer("Als taalmodel kan ik dat niet beoordelen.", taal="nl")["punten"] > 0


def test_leesbaarheid_gelijk_in_tells_en_leesbaarheid():
    from dutchquill import leesbaarheid, tekst
    md = ("---\ntitel: x\n---\n\n# Kop\n\nDit is een gewone zin met wat woorden erin. Nog een zin volgt hier.\n\n"
          "1. Open het programma en kies een map\n2. Klik op de knop om verder te gaan\n"
          "3. Sla je werk op voordat je het venster sluit\n\n"
          "Daarna kun je verder werken aan je tekst, zonder dat er iets verloren gaat.\n")
    assert tekst.statistiek(md, "nl")["flesch"] == leesbaarheid.flesch_douma(md)["score"]
    assert leesbaarheid.flesch_douma(md)["zinnen"] == 6


def test_rapport_in_het_engels_voor_engelse_tekst():
    from dutchquill import tells
    t = ("In today's digital world, artificial intelligence plays a crucial role in education. It is not just a "
         "tool, but a transformative force. In short, the future looks bright.")
    uit = tells.rapport(tells.analyseer(t, "en", "kort"))
    assert uit.startswith("Analysis: AI patterns HIGH") and "Broad opening without content" in uit
    assert "woorden" not in uit and "Brede aanloop" not in uit
    nl = tells.rapport(tells.analyseer("In de huidige digitale wereld speelt AI een cruciale rol.", "nl", "kort"))
    assert nl.startswith("Analyse: AI-patronen")
