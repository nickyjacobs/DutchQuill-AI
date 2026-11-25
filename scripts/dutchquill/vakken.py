"""Inlevereisen (quick scan) en beoordelingscriteria (rubric) per vak, uit de werkmap.

De bestanden staan in <werkmap>/templates/vakken/<VAKCODE>/quick-scan.md en .../beoordelingscriteria.md. Van beide
telt alleen de sectie `## Rapportage`; `## Praktijk` gaat niet over de tekst en wordt overgeslagen.

Welk vak: een meegegeven --code wint. Anders het enige vak in `student.vakken`, of de enige vakmap. Zijn er meer,
dan geeft het commando de keuzes terug en vraagt de skill welk vak.

  dq vak toon [--code CODE] [--json]
  dq vak lijst [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from dutchquill.config import ConfigFout, effectief

SOORTEN = {"quick_scan": "quick-scan.md", "beoordelingscriteria": "beoordelingscriteria.md"}
_KOP2 = re.compile(r"^##\s+(.+?)\s*$")
_KOP3 = re.compile(r"^###\s+(.+?)\s*$")
_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+(?:\[[ xX]\]\s*)?(.+?)\s*$")


def _code(tekst: str | None) -> str:
    return re.sub(r"[^\w\-]", "", tekst or "").upper()


def _basis() -> Path:
    e = effectief()
    if not e["ingesteld"]:
        raise ConfigFout("Nog geen werkmap ingesteld. Draai eerst /dutchquill:instellen.")
    return Path(e["mappen"]["templates"]) / "vakken"


def lijst() -> list[dict]:
    """Alle vakken: uit het profiel en uit de vakmappen, met welke bestanden er zijn."""
    basis = _basis()
    profiel = effectief().get("student", {}).get("vakken") or []
    vakken: dict[str, dict] = {}
    for v in profiel:
        c = _code(v.get("code"))
        if c:
            vakken[c] = {"code": c, "naam": v.get("naam") or "", "in_profiel": True}
    if basis.is_dir():
        for d in sorted(p for p in basis.iterdir() if p.is_dir()):
            vakken.setdefault(_code(d.name), {"code": _code(d.name), "naam": "", "in_profiel": False})
    for c, v in vakken.items():
        v["bestanden"] = [s for s, naam in SOORTEN.items() if (basis / c / naam).is_file()]
    return list(vakken.values())


def rapportage(tekst: str) -> tuple[list[dict], bool]:
    """De items onder `## Rapportage`, met hun subkop (###). Zonder die kop: alle items, en False."""
    regels = tekst.splitlines()
    def is_rapportage(regel: str) -> bool:
        m = _KOP2.match(regel)
        return bool(m) and m.group(1).strip().lower().startswith("rapportage")

    heeft_kop = any(is_rapportage(r) for r in regels)
    binnen, groep, items = not heeft_kop, "", []
    for r in regels:
        k2 = _KOP2.match(r)
        if k2:
            if heeft_kop:
                binnen = is_rapportage(r)
            groep = ""
            continue
        k3 = _KOP3.match(r)
        if k3:
            groep = k3.group(1).strip()
            continue
        if binnen:
            m = _ITEM.match(r)
            if m and not m.group(1).lower().startswith("voorbeeld:"):
                items.append({"groep": groep, "eis": m.group(1)})
    return items, heeft_kop


def kies(code: str | None = None) -> dict:
    """Welk vak geldt, en wat er voor dat vak geladen is."""
    basis = _basis()
    alle = lijst()
    gekozen = _code(code) if code else None
    if not gekozen:
        profiel = [v for v in alle if v["in_profiel"]]
        kandidaten = profiel if profiel else [v for v in alle if v["bestanden"]]
        if len(kandidaten) == 1:
            gekozen = kandidaten[0]["code"]
        elif not kandidaten:
            return {"status": "geen", "melding": "Geen vak in het profiel en geen vakmap met criteria.", "opties": []}
        else:
            return {"status": "kies", "melding": "Meer vakken; vraag welk vak deze tekst is.",
                    "opties": [{"code": v["code"], "naam": v["naam"]} for v in kandidaten]}
    naam = next((v["naam"] for v in alle if v["code"] == gekozen), "")
    uit: dict = {"status": "geladen", "vak": {"code": gekozen, "naam": naam}, "geladen": [], "ontbreekt": []}
    for soort, bestand in SOORTEN.items():
        pad = basis / gekozen / bestand
        if not pad.is_file():
            uit["ontbreekt"].append(soort)
            continue
        items, heeft_kop = rapportage(pad.read_text(encoding="utf-8", errors="replace"))
        uit[soort] = {"pad": pad.as_posix(), "items": items, "alleen_rapportage": heeft_kop}
        uit["geladen"].append(soort)
    if not uit["geladen"]:
        uit["status"] = "leeg"
    uit["melding"] = _melding(uit)
    return uit


def _melding(r: dict) -> str:
    vak = r["vak"]["code"] + (f" ({r['vak']['naam']})" if r["vak"]["naam"] else "")
    if r["status"] == "leeg":
        return f"Vak {vak}: geen quick scan en geen beoordelingscriteria in de werkmap."
    delen = []
    for soort, label in (("quick_scan", "inlevereisen"), ("beoordelingscriteria", "beoordelingscriteria")):
        if soort in r:
            n = len(r[soort]["items"])
            extra = "" if r[soort]["alleen_rapportage"] else ", geen sectie Rapportage: hele bestand gelezen"
            delen.append(f"{n} {label}{extra}")
    return f"Criteria geladen voor {vak}: " + "; ".join(delen) + "."


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq vak", description="Inlevereisen en beoordelingscriteria per vak")
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("toon", help="criteria van één vak (vanzelf gekozen als er één is)")
    t.add_argument("--code")
    t.add_argument("--json", action="store_true")
    sub.add_parser("lijst", help="alle vakken").add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        r = kies(a.code) if a.cmd == "toon" else lijst()
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    elif a.cmd == "lijst":
        for v in r:
            print(f"{v['code']}  {v['naam']}  [{', '.join(v['bestanden']) or 'geen criteria'}]")
    else:
        print(r["melding"])
        for o in r.get("opties", []):
            print(f"  - {o['code']} {o['naam']}".rstrip())
        for soort in ("quick_scan", "beoordelingscriteria"):
            if soort in r:
                print(f"\n{soort}: {r[soort]['pad']}")
                for i in r[soort]["items"]:
                    print(f"  - {i['groep'] + ': ' if i['groep'] else ''}{i['eis']}")
