#!/usr/bin/env python3
"""SessionStart-hook van DutchQuill AI. Alleen standaardbibliotheek, klaar in milliseconden.

1. Nog geen werkmap ingesteld en nog nooit gemeld: één keer "DutchQuill is nog niet ingesteld".
2. Referentiegidsen langer dan `herinnering_dagen` (standaard 30) niet gecontroleerd en deze periode nog
   niet gemeld: één melding met de opdracht /dutchquill:bijwerken. Ook als je hem negeert, komt de
   volgende pas na weer een volle periode.

Faalt nooit hard: bij elke fout stil afsluiten, zodat een sessie nooit last heeft van deze hook.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import date
from pathlib import Path


def _lees_json(pad: Path) -> dict:
    try:
        return json.loads(pad.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _datum(tekst: str | None) -> date | None:
    try:
        return date.fromisoformat(tekst) if tekst else None
    except ValueError:
        return None


def bepaal(root: Path, data: Path, vandaag: date) -> tuple[list[str], dict]:
    """Geef (meldingen, nieuwe status) terug. Los van IO-uitvoer, zodat het testbaar is."""
    status = _lees_json(data / "bijwerken.json")
    hookcfg = _lees_json(data / "hook.json")
    meldingen: list[str] = []

    if not (data / "werkmap").is_file() and not status.get("instellen_gemeld"):
        meldingen.append(
            "DutchQuill is nog niet ingesteld. Typ /dutchquill:instellen om je werkmap en voorkeuren te kiezen."
        )
        status["instellen_gemeld"] = vandaag.isoformat()

    dagen = int(hookcfg.get("herinnering_dagen") or 30)
    stand = _datum(_lees_json(root / "gidsen" / "stand.json").get("gecontroleerd"))
    eigen = _datum(status.get("laatst_gecontroleerd"))
    laatst = max([d for d in (stand, eigen) if d], default=None)
    gemeld = _datum(status.get("laatst_gemeld"))
    if laatst and (vandaag - laatst).days >= dagen and (not gemeld or (vandaag - gemeld).days >= dagen):
        meldingen.append(
            f"DutchQuill: de referentiegidsen (APA, taal, humaniseren) zijn {(vandaag - laatst).days} dagen niet "
            "gecontroleerd. Typ /dutchquill:bijwerken om te kijken of de bronnen veranderd zijn."
        )
        status["laatst_gemeld"] = vandaag.isoformat()
    return meldingen, status


def main() -> None:
    try:
        invoer = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    except Exception:
        invoer = {}
    if invoer.get("source", "startup") != "startup":
        return
    root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).resolve().parents[1]))
    data_env = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not data_env:
        return
    data = Path(data_env)
    data.mkdir(parents=True, exist_ok=True)

    meldingen, status = bepaal(root, data, date.today())
    if not meldingen:
        return
    (data / "bijwerken.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    uit = {
        "systemMessage": "\n".join(meldingen),
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": (
                "Melding van de DutchQuill-plugin aan de gebruiker (al getoond): " + " ".join(meldingen)
                + " Breng dit alleen ter sprake als het gesprek over schrijven gaat; dring niet aan."
            ),
        },
    }
    print(json.dumps(uit, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
