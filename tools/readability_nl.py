#!/usr/bin/env python3
"""
tools/readability_nl.py — DutchQuill AI

Berekent de leesbaarheidsindex van Nederlandse tekst met de Flesch-Douma formule.
Geeft een score en interpretatie specifiek voor HBO-academische tekst.

Flesch-Douma formule (Nederlandse standaard):
    Score = 206.835 − 0.93 × (woorden / zinnen) − 77 × (lettergrepen / woorden)

Interpretatie voor HBO-tekst:
    0–30   Zeer moeilijk — wetenschappelijk niveau
    30–50  Moeilijk      — ✓ geschikt voor HBO
    50–65  Redelijk      — ⚠ bovengrens HBO
    65–80  Standaard     — ✗ te eenvoudig voor HBO
    80+    Eenvoudig     — ✗ niet geschikt voor academisch

Gebruik:
    python3 tools/readability_nl.py --input rapport.txt
    python3 tools/readability_nl.py --compare origineel.txt herschreven.txt
    cat rapport.txt | python3 tools/readability_nl.py
    python3 tools/readability_nl.py --input rapport.txt --json
"""

import sys
import re
import json
import argparse
from typing import Tuple, Dict, List

# Nederlandse klinkergroepen voor lettergreeptellerlogica
# Langere combinaties eerst zodat "ui" niet als twee klinkers telt
NL_VOWEL_PATTERN = re.compile(
    r'ui|eu|au|ou|ei|ij|oe|aa|ee|oo|uu|ie'
    r'|[aeiouáéíóúàèìòùäëïöü]',
    re.IGNORECASE
)

# Afkortingen die geen zinseinde markeren (punt gevolgd door komma = niet einde)
ABBREVIATION_PATTERN = re.compile(
    r'\b(?:dr|drs|mr|ir|prof|ing|dhr|mw|jr|sr|ca|bijv|resp|etc|vs|nr|'
    r'art|par|p|pp|red|reds|ed|eds|vol|fig|tab)\.',
    re.IGNORECASE
)


def count_syllables(word: str) -> int:
    """
    Tel lettergrepen in een Nederlands woord via klinkergroepen.
    Elke klinkergroep = één lettergreep; minimum 1 lettergreep per woord.
    """
    clean = re.sub(r'[^a-zA-Záéíóúàèìòùäëïöü]', '', word)
    if not clean:
        return 0
    count = len(NL_VOWEL_PATTERN.findall(clean))
    return max(1, count)


def split_sentences(text: str) -> List[str]:
    """
    Splits tekst in zinnen.
    Negeert punten in afkortingen en URLs.
    """
    # Vervang URLs tijdelijk
    text_clean = re.sub(r'https?://\S+', 'URL', text)
    # Vervang afkortingen tijdelijk (punt → speciaal teken)
    text_clean = ABBREVIATION_PATTERN.sub(lambda m: m.group(0).replace('.', '\x00'), text_clean)

    # Splits op punt/uitroep/vraagteken gevolgd door spatie + hoofdletter
    raw = re.split(r'(?<=[.!?])\s+(?=[A-Z\u201c\u201e"\d])', text_clean)

    sentences = []
    for s in raw:
        s = s.replace('\x00', '.').strip()
        if s and len(s.split()) >= 2:
            sentences.append(s)

    return sentences


def split_words(text: str) -> List[str]:
    """Extraheer woorden (min. 2 tekens, alleen letters)."""
    return [w for w in re.findall(r'\b[a-zA-Záéíóúàèìòùäëïöü]+\b', text) if len(w) >= 2]


def flesch_douma(text: str) -> Dict:
    """
    Berekent Flesch-Douma score.
    Retourneert dict met score en alle tussenstappen.
    """
    sentences = split_sentences(text)
    words = split_words(text)

    n_sentences = max(len(sentences), 1)
    n_words = max(len(words), 1)
    n_syllables = sum(count_syllables(w) for w in words)

    asl = n_words / n_sentences       # Gemiddelde zinslengte
    asw = n_syllables / n_words        # Gemiddeld lettergrepen per woord

    raw_score = 206.835 - (0.93 * asl) - (77 * asw)
    score = round(max(0.0, min(100.0, raw_score)), 1)

    return {
        "score": score,
        "zinnen": n_sentences,
        "woorden": n_words,
        "lettergrepen": n_syllables,
        "gemiddelde_zinslengte": round(asl, 1),
        "gemiddelde_lettergrepen_per_woord": round(asw, 2),
    }


def interpret_score(score: float, gem_lettergrepen: float = 0.0) -> Tuple[str, str, str]:
    """
    Geeft (niveau, hbo_beoordeling, aanbeveling) op basis van score.
    gem_lettergrepen: gemiddeld aantal lettergrepen per woord — bij >= 2.2 en lage score
    is de oorzaak waarschijnlijk domeinspecifiek woordgebruik, niet slechte zinsbouw.
    """
    if score < 30:
        if gem_lettergrepen >= 2.2:
            aanbeveling = (
                "Lage score is vermoedelijk domeinspecifiek: technische vaktermen "
                "hebben van nature veel lettergrepen. Controleer of de zinsbouw helder "
                "is — dat weegt zwaarder dan de Flesch-Douma score in dit domein."
            )
        else:
            aanbeveling = (
                "Zinnen zijn waarschijnlijk te lang of het woordgebruik te technisch. "
                "Overweeg kortere zinnen."
            )
        return (
            "Zeer moeilijk",
            "Wetenschappelijk niveau — mogelijk te complex voor HBO",
            aanbeveling
        )
    elif score < 50:
        return (
            "Moeilijk",
            "✓ Geschikt voor HBO-niveau",
            "Leesbaarheid is goed voor academische tekst op HBO-niveau."
        )
    elif score < 65:
        return (
            "Redelijk moeilijk",
            "⚠ Bovengrens van HBO — iets te eenvoudig",
            "Overweeg langere zinnen of meer vaktaal te gebruiken."
        )
    elif score < 80:
        return (
            "Standaard",
            "✗ Te eenvoudig voor HBO-academisch",
            "Gebruik meer academische zinsstructuren en vaktermen."
        )
    else:
        return (
            "Eenvoudig",
            "✗ Niet geschikt voor academische tekst",
            "Tekst is te eenvoudig. Verhoog het academische niveau aanzienlijk."
        )


def print_report(stats: Dict, label: str = "Analyse") -> None:
    niveau, hbo, aanbeveling = interpret_score(
        stats["score"], stats.get("gemiddelde_lettergrepen_per_woord", 0.0)
    )
    lijn = "═" * 60
    lijn2 = "─" * 60

    print(f"\n{lijn}")
    print(f"  LEESBAARHEIDSRAPPORT — {label}")
    print(lijn)
    print(f"  Flesch-Douma Score:  {stats['score']} / 100")
    print(f"  Niveau:              {niveau}")
    print(f"  HBO-beoordeling:     {hbo}")
    print(lijn2)
    print(f"  Zinnen:              {stats['zinnen']}")
    print(f"  Woorden:             {stats['woorden']}")
    print(f"  Lettergrepen:        {stats['lettergrepen']}")
    print(f"  Gem. zinslengte:     {stats['gemiddelde_zinslengte']} woorden/zin")
    print(f"  Gem. lettergrepen:   {stats['gemiddelde_lettergrepen_per_woord']} per woord")
    print(lijn2)
    print(f"  Aanbeveling:  {aanbeveling}")
    print(f"{lijn}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Bereken Flesch-Douma leesbaarheidsindex voor Nederlands (DutchQuill AI)"
    )
    parser.add_argument("--input", "-i", help="Invoerbestand. Standaard: stdin.")
    parser.add_argument(
        "--compare", nargs=2, metavar=("ORIGINEEL", "HERSCHREVEN"),
        help="Vergelijk leesbaarheid van twee bestanden"
    )
    parser.add_argument("--json", action="store_true", help="Uitvoer als JSON")
    args = parser.parse_args()

    if args.compare:
        try:
            with open(args.compare[0], encoding="utf-8") as f:
                text_a = f.read()
            with open(args.compare[1], encoding="utf-8") as f:
                text_b = f.read()
        except FileNotFoundError as e:
            print(f"Fout: Bestand niet gevonden — {e}", file=sys.stderr)
            sys.exit(1)

        stats_a = flesch_douma(text_a)
        stats_b = flesch_douma(text_b)

        if args.json:
            print(json.dumps(
                {"origineel": stats_a, "herschreven": stats_b},
                ensure_ascii=False, indent=2
            ))
        else:
            print_report(stats_a, "ORIGINEEL")
            print_report(stats_b, "HERSCHREVEN")
            delta = round(stats_b["score"] - stats_a["score"], 1)
            sign = "+" if delta > 0 else ""
            niveau_a = interpret_score(stats_a["score"])[0]
            niveau_b = interpret_score(stats_b["score"])[0]
            print(f"  DELTA: {sign}{delta} punten  ({niveau_a} → {niveau_b})\n")

    else:
        if args.input:
            try:
                with open(args.input, encoding="utf-8") as f:
                    text = f.read()
            except FileNotFoundError:
                print(f"Fout: Bestand niet gevonden — {args.input}", file=sys.stderr)
                sys.exit(1)
        else:
            text = sys.stdin.read()

        if not text.strip():
            print("Fout: Lege invoer.", file=sys.stderr)
            sys.exit(1)

        stats = flesch_douma(text)

        if args.json:
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        else:
            print_report(stats)


if __name__ == "__main__":
    main()
