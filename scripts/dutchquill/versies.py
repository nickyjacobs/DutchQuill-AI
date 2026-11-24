"""Versies per titel: 2-output/<actie>/<titel>/v1, v2, ...

  dq versie volgende --actie schrijven --titel "Mijn rapport"   # maakt de map aan, geeft JSON terug
  dq versie volgende --van "2-output/schrijven/Mijn rapport/v1/bron.md"   # nieuwe ronde in dezelfde titelmap
  dq versie laatste  --actie schrijven --titel "Mijn rapport"
  dq versie lijst    [--actie schrijven]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from dutchquill.config import ConfigFout, effectief

ACTIES = ("schrijven", "herschrijven", "reviewen", "humaniseren")
_VERBODEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_VERSIE = re.compile(r"^v(\d+)$")


def veilige_titel(titel: str) -> str:
    """Leesbare mapnaam: verboden tekens eruit, spaties samengevoegd, maximaal 80 tekens."""
    schoon = _VERBODEN.sub("", titel).strip().strip(".")
    schoon = re.sub(r"\s+", " ", schoon)[:80].rstrip(" .")
    return schoon or "zonder titel"


def _actiemap(actie: str) -> Path:
    if actie not in ACTIES:
        raise ConfigFout(f"Onbekende actie '{actie}'. Kies uit: {', '.join(ACTIES)}.")
    e = effectief()
    if not e["ingesteld"]:
        raise ConfigFout("Nog geen werkmap ingesteld. Draai eerst /dutchquill:instellen.")
    return Path(e["mappen"][actie])


def bestaande(titelmap: Path) -> list[int]:
    if not titelmap.is_dir():
        return []
    return sorted(int(m.group(1)) for d in titelmap.iterdir() if d.is_dir() and (m := _VERSIE.match(d.name)))


def uit_pad(pad: str | Path) -> tuple[str, str] | None:
    """Hoort een pad bij een eerdere output (2-output/<actie>/<titel>/vN/...)? Dan (actie, titel)."""
    p = Path(pad).expanduser().resolve()
    for actie in ACTIES:
        basis = _actiemap(actie).resolve()
        try:
            delen = p.relative_to(basis).parts
        except ValueError:
            continue
        if len(delen) >= 2 and _VERSIE.match(delen[1]):
            return actie, delen[0]
    return None


FORMATEN = ("docx", "pdf", "html", "md", "txt")


def formaten_in(map_: Path, naam: str) -> list[str]:
    """Welke uitvoerformaten staan er in een versiemap (alleen <titel>.<ext>, niet bron.md en dergelijke)."""
    return [f for f in FORMATEN if (map_ / f"{naam}.{f}").is_file()]


def volgende(actie: str | None, titel: str | None, van: str | None = None) -> dict:
    """Maak de volgende versiemap. Met `van` (een eerdere output) komt de nieuwe ronde in diezelfde titelmap,
    ook als de actie nu herschrijven of humaniseren is: zo staat de hele geschiedenis van één tekst bij elkaar."""
    if van:
        gevonden = uit_pad(van)
        if gevonden:
            actie, titel = gevonden
    if not actie or not titel:
        raise ConfigFout("Geef --actie en --titel, of --van met een pad in 2-output/.")
    naam = veilige_titel(titel)
    titelmap = _actiemap(actie) / naam
    nummers = bestaande(titelmap)
    if effectief().get("versies", True) is False:
        # Versies uit: elke ronde overschrijft v1.
        doel, n = titelmap / "v1", 1
        vorige = str(doel) if doel.is_dir() else None
        doel.mkdir(parents=True, exist_ok=True)
    else:
        n = (nummers[-1] + 1) if nummers else 1
        doel = titelmap / f"v{n}"
        doel.mkdir(parents=True, exist_ok=False)
        vorige = str(titelmap / f"v{nummers[-1]}") if nummers else None
    # Een vervolgronde levert dezelfde formaten als de versie waarop hij voortbouwt.
    bronmap = Path(van).expanduser().resolve() if van else None
    if bronmap and bronmap.is_file():
        bronmap = bronmap.parent
    if not (bronmap and bronmap.is_dir() and _VERSIE.match(bronmap.name)):
        bronmap = Path(vorige) if vorige else None
    vorige_formaten = formaten_in(bronmap, naam) if bronmap else []
    return {"map": str(doel), "actie": actie, "versie": n, "titel": naam, "bestandsnaam": naam, "vorige": vorige,
            "vorige_formaten": vorige_formaten}


def laatste(actie: str, titel: str) -> dict | None:
    naam = veilige_titel(titel)
    titelmap = _actiemap(actie) / naam
    nummers = bestaande(titelmap)
    if not nummers:
        return None
    m = titelmap / f"v{nummers[-1]}"
    return {"map": str(m), "versie": nummers[-1], "titel": naam,
            "bestanden": sorted(f.name for f in m.iterdir() if f.is_file())}


def lijst(actie: str | None = None) -> list[dict]:
    uit = []
    for a in ([actie] if actie else ACTIES):
        basis = _actiemap(a)
        if not basis.is_dir():
            continue
        for titelmap in sorted(d for d in basis.iterdir() if d.is_dir()):
            nummers = bestaande(titelmap)
            if nummers:
                uit.append({"actie": a, "titel": titelmap.name, "versies": len(nummers), "laatste": f"v{nummers[-1]}"})
    return uit


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq versie", description="Versies van outputs")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("volgende")
    s.add_argument("--actie", choices=ACTIES)
    s.add_argument("--titel")
    s.add_argument("--van", help="pad van een eerdere output: de nieuwe ronde komt in dezelfde titelmap")
    s = sub.add_parser("laatste")
    s.add_argument("--actie", required=True, choices=ACTIES)
    s.add_argument("--titel", required=True)
    sub.add_parser("lijst").add_argument("--actie", choices=ACTIES)
    a = p.parse_args(argv)
    try:
        if a.cmd == "volgende":
            uit = volgende(a.actie, a.titel, a.van)
        elif a.cmd == "laatste":
            uit = laatste(a.actie, a.titel)
        else:
            uit = lijst(a.actie)
        print(json.dumps(uit, ensure_ascii=False, indent=2))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
