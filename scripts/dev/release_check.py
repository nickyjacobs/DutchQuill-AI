# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Controleert of een DutchQuill-release klopt, en geeft de releasetekst van een versie.

  release_check.py                  CHANGELOG-opbouw en versienummers controleren
  release_check.py --tag v2.0.0     hetzelfde, en de nieuwste versie in de CHANGELOG moet 2.0.0 zijn
  release_check.py --notes v2.0.0   de tekst voor de GitHub-release van die versie

De versie staat op drie plekken: `.claude-plugin/plugin.json`, `scripts/dutchquill/__init__.py` en
`pyproject.toml`. Alle drie moeten gelijk zijn aan de nieuwste versie in de CHANGELOG (of aan [Unreleased] voorbij
die versie, als er nog geen nieuwe release is). Opbouw van de CHANGELOG: zie docs/project/releasen.md.
Exitcodes: 0 in orde, 1 problemen gevonden.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SECTIES = ["🧭 Voor jou", "✨ Nieuw", "🔧 Veranderd", "🐛 Opgelost", "🗑️ Verwijderd", "🔒 Beveiliging"]
KOP = re.compile(r"^## \[(?P<naam>[^\]]+)\](?: - (?P<datum>\d{4}-\d{2}-\d{2}))?\s*$")
VERSIE = re.compile(r"^\d+\.\d+(?:\.\d+)?$")


def blokken(tekst: str) -> tuple[list[dict], list[str]]:
    uit, links, huidig = [], [], None
    for nr, regel in enumerate(tekst.splitlines(), 1):
        m = KOP.match(regel)
        if m:
            huidig = {"naam": m["naam"], "datum": m["datum"], "regels": [], "nr": nr}
            uit.append(huidig)
        elif re.match(r"^\[[^\]]+\]:\s+\S+", regel):
            links.append(regel)
            huidig = None
        elif huidig is not None:
            huidig["regels"].append(regel)
    return uit, links


def versies_in_code() -> dict[str, str]:
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    init = re.search(r'__version__ = "([^"]+)"', (ROOT / "scripts" / "dutchquill" / "__init__.py").read_text())
    pyproject = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M)
    return {"plugin.json": plugin, "__init__.py": init[1] if init else "?",
            "pyproject.toml": pyproject[1] if pyproject else "?"}


def controleer(tag: str | None = None) -> list[str]:
    fouten: list[str] = []
    tekst = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    bl, links = blokken(tekst)
    if not bl or bl[0]["naam"] != "Unreleased":
        fouten.append("CHANGELOG: het eerste blok moet ## [Unreleased] zijn.")
    versies = [b for b in bl if b["naam"] != "Unreleased"]
    if not versies:
        return fouten + ["CHANGELOG: geen versies gevonden."]
    sleutel = [tuple(int(x) for x in b["naam"].split(".")) for b in versies if VERSIE.match(b["naam"])]
    if sleutel != sorted(sleutel, reverse=True):
        fouten.append("CHANGELOG: versies staan niet van nieuw naar oud.")
    for b in versies:
        waar = f"CHANGELOG regel {b['nr']} ([{b['naam']}])"
        if not VERSIE.match(b["naam"]) or not b["datum"]:
            fouten.append(f"{waar}: kop moet zijn '## [x.y.z] - JJJJ-MM-DD'.")
        if not any(r.startswith("> **Kort gezegd:** ") for r in b["regels"]):
            fouten.append(f"{waar}: een regel '> **Kort gezegd:** ...' ontbreekt.")
        koppen = [r[4:].strip() for r in b["regels"] if r.startswith("### ")]
        onbekend = [k for k in koppen if k not in SECTIES]
        if onbekend:
            fouten.append(f"{waar}: onbekende sectie(s) {onbekend}; kies uit {SECTIES}.")
        elif koppen != sorted(koppen, key=SECTIES.index):
            fouten.append(f"{waar}: secties staan niet in de volgorde {SECTIES}.")
        if not any(link.startswith(f"[{b['naam']}]:") for link in links):
            fouten.append(f"{waar}: de link [{b['naam']}]: onderaan ontbreekt.")
        if f"| [{b['naam']}](" not in tekst:
            fouten.append(f"{waar}: de rij in de tabel bovenaan ontbreekt.")
    nieuwste = versies[0]["naam"]
    for plek, v in versies_in_code().items():
        if v != nieuwste:
            fouten.append(f"Versie in {plek} is {v}, de CHANGELOG zegt {nieuwste}.")
    if tag is not None and tag.removeprefix("v") != nieuwste:
        fouten.append(f"Tag {tag} hoort niet bij de nieuwste versie in de CHANGELOG ({nieuwste}).")
    return fouten


def notes(tag: str) -> str:
    bl, _ = blokken((ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
    versie = tag.removeprefix("v")
    blok = next((b for b in bl if b["naam"] == versie), None)
    if blok is None:
        raise SystemExit(f"Versie {versie} staat niet in de CHANGELOG.")
    regels = blok["regels"]
    while regels and regels[-1].strip() in ("", "---"):
        regels = regels[:-1]
    vorige = next((b["naam"] for b in bl if b["naam"] not in ("Unreleased", versie)
                   and bl.index(b) > bl.index(blok)), None)
    tekst = "\n".join(regels).strip() + "\n"
    if vorige:
        tekst += (f"\n**Alle wijzigingen:** https://github.com/nickyjacobs/DutchQuill-AI/compare/"
                  f"v{vorige}...v{versie}\n")
    return tekst


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--tag", help="de tag die gepubliceerd wordt, bijvoorbeeld v2.0.0")
    p.add_argument("--notes", metavar="TAG", help="druk de releasetekst van deze versie af")
    a = p.parse_args(argv)
    if a.notes:
        sys.stdout.write(notes(a.notes))
        return 0
    fouten = controleer(a.tag)
    for f in fouten:
        print(f"- {f}")
    print("Release-check: in orde." if not fouten else f"Release-check: {len(fouten)} probleem/problemen.")
    return 1 if fouten else 0


if __name__ == "__main__":
    sys.exit(main())
