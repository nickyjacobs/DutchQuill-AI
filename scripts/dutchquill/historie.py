"""Logboek van wat DutchQuill maakte, in <werkmap>/.dutchquill/historie.jsonl (één JSON-regel per actie).

Bewaart paden en metadata, geen volledige teksten.

  dq historie log --actie schrijven --titel "Mijn rapport" [--bestand pad ...] [--meta '{"genre":"rapport"}']
  dq historie toon [--n 10]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dutchquill.config import ConfigFout, effectief

ACTIES = ("schrijven", "herschrijven", "reviewen", "humaniseren", "instellen", "bijwerken")


def _pad() -> Path:
    e = effectief()
    if not e["ingesteld"]:
        raise ConfigFout("Nog geen werkmap ingesteld.")
    p = Path(e["mappen"]["intern"]) / "historie.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def log(actie: str, titel: str, bestanden: list[str], meta: dict) -> dict:
    regel = {
        "tijd": datetime.now().astimezone().isoformat(timespec="seconds"),
        "actie": actie,
        "titel": titel,
        "bestanden": bestanden,
        "meta": meta,
    }
    with _pad().open("a", encoding="utf-8") as f:
        f.write(json.dumps(regel, ensure_ascii=False) + "\n")
    return regel


def toon(n: int = 10) -> list[dict]:
    p = _pad()
    if not p.is_file():
        return []
    regels = [json.loads(r) for r in p.read_text(encoding="utf-8").splitlines() if r.strip()]
    return regels[-n:]


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq historie", description="Logboek van DutchQuill-acties")
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("--actie", required=True, choices=ACTIES)
    lg.add_argument("--titel", required=True)
    lg.add_argument("--bestand", action="append", default=[])
    lg.add_argument("--meta", default="{}")
    sub.add_parser("toon").add_argument("--n", type=int, default=10)
    a = p.parse_args(argv)
    try:
        if a.cmd == "log":
            try:
                meta = json.loads(a.meta)
            except json.JSONDecodeError as e:
                raise ConfigFout(f"--meta is geen geldige JSON: {e}") from e
            log(a.actie, a.titel, a.bestand, meta)
            print("Opgeslagen in de historie.")
        else:
            print(json.dumps(toon(a.n), ensure_ascii=False, indent=2))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
