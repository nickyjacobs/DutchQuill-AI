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


def test_html_in_readme_telt_niet_als_tekst():
    from dutchquill import tekst
    md = '<p align="center"><img src="a.png" alt="x"></p>\n\n<p align="center"><b>Schrijven in Claude Code.</b></p>\n'
    rs = [r for r in tekst.regels(md) if r.soort != "leeg"]
    assert [r.tekst for r in rs] == ["Schrijven in Claude Code."]


def test_vervolgregel_hoort_bij_opsommingspunt():
    from dutchquill import tekst
    md = "- Eerste punt dat over twee regels\n  doorloopt tot hier.\n- Tweede punt.\n\nGewone alinea.\n"
    rs = [r for r in tekst.regels(md) if r.soort != "leeg"]
    assert [(r.soort, r.tekst) for r in rs] == [("lijst", "Eerste punt dat over twee regels doorloopt tot hier."),
                                                 ("lijst", "Tweede punt."), ("proza", "Gewone alinea.")]


# ---- terug uit v1: Oxford-komma, gestapelde bijvoeglijke naamwoorden, niveau 3, leesbaarheid, korte tekst

def test_oxford_komma_alleen_nederlands():
    r = tells.analyseer("We kochten appels, peren, en bananen voor de kantine van het nieuwe kantoor.", taal="nl")
    assert "oxford_komma" in r["per_categorie"]
    r = tells.analyseer("We kochten appels, peren en bananen voor de kantine van het nieuwe kantoor.", taal="nl")
    assert "oxford_komma" not in r["per_categorie"]
    r = tells.analyseer("We bought apples, pears, and bananas for the canteen of the new office.", taal="en")
    assert "oxford_komma" not in r["per_categorie"]


def test_oxford_komma_niet_in_citaat():
    r = tells.analyseer('Hij schreef: "appels, peren, en bananen" en ging daarna naar huis.', taal="nl")
    assert "oxford_komma" not in r["per_categorie"]


def test_gestapelde_bijvoeglijke_naamwoorden():
    r = tells.analyseer("Dit is een innovatief, baanbrekend en duurzaam project voor de hele regio.", taal="nl")
    assert "bijvoeglijk_stapel" in r["per_categorie"]
    r = tells.analyseer("We spraken met de klanten, collega's en partners over het nieuwe plan.", taal="nl")
    assert "bijvoeglijk_stapel" not in r["per_categorie"]
    r = tells.analyseer("It is a robust, scalable and innovative platform for teams of every size.", taal="en")
    assert "bijvoeglijk_stapel" in r["per_categorie"]


def test_niveau3_dichtheid():
    zin = "Het belangrijke punt is dat dit een effectief en uniek plan is voor ons team. "
    vul = "We bespreken het plan morgen met de afdeling en maken dan een keuze over de planning. "
    r = tells.analyseer((zin + vul) * 4, taal="nl")
    b = [b for b in r["bevindingen"] if b["cat"] == "niveau3_dichtheid"]
    assert b and b[0]["punten"] == 1 and "belangrijke" in b[0]["context"]
    r = tells.analyseer(zin + vul * 8, taal="nl")
    assert "niveau3_dichtheid" not in r["per_categorie"]


def test_lage_leesbaarheid_telt_bij_rapport():
    tekst = lees("rapport_moeilijk_nl.md")
    r = tells.analyseer(tekst, taal="nl", genre="rapport")
    assert r["statistiek"]["flesch"] < 30
    assert "leesbaarheid" in r["per_categorie"] and r["niveau"] != "laag", tells.rapport(r)
    assert r["acceptatie"] and not r["acceptatie"]["voldaan"]
    assert any("Flesch" in t for t in r["acceptatie"]["tekort"])
    mail = tells.analyseer(tekst, taal="nl", genre="mail")
    assert "leesbaarheid" not in mail["per_categorie"] and mail["acceptatie"] is None


def test_technisch_rapport_eigen_drempels():
    tekst = lees("rapport_moeilijk_nl.md")
    r = tells.analyseer(tekst, taal="nl", genre="technisch-rapport")
    assert r["drempels"]["groep"] == "technisch" and r["drempels"]["laag_onder"] == 6
    assert r["acceptatie"]["eisen"]["flesch_min"] == 25 and r["acceptatie"]["eisen"]["mattr_min"] == 0.70
    assert tells.groep("rapport") == "streng" and tells.groep("mail") == "los"


def test_bovengrens_leesbaarheid_alleen_academisch():
    tekst = lees("mens_nl.md")
    assert any("tot 50" in t for t in tells.analyseer(tekst, genre="rapport")["acceptatie"]["tekort"])
    assert tells.analyseer(tekst, genre="zakelijk-rapport")["acceptatie"]["voldaan"]


def test_korte_tekst_waarschuwt():
    r = tells.analyseer("Hoi Sam, morgen om tien uur past prima. Tot dan!", taal="nl", genre="mail")
    assert r["waarschuwingen"] and "Korte tekst" in r["waarschuwingen"][0]
    assert "Let op: Korte tekst" in tells.rapport(r)
    r = tells.analyseer("Hi Sam, ten tomorrow works fine. See you then!", taal="en", genre="mail")
    assert "Note: Short text" in tells.rapport(r)
    assert not tells.analyseer(lees("mens_nl.md"))["waarschuwingen"]


# ---- testronde 2.1: harde regelafbrekingen, labels, technische koppen

def test_patroon_over_regelafbreking():
    tekst = ("Organisaties zoeken naar een snelle,\nveilige en duurzame aanpak. Het gaat niet alleen om\n"
             "techniek, maar om mensen.")
    r = tells.analyseer(tekst, "nl")
    stapel = [b for b in r["bevindingen"] if b["cat"] == "bijvoeglijk_stapel"]
    assert stapel and stapel[0]["regel"] == 1
    par = [b for b in r["bevindingen"] if b["cat"] == "niet_x_maar_y"]
    assert par and par[0]["regel"] == 2


def test_geen_dubbele_treffer_over_regelafbreking():
    r = tells.analyseer("Er is een breed\nscala aan opties voor de klant om uit te kiezen vandaag.", "nl")
    assert [b["match"].lower() for b in r["bevindingen"] if b["cat"] == "woord"] == ["een breed scala aan"]


def test_lijsten_en_koppen_blijven_los():
    tekst = "# Een snelle,\n\n- veilige en duurzame aanpak voor iedereen"
    assert "bijvoeglijk_stapel" not in tells.analyseer(tekst, "nl")["per_categorie"]


def test_label_aan_alineabegin_telt_niet():
    alineas = [f"Advies: zet onderdeel {i} uit via GPO en controleer het daarna." for i in range(3)]
    tekst = "\n\n".join(["Dit is de inleiding van het stuk."] + alineas)
    assert "alineabegin" not in tells.analyseer(tekst, "nl")["per_categorie"]
    zonder = "\n\n".join(["Dit is de inleiding."] + [a.replace("Advies:", "Daarom") for a in alineas])
    assert "alineabegin" in tells.analyseer(zonder, "nl")["per_categorie"]


def test_title_case_negeert_namen_en_technische_teksten():
    assert "title_case" not in tells.analyseer("## Inzet van PowerShell via DCSync\n\nTekst.", "nl")["per_categorie"]
    kop = "## Bevinding via Backup Operators\n\nTekst hier."
    assert "title_case" in tells.analyseer(kop, "nl", genre="rapport")["per_categorie"]
    assert "title_case" not in tells.analyseer(kop, "nl", genre="technisch-rapport")["per_categorie"]
