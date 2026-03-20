#!/usr/bin/env python3
"""
.claude/hooks/check_verboden_woorden.py — DutchQuill AI

Stop-hook: controleert of de laatste assistent-boodschap verboden woorden bevat
die zijn opgesomd in CLAUDE.md. Wordt automatisch uitgevoerd na elke Claude-respons.

Exit-codes:
    0 — geen verboden woorden gevonden, geen actie nodig
    2 — verboden woorden gevonden; feedback gaat naar Claude zodat het herschrijft
"""

import sys
import json
import re

VERBODEN_WOORDEN = [
    "cruciaal",
    "essentieel",
    "robuust",
    "baanbrekend",
    "naadloos",
    "transformatief",
    "katalysator",
    "speerpunt",
    "faciliteert",
    "demonstreert",
    "onderstreept",
    "weerspiegelt",
    "stroomlijnen",
    "duiken in",
    "scala aan",
    "betekenisvol",
    "diepgaand",
    "genuanceerd",
    "uitgebreid",
    "proactief",
    "integraal",
    "zodoende",
    "passie",
    "verheugd",
    "fosteren",
    "testament aan",
]

# Verboden openingszinnen (begin van zin)
VERBODEN_OPENERS = [
    "in de huidige samenleving",
    "in een wereld waar",
    "in het huidige tijdperk",
    "het is belangrijk om te benadrukken",
    "in het kader van",
    "het is belangrijker dan ooit",
]


def extract_last_assistant_text(data: dict) -> str:
    """
    Haal de tekstinhoud op van de laatste assistent-boodschap.
    Slaat tool_use en tool_result blokken over — die zijn geen gegenereerde tekst.
    """
    conversation = data.get("conversation", [])

    # Loop achterstevoren om de laatste assistant-turn te vinden
    for msg in reversed(conversation):
        if msg.get("role") != "assistant":
            continue

        content = msg.get("content", "")

        # String-content: direct teruggeven
        if isinstance(content, str):
            return content

        # Lijst-content: alleen text-blokken samenvoegen
        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
            return "\n".join(parts)

    return ""


def strip_code_blocks(text: str) -> str:
    """Verwijder code-blokken en inline code zodat die niet mee-checken."""
    # Verwijder fenced code blocks (``` ... ```)
    text = re.sub(r"```[\s\S]*?```", "", text)
    # Verwijder inline code (`...`)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def check_verboden(text: str) -> list[str]:
    """
    Controleer tekst op verboden woorden en openers.
    Retourneert lijst van gevonden overtredingen.
    """
    if not text.strip():
        return []

    # Verwijder code-blokken vóór de check
    clean = strip_code_blocks(text).lower()
    gevonden = []

    for woord in VERBODEN_WOORDEN:
        # Gebruik word-boundary voor enkelvoudige woorden, partial match voor zinsdelen
        if " " in woord:
            if woord in clean:
                gevonden.append(f'"{woord}"')
        else:
            pattern = r"\b" + re.escape(woord) + r"\b"
            if re.search(pattern, clean):
                gevonden.append(f'"{woord}"')

    for opener in VERBODEN_OPENERS:
        if opener in clean:
            gevonden.append(f'opener: "{opener}..."')

    return gevonden


def main():
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            sys.exit(0)
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        # Bij parse-fouten: niet blokkeren, gewoon doorgaan
        sys.exit(0)

    tekst = extract_last_assistant_text(data)

    # Alleen checken als er substantiële Nederlandse tekst is (> 100 tekens)
    if len(tekst.strip()) < 100:
        sys.exit(0)

    gevonden = check_verboden(tekst)

    if gevonden:
        overtredingen = ", ".join(gevonden)
        print(
            f"VERBODEN WOORDEN GEVONDEN: {overtredingen}\n"
            f"Herschrijf de betreffende passage(s) zonder deze woorden. "
            f"Zie CLAUDE.md § Schrijfstijl voor de volledige lijst en alternatieven.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
