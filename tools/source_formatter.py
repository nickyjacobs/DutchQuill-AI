#!/usr/bin/env python3
"""
tools/source_formatter.py — DutchQuill AI

Zet ruwe brondata om naar een correct opgemaakte APA 7e editie referentieregel (Nederlands).
Gebaseerd op apa_nl_gids.md (bron: Scribbr NL).

Gebruik:
    python3 tools/source_formatter.py --input bron.json
    python3 tools/source_formatter.py --input bronnen.json   (lijst van bronnen)
    python3 tools/source_formatter.py --help-schema          (toon JSON-voorbeelden)

Ondersteunde brontypen:
    boek, boek_hoofdstuk, tijdschriftartikel, webpagina, webpagina_geen_datum,
    rapport, scriptie, krant_online, youtube, podcast, wet, wikipedia,
    woordenboek_online, film, ted_talk

Uitvoer:
    - APA-referentieregel (literatuurlijst)
    - In-text citatie (parenthetisch + narratief)
"""

import sys
import json
import argparse
from typing import List, Dict


# ─────────────────────────────────────────────
# AUTEURS FORMATTERING
# ─────────────────────────────────────────────

def format_authors_ref(auteurs: List[str]) -> str:
    """
    Formatteer auteurslijst voor de literatuurlijst.
    Input: ["De Vries, J.", "Bakker, L."]
    Output: "De Vries, J., & Bakker, L."
    """
    if not auteurs:
        return ""
    if len(auteurs) == 1:
        return auteurs[0]
    elif len(auteurs) <= 20:
        return ", ".join(auteurs[:-1]) + ", & " + auteurs[-1]
    else:
        # 21+ auteurs: eerste 19, ellipsis, laatste
        return ", ".join(auteurs[:19]) + ", . . . " + auteurs[-1]


def get_last_names(auteurs: List[str]) -> List[str]:
    """Extraheer achternamen voor in-text citaties."""
    last_names = []
    for a in auteurs:
        # Formaat "Achternaam, V." — neem alles vóór de eerste komma
        last_names.append(a.split(",")[0].strip())
    return last_names


def intext_citation(auteurs: List[str], jaar: str, pagina: str = None) -> Dict:
    """Genereer in-text citatie (parenthetisch en narratief)."""
    last_names = get_last_names(auteurs) if auteurs else []
    jaar_str = jaar if jaar else "z.d."
    p_suffix = f", p. {pagina}" if pagina else ""

    if not last_names:
        parent = f"(z.a., {jaar_str}{p_suffix})"
        narrative = f"z.a. ({jaar_str})"
    elif len(last_names) == 1:
        parent = f"({last_names[0]}, {jaar_str}{p_suffix})"
        narrative = f"{last_names[0]} ({jaar_str})"
    elif len(last_names) == 2:
        parent = f"({last_names[0]} & {last_names[1]}, {jaar_str}{p_suffix})"
        narrative = f"{last_names[0]} en {last_names[1]} ({jaar_str})"
    else:
        parent = f"({last_names[0]} et al., {jaar_str}{p_suffix})"
        narrative = f"{last_names[0]} et al. ({jaar_str})"

    return {"parenthetisch": parent, "narratief": narrative}


def ital(text: str) -> str:
    """Markeer cursief met asterisken (markdown-conventie)."""
    return f"*{text}*"


# ─────────────────────────────────────────────
# FORMATTERINGSFUNCTIES PER BRONTYPE
# ─────────────────────────────────────────────

def fmt_boek(d: dict) -> str:
    auteurs = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    titel = d.get("titel", "")
    ondertitel = d.get("ondertitel", "")
    uitgever = d.get("uitgever", "")
    doi = d.get("doi", "")
    editie = d.get("editie", "")

    titel_full = ital(f"{titel}: {ondertitel}") if ondertitel else ital(titel)
    editie_str = f" ({editie} ed.)" if editie else ""

    ref = f"{auteurs} ({jaar}). {titel_full}{editie_str}. {uitgever}."
    if doi:
        ref += f" https://doi.org/{doi}"
    return ref


def fmt_boek_hoofdstuk(d: dict) -> str:
    auteurs = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    hoofdstuk_titel = d.get("hoofdstuk_titel", "")
    redacteuren = d.get("redacteuren", [])
    boek_titel = ital(d.get("boek_titel", ""))
    paginas = d.get("paginas", "")
    uitgever = d.get("uitgever", "")

    # Redacteuren: "V. Achternaam" formaat
    red_list = []
    for r in redacteuren:
        parts = r.split(",")
        if len(parts) >= 2:
            red_list.append(f"{parts[1].strip()} {parts[0].strip()}")
        else:
            red_list.append(r)

    if len(red_list) == 0:
        red_str = ""
    elif len(red_list) == 1:
        red_str = f"In {red_list[0]} (Red.)"
    elif len(red_list) == 2:
        red_str = f"In {red_list[0]} & {red_list[1]} (Reds.)"
    else:
        red_str = f"In {', '.join(red_list[:-1])} & {red_list[-1]} (Reds.)"

    paginas_str = f" (pp. {paginas})" if paginas else ""
    return f"{auteurs} ({jaar}). {hoofdstuk_titel}. {red_str}, {boek_titel}{paginas_str}. {uitgever}."


def fmt_tijdschriftartikel(d: dict) -> str:
    auteurs = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    artikel_titel = d.get("titel", "")
    tijdschrift = d.get("tijdschrift", "")
    volume = d.get("volume", "")
    nummer = d.get("nummer", "")
    paginas = d.get("paginas", "")
    doi = d.get("doi", "")

    volume_str = ital(volume) if volume else ""
    nummer_str = f"({nummer})" if nummer else ""
    paginas_str = f", {paginas}" if paginas else ""

    ref = f"{auteurs} ({jaar}). {artikel_titel}. {ital(tijdschrift)}, {volume_str}{nummer_str}{paginas_str}."
    if doi:
        ref += f" https://doi.org/{doi}"
    return ref


def fmt_webpagina(d: dict) -> str:
    auteurs = d.get("auteurs", [])
    auteur_str = format_authors_ref(auteurs) if auteurs else d.get("organisatie", "")
    jaar = d.get("jaar", "")
    datum = d.get("datum", "")
    titel = d.get("titel", "")
    website_naam = d.get("website_naam", "")
    url = d.get("url", "")

    jaar_datum = f"{jaar}, {datum}" if datum else jaar
    website_str = f" {website_naam}." if website_naam else ""
    return f"{auteur_str} ({jaar_datum}). {titel}.{website_str} {url}"


def fmt_webpagina_geen_datum(d: dict) -> str:
    auteurs = d.get("auteurs", [])
    auteur_str = format_authors_ref(auteurs) if auteurs else d.get("organisatie", "")
    titel = d.get("titel", "")
    raadpleegdatum = d.get("raadpleegdatum", "")
    url = d.get("url", "")
    return f"{auteur_str} (z.d.). {titel}. Geraadpleegd op {raadpleegdatum}, van {url}"


def fmt_rapport(d: dict) -> str:
    auteurs = d.get("auteurs", [])
    auteur_str = format_authors_ref(auteurs) if auteurs else d.get("organisatie", "")
    jaar = d.get("jaar", "z.d.")
    titel = ital(d.get("titel", ""))
    nummer = d.get("rapport_nummer", "")
    organisatie = d.get("organisatie", "")
    url = d.get("url", "")
    doi = d.get("doi", "")

    nummer_str = f" (Nr. {nummer})" if nummer else ""
    # Toon organisatienaam als uitgever alleen als er ook auteurs zijn
    org_str = f" {organisatie}." if organisatie and auteurs else ""

    ref = f"{auteur_str} ({jaar}). {titel}{nummer_str}.{org_str}"
    if doi:
        ref += f" https://doi.org/{doi}"
    elif url:
        ref += f" {url}"
    return ref


def fmt_scriptie(d: dict) -> str:
    auteurs = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    titel = ital(d.get("titel", ""))
    type_scriptie = d.get("type_scriptie", "Bachelorscriptie")
    instelling = d.get("instelling", "")
    url = d.get("url", "")
    database = d.get("database", "")

    bron = database if database else url
    return f"{auteurs} ({jaar}). {titel} [{type_scriptie}, {instelling}]. {bron}"


def fmt_krant_online(d: dict) -> str:
    auteurs = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    datum = d.get("datum", "")
    titel = d.get("titel", "")
    krant = d.get("krant", "")
    url = d.get("url", "")

    jaar_datum = f"{jaar}, {datum}" if datum else jaar
    return f"{auteurs} ({jaar_datum}). {titel}. {krant}. {url}"


def fmt_youtube(d: dict) -> str:
    auteurs = d.get("auteurs", [])
    auteur_str = format_authors_ref(auteurs) if auteurs else d.get("kanaal", "")
    jaar = d.get("jaar", "z.d.")
    datum = d.get("datum", "")
    titel = d.get("titel", "")
    url = d.get("url", "")

    jaar_datum = f"{jaar}, {datum}" if datum else jaar
    return f"{auteur_str} ({jaar_datum}). {titel} [Video]. YouTube. {url}"


def fmt_podcast(d: dict) -> str:
    host = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    datum = d.get("datum", "")
    aflevering_titel = d.get("aflevering_titel", "")
    nummer = d.get("nummer", "")
    podcast_naam = d.get("podcast_naam", "")
    producent = d.get("producent", "")
    url = d.get("url", "")

    jaar_datum = f"{jaar}, {datum}" if datum else jaar
    nummer_str = f" (Nr. {nummer})" if nummer else ""
    return (f"{host} (Host). ({jaar_datum}). {aflevering_titel}{nummer_str} "
            f"[Podcastaflevering]. In {podcast_naam}. {producent}. {url}")


def fmt_wet(d: dict) -> str:
    naam = d.get("naam", "")
    afkorting = d.get("afkorting", "")
    jaar = d.get("jaar", "z.d.")
    url = d.get("url", "")

    afk_str = f" [{afkorting}]" if afkorting else ""
    return f"{naam}{afk_str}. ({jaar}). {url}"


def fmt_wikipedia(d: dict) -> str:
    titel = d.get("titel", "")
    jaar = d.get("jaar", "z.d.")
    datum = d.get("datum", "")
    url = d.get("url", "")

    jaar_datum = f"{jaar}, {datum}" if datum else jaar
    return f"Wikipedia-bijdragers. ({jaar_datum}). {titel}. Wikipedia. {url}"


def fmt_woordenboek_online(d: dict) -> str:
    naam = d.get("naam", "")
    lemma = d.get("lemma", "")
    raadpleegdatum = d.get("raadpleegdatum", "")
    url = d.get("url", "")
    return f"{naam}. (z.d.). {lemma}. In {naam}. Geraadpleegd op {raadpleegdatum}, van {url}"


def fmt_film(d: dict) -> str:
    regisseur = d.get("regisseur", "")
    jaar = d.get("jaar", "z.d.")
    titel = ital(d.get("titel", ""))
    productiemaatschappij = d.get("productiemaatschappij", "")
    return f"{regisseur} (Regisseur). ({jaar}). {titel} [Film]. {productiemaatschappij}."


def fmt_ted_talk(d: dict) -> str:
    spreker = format_authors_ref(d.get("auteurs", []))
    jaar = d.get("jaar", "z.d.")
    maand = d.get("maand", "")
    titel = d.get("titel", "")
    raadpleegdatum = d.get("raadpleegdatum", "")
    url = d.get("url", "")

    jaar_maand = f"{jaar}, {maand}" if maand else jaar
    return (f"{spreker} ({jaar_maand}). {titel} [Video]. TED Conferences. "
            f"Geraadpleegd op {raadpleegdatum}, van {url}")


# ─────────────────────────────────────────────
# DISPATCHER
# ─────────────────────────────────────────────

FORMATTERS = {
    "boek": fmt_boek,
    "boek_hoofdstuk": fmt_boek_hoofdstuk,
    "tijdschriftartikel": fmt_tijdschriftartikel,
    "webpagina": fmt_webpagina,
    "webpagina_geen_datum": fmt_webpagina_geen_datum,
    "rapport": fmt_rapport,
    "scriptie": fmt_scriptie,
    "krant_online": fmt_krant_online,
    "youtube": fmt_youtube,
    "podcast": fmt_podcast,
    "wet": fmt_wet,
    "wikipedia": fmt_wikipedia,
    "woordenboek_online": fmt_woordenboek_online,
    "film": fmt_film,
    "ted_talk": fmt_ted_talk,
}

HELP_SCHEMA = """
Voorbeelden per brontype (minimale velden):

BOEK:
{
  "type": "boek",
  "auteurs": ["De Vries, J."],
  "jaar": "2020",
  "titel": "Duurzame bedrijfsvoering",
  "ondertitel": "Theorie en praktijk",
  "uitgever": "Boom Uitgevers"
}

TIJDSCHRIFTARTIKEL:
{
  "type": "tijdschriftartikel",
  "auteurs": ["Jansen, M.", "Bakker, L."],
  "jaar": "2022",
  "titel": "Klimaatadaptatie in stedelijke gebieden",
  "tijdschrift": "Planologisch Tijdschrift",
  "volume": "18",
  "nummer": "3",
  "paginas": "112-128",
  "doi": "10.1234/pt.2022.18.3.112"
}

WEBPAGINA:
{
  "type": "webpagina",
  "organisatie": "Rijksoverheid",
  "jaar": "2023",
  "datum": "15 maart",
  "titel": "Klimaatakkoord: Maatregelen voor de industrie",
  "website_naam": "Rijksoverheid",
  "url": "https://www.rijksoverheid.nl/..."
}

WEBPAGINA (geen datum):
{
  "type": "webpagina_geen_datum",
  "organisatie": "Scribbr",
  "titel": "Overzicht van onderzoeksmethoden",
  "raadpleegdatum": "1 maart 2024",
  "url": "https://www.scribbr.nl/..."
}

RAPPORT:
{
  "type": "rapport",
  "organisatie": "Nationaal Expertisecentrum Studentenwelzijn",
  "jaar": "2023",
  "titel": "Monitor studentenwelzijn 2023",
  "url": "https://..."
}

SCRIPTIE:
{
  "type": "scriptie",
  "auteurs": ["Achternaam, V."],
  "jaar": "2026",
  "titel": "Titel van de Scriptie",
  "type_scriptie": "Bachelorscriptie",
  "instelling": "Naam Instelling",
  "url": "https://..."
}

FILM:
{
  "type": "film",
  "regisseur": "Verhoeven, P.",
  "jaar": "1973",
  "titel": "Turks fruit",
  "productiemaatschappij": "Verenigde Nederlandsche Filmcompagnie"
}

Alle beschikbare typen:
  boek, boek_hoofdstuk, tijdschriftartikel, webpagina, webpagina_geen_datum,
  rapport, scriptie, krant_online, youtube, podcast, wet, wikipedia,
  woordenboek_online, film, ted_talk
"""


def format_source(data: dict) -> dict:
    """Formatteer één bron. Geeft dict met referentie en in-text citatie."""
    bron_type = data.get("type", "").lower()

    if bron_type not in FORMATTERS:
        beschikbaar = ", ".join(sorted(FORMATTERS.keys()))
        return {
            "error": (f"Onbekend brontype: '{bron_type}'. "
                      f"Beschikbare typen: {beschikbaar}. "
                      f"Gebruik --help-schema voor voorbeelden.")
        }

    reference = FORMATTERS[bron_type](data)

    # Bepaal auteurs voor in-text citatie
    auteurs = data.get("auteurs", [])
    if not auteurs:
        for fallback in ["organisatie", "naam", "kanaal", "regisseur"]:
            if data.get(fallback):
                auteurs = [data[fallback]]
                break
        else:
            if bron_type == "wikipedia":
                auteurs = ["Wikipedia-bijdragers"]

    citation = intext_citation(auteurs, data.get("jaar", "z.d."))

    return {
        "type": bron_type,
        "referentie": reference,
        "intext_parenthetisch": citation["parenthetisch"],
        "intext_narratief": citation["narratief"],
    }


def main():
    parser = argparse.ArgumentParser(
        description="Formatteer bronnen naar APA 7e editie (DutchQuill AI)"
    )
    parser.add_argument("--input", "-i",
                        help="JSON-bestand met bron of lijst van bronnen. Standaard: stdin.")
    parser.add_argument("--help-schema", action="store_true",
                        help="Toon JSON-voorbeelden per brontype")
    parser.add_argument("--json", action="store_true", help="Uitvoer als JSON")
    args = parser.parse_args()

    if args.help_schema:
        print(HELP_SCHEMA)
        return

    if args.input:
        try:
            with open(args.input, encoding="utf-8") as f:
                raw = json.load(f)
        except FileNotFoundError:
            print(f"Fout: Bestand niet gevonden — {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Fout: Ongeldige JSON — {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            raw = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Fout: Ongeldige JSON via stdin — {e}", file=sys.stderr)
            sys.exit(1)

    # Accepteer zowel een enkel object als een lijst
    sources = raw if isinstance(raw, list) else [raw]
    results = [format_source(s) for s in sources]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        lijn = "─" * 60
        for r in results:
            print(f"\n{lijn}")
            if "error" in r:
                print(f"✗ FOUT: {r['error']}")
            else:
                print(f"Type: {r['type']}")
                print(f"\nLiteratuurlijst:")
                print(f"  {r['referentie']}")
                print(f"\nIn-text (parenthetisch): {r['intext_parenthetisch']}")
                print(f"In-text (narratief):     {r['intext_narratief']}")
        print(f"\n{lijn}\n")


if __name__ == "__main__":
    main()
