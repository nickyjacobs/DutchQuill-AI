"""Welke gidsen en sjablonen gelden, en waar staat de nieuwste versie?

  dq gids voor [--genre G] [--profiel P] [--set k=v ...]   # JSON: de te lezen gidsen voor deze opdracht
  dq gids pad <naam>                                       # bijv. nl/humaniseren, toon, genres/mail

Zoekvolgorde:
  genre-sjablonen: eigen sjabloon in <werkmap>/templates/genres/ gaat voor het meegeleverde;
  gidsen: de versie met de nieuwste `gecontroleerd`-datum wint, uit ${CLAUDE_PLUGIN_DATA}/gidsen/ (bijgewerkt
  via /dutchquill:bijwerken) of uit de plugin zelf (een plugin-update met een nieuwere basis wint dus).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from dutchquill import paden
from dutchquill.config import ConfigFout, effectief

GENRES = ("rapport", "onderzoeksrapport", "adviesrapport", "zakelijk-rapport", "sop", "research-notitie", "mail",
          "linkedin", "social", "readme", "memo", "kort")


def _gecontroleerd(pad: Path) -> str:
    try:
        kop = pad.read_text(encoding="utf-8")[:800]
    except OSError:
        return ""
    m = re.search(r"^gecontroleerd:\s*['\"]?(\d{4}-\d{2}-\d{2})", kop, re.MULTILINE)
    return m.group(1) if m else ""


def pad(naam: str) -> Path:
    naam = naam.removesuffix(".md")
    if naam.startswith("genres/"):
        genre = naam.split("/", 1)[1]
        try:
            e = effectief()
            if e["ingesteld"]:
                eigen = Path(e["mappen"]["templates"]) / "genres" / f"{genre}.md"
                if eigen.is_file():
                    return eigen
        except ConfigFout:
            pass
        basis = paden.root() / "templates" / "genres" / f"{genre}.md"
        if basis.is_file():
            return basis
        raise ConfigFout(f"Geen sjabloon voor genre '{genre}'. Bekend: {', '.join(GENRES)}.")
    kandidaten = [p for p in (paden.data() / "gidsen" / f"{naam}.md", paden.root() / "gidsen" / f"{naam}.md")
                  if p.is_file()]
    if not kandidaten:
        raise ConfigFout(f"Gids '{naam}' bestaat niet.")
    return max(kandidaten, key=_gecontroleerd)  # gelijke datum: de eerste (bijgewerkte kopie) wint


def voor(genre: str | None = None, profiel: str | None = None, sets: list[str] | None = None) -> dict:
    e = effectief(genre, profiel, sets)
    taal = e["taal"] if e["taal"] in ("nl", "en") else "nl"
    c = e["controles"]
    lijst: list[tuple[str, str]] = [("werkwijze", "werkwijze/basis"), ("toon", "toon")]
    lijst.append(("kern", "nl/kern" if taal == "nl" else "en/style"))
    if c.get("taalregels") and taal == "nl":
        lijst.append(("taalregels", "nl/taal"))
    if c.get("academische_stijl"):
        lijst.append(("academische_stijl", "nl/academische-stijl"))
    if c.get("apa"):
        lijst += [("apa", "nl/apa"), ("ai_gebruik", "nl/ai-gebruik")]
    if c.get("humaniseren"):
        lijst.append(("humaniseren", "nl/humaniseren" if taal == "nl" else "en/humanize"))
    gidsen = [{"module": m, "naam": n, "pad": str(pad(n))} for m, n in lijst]
    if genre:
        gidsen.append({"module": "genre", "naam": f"genres/{genre}", "pad": str(pad(f"genres/{genre}"))})
    extra = {}
    if e["ingesteld"]:
        for sleutel in ("eigen_regels", "stemprofiel"):
            p = Path(e["mappen"][sleutel])
            if p.is_file():
                extra[sleutel] = str(p)
        stem_json = Path(e["mappen"]["intern"]) / "stem.json"
        if stem_json.is_file():
            extra["stem_json"] = str(stem_json)
    return {"genre": genre, "taal": e["taal"], "profiel": e["profiel"], "gidsen": gidsen, **extra}


def _huidig(naam: str) -> Path:
    if naam.startswith("data/"):
        eigen = paden.data() / "gidsen" / f"{naam}.yaml"
        return eigen if eigen.is_file() else paden.root() / "gidsen" / f"{naam}.yaml"
    return pad(naam)


def diff(naam: str, van: Path) -> str:
    import difflib
    oud = _huidig(naam).read_text(encoding="utf-8").splitlines(keepends=True)
    nieuw = van.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(difflib.unified_diff(oud, nieuw, fromfile=f"{naam} (nu)", tofile=f"{naam} (voorstel)", n=2))


def schrijf(naam: str, van: Path, repo: bool = False) -> dict:
    """Zet een goedgekeurde nieuwe versie neer en stempel de controledatum van vandaag erin."""
    from datetime import date
    if naam.startswith("genres/") or naam.startswith("werkwijze/"):
        raise ConfigFout("Sjablonen en de werkwijze worden niet via bijwerken aangepast.")
    ext = ".yaml" if naam.startswith("data/") else ".md"
    tekst = van.read_text(encoding="utf-8")
    vandaag = date.today().isoformat()
    sleutel = "bijgewerkt" if ext == ".yaml" else "gecontroleerd"
    if re.search(rf"(?m)^{sleutel}:", tekst):
        tekst = re.sub(rf"(?m)^{sleutel}:.*$", f"{sleutel}: {vandaag}", tekst, count=1)
    else:
        raise ConfigFout(f"Het voorstel mist de regel '{sleutel}:' in de kop; die is nodig om de nieuwste te kiezen.")
    if repo:
        if not (paden.root() / ".git").exists():
            raise ConfigFout("--repo kan alleen in de broncode van de plugin (onderhoud), niet in een installatie.")
        doel = paden.root() / "gidsen" / f"{naam}{ext}"
    else:
        doel = paden.data() / "gidsen" / f"{naam}{ext}"
    doel.parent.mkdir(parents=True, exist_ok=True)
    if doel.is_file():
        doel.with_suffix(doel.suffix + ".bak").write_text(doel.read_text(encoding="utf-8"), encoding="utf-8")
    doel.write_text(tekst, encoding="utf-8")
    return {"gids": naam, "geschreven": str(doel), sleutel: vandaag}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq gids", description="Gidsen en sjablonen vinden")
    sub = p.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("voor")
    v.add_argument("--genre", choices=GENRES)
    v.add_argument("--profiel")
    v.add_argument("--set", action="append", default=[])
    sub.add_parser("pad").add_argument("naam")
    d = sub.add_parser("diff", help="Voorstel vergelijken met de huidige gids")
    d.add_argument("naam")
    d.add_argument("--van", required=True)
    w = sub.add_parser("schrijf", help="Goedgekeurd voorstel wegschrijven (met datum van vandaag)")
    w.add_argument("naam")
    w.add_argument("--van", required=True)
    w.add_argument("--repo", action="store_true", help="Onderhoud: schrijf in de pluginbron zelf")
    a = p.parse_args(argv)
    try:
        if a.cmd == "voor":
            print(json.dumps(voor(a.genre, a.profiel, a.set), ensure_ascii=False, indent=2))
        elif a.cmd == "diff":
            print(diff(a.naam, Path(a.van)) or "Geen verschil.")
        elif a.cmd == "schrijf":
            print(json.dumps(schrijf(a.naam, Path(a.van), a.repo), ensure_ascii=False, indent=2))
        else:
            print(pad(a.naam))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
