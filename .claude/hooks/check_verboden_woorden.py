#!/usr/bin/env python3
"""
.claude/hooks/check_verboden_woorden.py — DutchQuill AI

Stop-hook: controleert of de laatste assistent-boodschap verboden woorden bevat
die zijn opgesomd in .claude/rules/schrijfstijl.md. Wordt automatisch uitgevoerd
na elke Claude-respons.

De woorden worden dynamisch geladen uit schrijfstijl.md zodat er één bron van
waarheid is. Als het bestand niet gelezen kan worden, valt de hook terug op een
ingebouwde kopie.

Exit-codes:
    0 — geen verboden woorden gevonden, geen actie nodig
    2 — verboden woorden gevonden; feedback gaat naar Claude zodat het herschrijft
"""

from __future__ import annotations

import sys
import json
import re
import os

# --- Dynamisch laden uit schrijfstijl.md ---

def _find_schrijfstijl() -> str | None:
    """Zoek schrijfstijl.md relatief ten opzichte van dit script."""
    hook_dir = os.path.dirname(os.path.abspath(__file__))
    # .claude/hooks/ → .claude/rules/schrijfstijl.md
    candidate = os.path.join(hook_dir, "..", "rules", "schrijfstijl.md")
    candidate = os.path.normpath(candidate)
    if os.path.isfile(candidate):
        return candidate
    # Fallback: probeer via CLAUDE_PROJECT_DIR
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    if project_dir:
        candidate = os.path.join(project_dir, ".claude", "rules", "schrijfstijl.md")
        if os.path.isfile(candidate):
            return candidate
    return None


def _parse_schrijfstijl(path: str) -> tuple[list[str], list[str]]:
    """
    Parse schrijfstijl.md en extraheer verboden woorden en openers.

    Verwacht format:
      ## Verboden woorden (NOOIT gebruiken)
      woord1, woord2, woord3, ...

      ## Verboden zinsopeners (NOOIT zo beginnen)
      - "In de huidige samenleving..."
      - "In een wereld waar..."
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    woorden: list[str] = []
    openers: list[str] = []

    # Verboden woorden: alles tussen de woorden-header en de volgende ##
    woorden_match = re.search(
        r"## Verboden woorden.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if woorden_match:
        block = woorden_match.group(1).strip()
        # Komma-gescheiden lijst op één of meerdere regels
        for item in re.split(r",\s*", block):
            item = item.strip().strip('"').strip("'")
            if item:
                woorden.append(item.lower())

    # Verboden openers: bullet-list met aanhalingstekens
    openers_match = re.search(
        r"## Verboden zinsopeners.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if openers_match:
        block = openers_match.group(1).strip()
        for line in block.splitlines():
            line = line.strip().lstrip("- ").strip()
            # Extraheer tekst uit aanhalingstekens, zonder trailing ...
            m = re.match(r'"([^"]+?)\.{0,3}"', line)
            if m:
                openers.append(m.group(1).lower().rstrip("."))

    return woorden, openers


# Ingebouwde fallback (voor het geval schrijfstijl.md niet gevonden wordt)
_FALLBACK_WOORDEN = [
    "cruciaal", "essentieel", "robuust", "baanbrekend", "naadloos",
    "transformatief", "katalysator", "speerpunt", "faciliteert", "demonstreert",
    "onderstreept", "weerspiegelt", "stroomlijnen", "duiken in", "scala aan",
    "betekenisvol", "diepgaand", "genuanceerd", "uitgebreid", "proactief",
    "integraal", "zodoende", "passie", "verheugd", "fosteren", "testament aan",
]
_FALLBACK_OPENERS = [
    "in de huidige samenleving", "in een wereld waar", "in het huidige tijdperk",
    "het is belangrijk om te benadrukken", "in het kader van",
    "het is belangrijker dan ooit",
]


def load_verboden() -> tuple[list[str], list[str]]:
    """Laad verboden woorden en openers. Dynamisch als mogelijk, anders fallback."""
    path = _find_schrijfstijl()
    if path:
        try:
            woorden, openers = _parse_schrijfstijl(path)
            if woorden:  # Minimale sanity check
                return woorden, openers
        except Exception:
            pass
    return _FALLBACK_WOORDEN, _FALLBACK_OPENERS


# --- Bestaande logica ---

def extract_last_assistant_text(data: dict) -> str:
    """
    Haal de tekstinhoud op van de laatste assistent-boodschap.
    Slaat tool_use en tool_result blokken over — die zijn geen gegenereerde tekst.
    """
    conversation = data.get("conversation", [])

    for msg in reversed(conversation):
        if msg.get("role") != "assistant":
            continue

        content = msg.get("content", "")

        if isinstance(content, str):
            return content

        if isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
            return "\n".join(parts)

    return ""


def strip_code_blocks(text: str) -> str:
    """Verwijder code-blokken en inline code zodat die niet mee-checken."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def check_verboden(text: str, woorden: list[str], openers: list[str]) -> list[str]:
    """
    Controleer tekst op verboden woorden en openers.
    Retourneert lijst van gevonden overtredingen.
    """
    if not text.strip():
        return []

    clean = strip_code_blocks(text).lower()
    gevonden = []

    for woord in woorden:
        if " " in woord:
            if woord in clean:
                gevonden.append(f'"{woord}"')
        else:
            pattern = r"\b" + re.escape(woord) + r"\b"
            if re.search(pattern, clean):
                gevonden.append(f'"{woord}"')

    for opener in openers:
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
        sys.exit(0)

    tekst = extract_last_assistant_text(data)

    # Alleen checken als er substantiële Nederlandse tekst is (> 100 tekens)
    if len(tekst.strip()) < 100:
        sys.exit(0)

    woorden, openers = load_verboden()
    gevonden = check_verboden(tekst, woorden, openers)

    if gevonden:
        overtredingen = ", ".join(gevonden)
        print(
            f"VERBODEN WOORDEN GEVONDEN: {overtredingen}\n"
            f"Herschrijf de betreffende passage(s) zonder deze woorden. "
            f"Zie .claude/rules/schrijfstijl.md voor de volledige lijst en alternatieven.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
