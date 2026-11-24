"""Het materiaal in de werkmap: wat ligt er, wat is nieuw, en alles voor één opdracht klaarzetten.

  dq materiaal inventaris [--json]
  dq materiaal verzamel --opdracht "<titel>" [--nieuw | --alles | --bestand <pad> ...] [--met-stijl]

`verzamel` maakt <werkmap>/.dutchquill/materiaal/<datum>-<titel>/ met:
  bronnen/   een .md per tekstbestand (paginamarkeringen, metadata in de kop)
  beeld/     genormaliseerde beelden (los aangeleverd en uit documenten gehaald)
  manifest.json
en markeert de gebruikte bestanden als gezien, zodat "nieuw" de volgende keer klopt.
De map mijn-stijl doet alleen mee met --met-stijl (die is voor stemkalibratie, niet voor inhoud).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dutchquill import beeld as beeldmod
from dutchquill import extraheer as ext
from dutchquill.config import ConfigFout, effectief
from dutchquill.versies import veilige_titel

INPUTMAPPEN = ("notities", "rapporten", "beeld", "bronnen", "mijn_stijl")


def _context() -> tuple[dict, Path]:
    e = effectief()
    if not e["ingesteld"]:
        raise ConfigFout("Nog geen werkmap ingesteld. Draai eerst /dutchquill:instellen.")
    return e, Path(e["mappen"]["intern"])


def _gezien_pad(intern: Path) -> Path:
    return intern / "gezien.json"


def _lees_gezien(intern: Path) -> dict:
    try:
        return json.loads(_gezien_pad(intern).read_text(encoding="utf-8"))
    except Exception:
        return {}


def inventaris() -> list[dict]:
    e, intern = _context()
    werkmap = Path(e["werkmap"])
    gezien = _lees_gezien(intern)
    uit = []
    for sleutel in INPUTMAPPEN:
        basis = Path(e["mappen"][sleutel])
        if not basis.is_dir():
            continue
        for f in sorted(basis.rglob("*")):
            if not f.is_file() or f.name.startswith((".", "~$")):
                continue
            rel = str(f.relative_to(werkmap))
            mtime = f.stat().st_mtime
            uit.append({
                "map": sleutel,
                "pad": str(f),
                "rel": rel,
                "soort": ext.soort(f),
                "grootte_kb": round(f.stat().st_size / 1024, 1),
                "gewijzigd": datetime.fromtimestamp(mtime).isoformat(timespec="minutes"),
                "nieuw": gezien.get(rel) != round(mtime, 3),
            })
    return uit


def verzamel(opdracht: str, keuze: str = "nieuw", bestanden: list[str] | None = None,
             met_stijl: bool = False) -> dict:
    e, intern = _context()
    werkmap = Path(e["werkmap"])
    alles = inventaris()
    if bestanden:
        gekozen = []
        for b in bestanden:
            p = Path(b).expanduser()
            p = p if p.is_absolute() else werkmap / p
            treffer = [x for x in alles if Path(x["pad"]) == p.resolve() or Path(x["pad"]) == p]
            if treffer:
                gekozen += treffer
            elif p.is_file():  # bestand buiten de werkmap mag ook
                gekozen.append({"map": "extern", "pad": str(p), "rel": str(p), "soort": ext.soort(p), "nieuw": True})
            else:
                raise ConfigFout(f"Bestand niet gevonden: {b}")
    else:
        gekozen = [x for x in alles if keuze == "alles" or x["nieuw"]]
    if not met_stijl:
        gekozen = [x for x in gekozen if x["map"] != "mijn_stijl"]
    if not gekozen:
        return {"map": None, "bestanden": [], "melding":
                "Geen (nieuw) materiaal gevonden. Gebruik --alles, of zet bestanden in de inputmappen."}

    doelmap = intern / "materiaal" / f"{datetime.now():%Y-%m-%d-%H%M}-{veilige_titel(opdracht)[:40]}"
    bronnen_dir, beeld_dir = doelmap / "bronnen", doelmap / "beeld"
    resultaten, beelden, ophalen, genoemd = [], [], set(), set()
    for item in gekozen:
        pad = Path(item["pad"])
        if item["soort"] == "beeld":
            r = beeldmod.normaliseer(pad, beeld_dir)
            r["map"] = item["map"]
            beelden.append(r)
            continue
        r = ext.extraheer(pad, bronnen_dir)
        r["map"] = item["map"]
        for a in r.get("afbeeldingen", []):
            nb = beeldmod.normaliseer(Path(a), beeld_dir / pad.stem)
            nb["uit_document"] = str(pad)
            beelden.append(nb)
        # Zelf aangeleverde links worden opgehaald; URL's die een document alleen noemt, niet automatisch.
        aangeleverd = r["soort"] == "link" or pad.stem.lower() in ("links", "bronnen", "urls") or (
            item["map"] == "bronnen" and r["soort"] == "tekst")
        (ophalen if aangeleverd else genoemd).update(r.get("urls", []))
        resultaten.append(r)

    manifest = {
        "opdracht": opdracht,
        "gemaakt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "werkmap": str(werkmap),
        "map": str(doelmap),
        "bestanden": resultaten,
        "beelden": beelden,
        "urls": sorted(ophalen),
        "urls_genoemd": sorted(genoemd - ophalen),
        "totaal_woorden": sum(r.get("woorden", 0) for r in resultaten),
        "fouten": [r for r in resultaten + beelden if "fout" in r],
    }
    doelmap.mkdir(parents=True, exist_ok=True)
    (doelmap / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    gezien = _lees_gezien(intern)
    for item in gekozen:
        if item["map"] != "extern":
            gezien[item["rel"]] = round(Path(item["pad"]).stat().st_mtime, 3)
    _gezien_pad(intern).write_text(json.dumps(gezien, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def samenvatting(m: dict) -> dict:
    """Korte versie voor de chat en de skill: zonder de volledige lijsten met metadata."""
    if not m.get("map"):
        return m
    return {
        "map": m["map"],
        "manifest": str(Path(m["map"]) / "manifest.json"),
        "teksten": [{"bron": Path(r["bron"]).name, "soort": r["soort"], "woorden": r.get("woorden"),
                     "paginas": r.get("paginas"), "uitvoer": r.get("uitvoer"),
                     "waarschuwingen": r.get("waarschuwingen") or None} for r in m["bestanden"]],
        "beelden": len([b for b in m["beelden"] if "fout" not in b]),
        "urls": m["urls"],
        "urls_genoemd": len(m.get("urls_genoemd", [])),
        "totaal_woorden": m["totaal_woorden"],
        "fouten": [{"bron": f["bron"], "fout": f["fout"]} for f in m["fouten"]],
    }


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq materiaal", description="Materiaal in de werkmap")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("inventaris").add_argument("--json", action="store_true")
    v = sub.add_parser("verzamel")
    v.add_argument("--opdracht", required=True)
    groep = v.add_mutually_exclusive_group()
    groep.add_argument("--nieuw", action="store_true", help="Alleen nieuw of gewijzigd materiaal (standaard)")
    groep.add_argument("--alles", action="store_true")
    groep.add_argument("--bestand", action="append", help="Precies deze bestanden (herhaalbaar)")
    v.add_argument("--met-stijl", action="store_true", help="Ook de map mijn-stijl meenemen")
    a = p.parse_args(argv)
    try:
        if a.cmd == "inventaris":
            items = inventaris()
            if a.json:
                print(json.dumps(items, ensure_ascii=False, indent=2))
                return
            if not items:
                print("De inputmappen zijn leeg.")
                return
            for it in items:
                print(f"{'NIEUW ' if it['nieuw'] else '      '}{it['rel']}  ({it['soort']}, {it['grootte_kb']} kB, "
                      f"{it['gewijzigd']})")
        else:
            keuze = "alles" if a.alles else "nieuw"
            m = verzamel(a.opdracht, keuze, a.bestand, a.met_stijl)
            print(json.dumps(samenvatting(m), ensure_ascii=False, indent=2))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
