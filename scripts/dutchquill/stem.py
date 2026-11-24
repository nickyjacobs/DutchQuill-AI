"""Het stemprofiel van de schrijver, gemeten aan de eigen teksten in de map mijn-stijl.

  dq stem analyse [--map <map>]      # schrijft <werkmap>/.dutchquill/stem.json
  dq stem toon

dq tells gebruikt dit profiel: wat de schrijver zelf vaak doet (streepjes, korte zinnen, dubbele punten),
telt dan niet als AI-patroon. De subagent stem-analist maakt er daarnaast een leesbaar stemprofiel.md van.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

from dutchquill import extraheer as ext
from dutchquill import tekst as tk
from dutchquill.config import ConfigFout, effectief


def _teksten(map_: Path) -> list[tuple[str, str]]:
    uit = []
    for f in sorted(map_.rglob("*")):
        if not f.is_file() or f.name.startswith(".") or ext.soort(f) not in ("tekst", "document", "pdf", "web"):
            continue
        try:
            if f.suffix.lower() == ".docx":
                from dutchquill.docx_tekst import extract_text
                t = extract_text(str(f))
            elif f.suffix.lower() == ".pdf":
                t = ext._pdf(f, None)["tekst"]
            elif ext.soort(f) == "web":
                t = ext._html(f)["tekst"]
            else:
                t = ext._tekst(f)["tekst"]
        except Exception:
            continue
        if len(tk.woorden(t)) >= 40:
            uit.append((f.name, t))
    return uit


def analyse(map_: Path | None = None) -> dict:
    e = effectief()
    if not e["ingesteld"] and map_ is None:
        raise ConfigFout("Nog geen werkmap ingesteld. Draai eerst /dutchquill:instellen.")
    map_ = map_ or Path(e["mappen"]["mijn_stijl"])
    teksten = _teksten(map_)
    if not teksten:
        raise ConfigFout(f"Geen bruikbare eigen teksten in {map_} (minstens 40 woorden per tekst).")
    samen = "\n\n".join(t for _, t in teksten)
    stat = tk.statistiek(samen)
    profiel = {"gemeten": date.today().isoformat(), "bestanden": [n for n, _ in teksten], **stat}
    if e["ingesteld"]:
        doel = Path(e["mappen"]["intern"]) / "stem.json"
        doel.parent.mkdir(parents=True, exist_ok=True)
        doel.write_text(json.dumps(profiel, ensure_ascii=False, indent=2), encoding="utf-8")
        profiel["opgeslagen"] = str(doel)
    return profiel


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq stem", description="Stemprofiel uit eigen teksten")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("analyse").add_argument("--map")
    sub.add_parser("toon")
    a = p.parse_args(argv)
    try:
        if a.cmd == "analyse":
            print(json.dumps(analyse(Path(a.map) if a.map else None), ensure_ascii=False, indent=2))
        else:
            pad = Path(effectief()["mappen"].get("intern", "")) / "stem.json"
            print(pad.read_text(encoding="utf-8") if pad.is_file() else "Nog geen stemprofiel: dq stem analyse")
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
