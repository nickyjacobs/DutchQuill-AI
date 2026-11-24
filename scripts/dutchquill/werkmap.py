"""De werkmap van de gebruiker: aanmaken, tonen en controleren.

  dq werkmap init --pad <map> [--taal nl|en] [--profiel P] [--languagetool ja|nee]
  dq werkmap pad
  dq werkmap status
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from dutchquill import paden
from dutchquill.config import ConfigFout, effectief, laad_yaml, schrijf_config

MAPPEN_EN = {
    "input": "1-input", "output": "2-output", "notities": "notes", "rapporten": "reports", "beeld": "images",
    "bronnen": "sources", "mijn_stijl": "my-style", "schrijven": "write", "herschrijven": "rewrite",
    "reviewen": "review", "humaniseren": "humanize", "templates": "templates",
}

LEESMIJ = {
    "nl": """# DutchQuill-werkmap

Gooi hier je materiaal neer; DutchQuill haalt het op als je schrijft, herschrijft, reviewt of humaniseert.

| Map | Wat erin hoort |
|---|---|
| `{input}/{notities}/` | Je notities, ruwe ideeën, aantekeningen van colleges of meetings (.md, .txt, .docx) |
| `{input}/{rapporten}/` | Bestaande of halve rapporten, rapporten van anderen, readers (.docx, .pdf) |
| `{input}/{beeld}/` | Screenshots, afbeeldingen, infographics die in de tekst moeten (.png, .jpg, .heic) |
| `{input}/{bronnen}/` | Artikelen, papers, webpagina's als pdf, of een `links.md` met URL's |
| `{input}/{mijn_stijl}/` | Een paar teksten die jij zelf schreef, zodat DutchQuill klinkt zoals jij |
| `{output}/` | Resultaten per actie, per titel, per versie (v1, v2, ...) |
| `{templates}/` | Je eigen Word-templates en sjablonen |
| `eigen-regels.md` | Woorden die je nooit of juist wel wilt, en je huisstijl |
| `dutchquill.yaml` | Je instellingen (of gebruik /dutchquill:instellen) |

Mails, posts en korte teksten komen gewoon in de chat; die worden niet opgeslagen, tenzij je zegt: sla op.
""",
    "en": """# DutchQuill workspace

Drop your material here; DutchQuill picks it up when you write, rewrite, review or humanize.

| Folder | What goes in |
|---|---|
| `{input}/{notities}/` | Your notes, rough ideas, lecture or meeting notes (.md, .txt, .docx) |
| `{input}/{rapporten}/` | Existing or half-finished reports, reports by others (.docx, .pdf) |
| `{input}/{beeld}/` | Screenshots, images, infographics for the text (.png, .jpg, .heic) |
| `{input}/{bronnen}/` | Articles, papers, web pages as pdf, or a `links.md` with URLs |
| `{input}/{mijn_stijl}/` | A few texts you wrote yourself, so DutchQuill sounds like you |
| `{output}/` | Results per action, per title, per version (v1, v2, ...) |
| `{templates}/` | Your own Word templates |
| `eigen-regels.md` | Words you never (or always) want, and your house style |
| `dutchquill.yaml` | Your settings (or use /dutchquill:instellen) |

Emails, posts and short texts simply appear in the chat and are not saved unless you say: save it.
""",
}

EIGEN_REGELS = """# Eigen regels

Regels die altijd voor jou gelden, bovenop de gidsen. Voorbeelden:

## Nooit gebruiken
<!-- één woord of zin per regel, bijvoorbeeld: synergie -->

## Juist wel (niet als AI-patroon zien)
<!-- bijvoorbeeld een vakterm die je vaak nodig hebt -->

## Huisstijl
<!-- bijvoorbeeld: bedrijfsnaam altijd met hoofdletters, datums als 24 november 2026 -->
"""


def _schrijf_als_nieuw(pad: Path, tekst: str) -> bool:
    if pad.exists():
        return False
    pad.write_text(tekst, encoding="utf-8")
    return True


def init(pad: Path, taal: str = "nl", profiel: str = "zakelijk", languagetool: bool = False) -> dict:
    pad = pad.expanduser().resolve()
    if pad.exists() and not pad.is_dir():
        raise ConfigFout(f"{pad} bestaat al en is geen map.")
    pad.mkdir(parents=True, exist_ok=True)
    cfg_pad = pad / paden.WERKMAP_CONFIG
    nieuw_cfg = not cfg_pad.exists()

    if nieuw_cfg:
        sjabloon = (paden.root() / "config" / "dutchquill.voorbeeld.yaml").read_text(encoding="utf-8")
        tekst = (sjabloon.replace("__TAAL__", taal).replace("__PROFIEL__", profiel)
                 .replace("__LANGUAGETOOL__", "true" if languagetool else "false"))
        if taal == "en":
            tekst += "\n# Mapnamen (Engels gekozen bij het instellen)\nmappen:\n" + "".join(
                f"  {k}: {v}\n" for k, v in MAPPEN_EN.items())
        data = _yaml_laad_tekst(tekst)
        schrijf_config(cfg_pad, data)
    mappen = effectief_mappen(cfg_pad)

    gemaakt = []
    for sleutel in ("notities", "rapporten", "beeld", "bronnen", "mijn_stijl"):
        m = pad / mappen["input"] / mappen[sleutel]
        if not m.exists():
            gemaakt.append(m.relative_to(pad).as_posix())
        m.mkdir(parents=True, exist_ok=True)
    for sleutel in ("schrijven", "herschrijven", "reviewen", "humaniseren"):
        m = pad / mappen["output"] / mappen[sleutel]
        if not m.exists():
            gemaakt.append(m.relative_to(pad).as_posix())
        m.mkdir(parents=True, exist_ok=True)
    (pad / mappen["templates"]).mkdir(exist_ok=True)
    (pad / ".dutchquill").mkdir(exist_ok=True)

    leesmij_taal = "en" if taal == "en" else "nl"
    leesmij = "README.md" if taal == "en" else "LEESMIJ.md"
    _schrijf_als_nieuw(pad / leesmij, LEESMIJ[leesmij_taal].format(**mappen))
    _schrijf_als_nieuw(pad / "eigen-regels.md", EIGEN_REGELS)
    paden.zet_werkmap(pad)
    return {"werkmap": str(pad), "config_nieuw": nieuw_cfg, "mappen_gemaakt": gemaakt}


def _yaml_laad_tekst(tekst: str):
    from dutchquill.config import _yaml
    return _yaml().load(tekst)


def effectief_mappen(cfg_pad: Path) -> dict:
    from dutchquill.config import naar_dict, schema
    from dutchquill.schema_check import standaardwaarden
    sch = schema()
    standaard = standaardwaarden(sch["properties"]["mappen"], sch)
    eigen = naar_dict(laad_yaml(cfg_pad)).get("mappen", {}) if cfg_pad.is_file() else {}
    return {**standaard, **eigen}


def status() -> dict:
    e = effectief()
    if not e["ingesteld"]:
        return {"ingesteld": False, "melding": "Nog geen werkmap. Draai /dutchquill:instellen."}
    tellingen = {}
    for sleutel in ("notities", "rapporten", "beeld", "bronnen", "mijn_stijl"):
        m = Path(e["mappen"][sleutel])
        bestanden = [f for f in m.rglob("*") if f.is_file() and not f.name.startswith(".")] if m.is_dir() else []
        laatste = max((f.stat().st_mtime for f in bestanden), default=None)
        tellingen[sleutel] = {
            "aantal": len(bestanden),
            "laatst_gewijzigd": datetime.fromtimestamp(laatste).isoformat(timespec="minutes") if laatste else None,
        }
    return {"ingesteld": True, "werkmap": e["werkmap"], "profiel": e["profiel"], "input": tellingen}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq werkmap", description="De DutchQuill-werkmap")
    sub = p.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("init", help="Werkmap aanmaken of aanvullen (overschrijft niets)")
    i.add_argument("--pad", required=True)
    i.add_argument("--taal", choices=["nl", "en", "auto"], default="nl")
    i.add_argument("--profiel", default="zakelijk")
    i.add_argument("--languagetool", choices=["ja", "nee"], default="nee")
    sub.add_parser("pad")
    sub.add_parser("status")
    a = p.parse_args(argv)
    try:
        if a.cmd == "init":
            uit = init(Path(a.pad), a.taal, a.profiel, a.languagetool == "ja")
        elif a.cmd == "pad":
            w = paden.werkmap(None)
            print(w if w else "")
            return
        else:
            uit = status()
        print(json.dumps(uit, ensure_ascii=False, indent=2))
    except ConfigFout as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
