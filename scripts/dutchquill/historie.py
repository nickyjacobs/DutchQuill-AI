"""Logboek van wat DutchQuill maakte, in <werkmap>/.dutchquill/historie.jsonl (één JSON-regel per actie).

Elke regel heeft de tijd, de actie, de titel, de paden en wat metadata. Met --tekst komt er ook een kopie van de
tekst bij, in <werkmap>/.dutchquill/historie/, zodat ook een scan of een tekst die alleen in de chat kwam terug te
vinden is. Dat kan uit met `historie.tekst_bewaren: false`; dan blijven alleen titel, datum en paden.

  dq historie log --actie schrijven --titel "Mijn rapport" [--bestand pad ...] [--tekst pad|-] [--meta '{...}']
  dq historie toon [--n 10]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from dutchquill.config import ConfigFout, effectief

ACTIES = ("schrijven", "herschrijven", "reviewen", "humaniseren", "instellen", "bijwerken")
MAX_TEKST = 2_000_000  # tekens; een historiekopie is voor teksten, niet voor hele boeken


def _intern() -> tuple[Path, dict]:
    e = effectief()
    if not e["ingesteld"]:
        raise ConfigFout("Nog geen werkmap ingesteld.")
    p = Path(e["mappen"]["intern"])
    p.mkdir(parents=True, exist_ok=True)
    return p, e


def _pad() -> Path:
    return _intern()[0] / "historie.jsonl"


def _slug(titel: str) -> str:
    s = re.sub(r"[^\w\-]+", "-", titel.lower(), flags=re.UNICODE).strip("-")
    return s[:50] or "tekst"


def log(actie: str, titel: str, bestanden: list[str], meta: dict, tekst: str | None = None) -> dict:
    intern, e = _intern()
    nu = datetime.now().astimezone()
    regel = {
        "tijd": nu.isoformat(timespec="seconds"),
        "actie": actie,
        "titel": titel,
        "bestanden": bestanden,
        "meta": meta,
    }
    if tekst is not None and tekst.strip() and e.get("historie", {}).get("tekst_bewaren", True):
        map_ = intern / "historie"
        map_.mkdir(exist_ok=True)
        basis = f"{nu.strftime('%Y%m%d-%H%M%S')}-{actie}-{_slug(titel)}"
        doel, n = map_ / f"{basis}.md", 2
        while doel.exists():
            doel, n = map_ / f"{basis}-{n}.md", n + 1
        doel.write_text(tekst[:MAX_TEKST], encoding="utf-8")
        regel["tekst"] = doel.relative_to(intern).as_posix()
        regel["woorden"] = len(tekst.split())
    with (intern / "historie.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(regel, ensure_ascii=False) + "\n")
    return regel


def toon(n: int = 10) -> list[dict]:
    p = _pad()
    if not p.is_file():
        return []
    regels = [json.loads(r) for r in p.read_text(encoding="utf-8").splitlines() if r.strip()]
    return regels[-n:]


def _lees_tekst(bron: str | None) -> str | None:
    if bron is None:
        return None
    if bron == "-":
        return sys.stdin.read()
    p = Path(bron)
    if not p.is_file():
        raise ConfigFout(f"--tekst: bestand {bron} bestaat niet.")
    if p.suffix.lower() == ".docx":
        from dutchquill.docx_tekst import extract_text
        return extract_text(str(p))
    return p.read_text(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq historie", description="Logboek van DutchQuill-acties")
    sub = p.add_subparsers(dest="cmd", required=True)
    lg = sub.add_parser("log")
    lg.add_argument("--actie", required=True, choices=ACTIES)
    lg.add_argument("--titel", required=True)
    lg.add_argument("--bestand", action="append", default=[])
    lg.add_argument("--tekst", help="Pad naar de tekst (.md, .txt, .docx), of - voor stdin: er komt een kopie bij")
    lg.add_argument("--meta", default="{}")
    sub.add_parser("toon").add_argument("--n", type=int, default=10)
    a = p.parse_args(argv)
    try:
        if a.cmd == "log":
            try:
                meta = json.loads(a.meta)
            except json.JSONDecodeError as e:
                raise ConfigFout(f"--meta is geen geldige JSON: {e}") from e
            r = log(a.actie, a.titel, a.bestand, meta, _lees_tekst(a.tekst))
            print("Opgeslagen in de historie" + (f", met de tekst in {r['tekst']}." if r.get("tekst") else "."))
        else:
            print(json.dumps(toon(a.n), ensure_ascii=False, indent=2))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
