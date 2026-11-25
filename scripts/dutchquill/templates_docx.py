"""Templates beheren: welke er zijn, of een eigen .docx bruikbaar is, en een aangepaste kopie maken.

  dq template lijst
  dq template check <naam|pad>
  dq template aanpas --van <naam|pad> --naar <nieuwe naam> [--stijl kop1.font=Arial] [--stijl kop1.grootte=14]
                     [--stijl kop1.kleur=1F4E79] [--stijl normaal.regelafstand=1.5] [--marge 2.5] [--beschrijving T]

Stijlsleutels: titel, ondertitel, kop1-kop4, normaal, bijschrift, citaat, code, lijst_bullet, lijst_nummer.
Eigenschappen: font, grootte, kleur (hex), vet, cursief (ja/nee), uitlijning (links/midden/rechts/uitgevuld),
regelafstand, voor, na (punten).
`aanpas` zet de kopie in <werkmap>/templates/ en registreert hem in dutchquill.yaml. Het origineel blijft.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

from dutchquill import paden
from dutchquill.config import ConfigFout, effectief, zet
from dutchquill.export import INGEBOUWD, STIJL_STANDAARD, ExportFout, template_pad

NODIG = ("kop1", "kop2", "normaal")
HANDIG = ("titel", "kop3", "bijschrift", "lijst_bullet", "lijst_nummer", "citaat", "code", "tabel")
NL_NAMEN = {"kop1": ["Kop 1", "Kop1"], "kop2": ["Kop 2", "Kop2"], "kop3": ["Kop 3", "Kop3"], "kop4": ["Kop 4"],
            "normaal": ["Standaard", "Normaal"], "titel": ["Titel"], "ondertitel": ["Ondertitel"],
            "bijschrift": ["Bijschrift"], "citaat": ["Citaat"], "lijst_bullet": ["Lijstopsommingteken"],
            "lijst_nummer": ["Lijstnummer"]}


def lijst() -> list[dict]:
    e = effectief()
    uit = [{"naam": n, "soort": "meegeleverd", "bestand": str(paden.root() / "templates" / "docx" / f"{n}.docx")}
           for n in sorted(INGEBOUWD)]
    for n, t in (e.get("templates") or {}).items():
        uit.append({"naam": n, "soort": "eigen", "bestand": t.get("bestand"),
                    "beschrijving": t.get("beschrijving", "")})
    actief = e["uitvoer"].get("template")
    for t in uit:
        t["actief"] = t["naam"] == actief
    return uit


def check(naam: str) -> dict:
    from docx import Document
    e = effectief()
    pad = template_pad(naam, e)
    doc = Document(str(pad))
    namen = sorted(s.name for s in doc.styles if s.type == 1)  # alinea-stijlen
    mapping = e.get("stijlen") or {}
    resultaat, voorstel = {}, {}
    for sleutel in (*NODIG, *HANDIG):
        gewenst = mapping.get(sleutel) or STIJL_STANDAARD[sleutel]
        if sleutel == "tabel":
            tabellen = [s.name for s in doc.styles if s.type == 3]
            resultaat[sleutel] = gewenst if gewenst in tabellen else None
            continue
        if gewenst in namen:
            resultaat[sleutel] = gewenst
        else:
            resultaat[sleutel] = None
            for alt in NL_NAMEN.get(sleutel, []):
                if alt in namen:
                    voorstel[sleutel] = alt
                    break
            else:
                patroon = sleutel.replace("kop", r"(kop|heading)\s*")
                kandidaat = next((n for n in namen if re.search(patroon, n, re.I)), None)
                if kandidaat:
                    voorstel[sleutel] = kandidaat
    ontbreekt = [k for k in NODIG if not resultaat[k] and k not in voorstel]
    return {"template": str(pad), "stijlen_gevonden": resultaat, "voorstel_mapping": voorstel,
            "ontbreekt_echt": ontbreekt, "bruikbaar": not ontbreekt, "alle_stijlen": namen,
            "advies": ("Voeg de mapping toe met: "
                       + "; ".join(f"dq config zet stijlen.{k} \"{v}\"" for k, v in voorstel.items()))
            if voorstel else ("Template is bruikbaar." if not ontbreekt else
                              "Kopstijlen of Normal ontbreken; maak ze aan in Word of kies een andere template.")}


EIGENSCHAPPEN = {"font", "grootte", "kleur", "vet", "cursief", "uitlijning", "regelafstand", "voor", "na"}


def aanpas(van: str, naar: str, stijlen: list[str], marge: float | None, beschrijving: str | None) -> dict:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
    e = effectief()
    if not e["ingesteld"]:
        raise ConfigFout("Nog geen werkmap ingesteld. Draai eerst /dutchquill:instellen.")
    if not re.fullmatch(r"[a-z0-9][a-z0-9\-]{1,40}", naar) or naar in INGEBOUWD:
        raise ConfigFout("Kies een nieuwe naam met kleine letters, cijfers en streepjes, anders dan apa-hbo, zakelijk, "
                         "notitie of review.")
    bron = template_pad(van, e)
    doelmap = Path(e["mappen"]["templates"])
    doelmap.mkdir(parents=True, exist_ok=True)
    doel = doelmap / f"{naar}.docx"
    if doel.exists():
        raise ConfigFout(f"{doel.name} bestaat al in je templates; kies een andere naam.")
    shutil.copy2(bron, doel)
    doc = Document(str(doel))
    mapping = e.get("stijlen") or {}
    gedaan = []
    for regel in stijlen:
        m = re.fullmatch(r"(\w+)\.(\w+)=(.+)", regel.strip())
        if not m or m.group(1) not in STIJL_STANDAARD or m.group(2) not in EIGENSCHAPPEN:
            raise ConfigFout(f"'{regel}' snap ik niet. Vorm: kop1.font=Arial (sleutels: {', '.join(STIJL_STANDAARD)}; "
                             f"eigenschappen: {', '.join(sorted(EIGENSCHAPPEN))}).")
        sleutel, eig, waarde = m.groups()
        naam = mapping.get(sleutel) or STIJL_STANDAARD[sleutel]
        try:
            s = doc.styles[naam]
        except KeyError as ex:
            raise ConfigFout(f"De template heeft geen stijl '{naam}'.") from ex
        if eig == "font":
            s.font.name = waarde
            rpr = s.element.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            if rf is None:
                rf = OxmlElement("w:rFonts")
                rpr.append(rf)
            for attr in ("w:ascii", "w:hAnsi", "w:cs"):
                rf.set(qn(attr), waarde)
            for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme"):
                if rf.get(qn(attr)) is not None:
                    del rf.attrib[qn(attr)]
        elif eig == "grootte":
            s.font.size = Pt(float(waarde))
        elif eig == "kleur":
            s.font.color.rgb = RGBColor.from_string(waarde.lstrip("#").upper())
        elif eig in ("vet", "cursief"):
            setattr(s.font, "bold" if eig == "vet" else "italic", waarde.lower() in ("ja", "true", "1", "yes"))
        elif eig == "uitlijning":
            s.paragraph_format.alignment = {"links": WD_ALIGN_PARAGRAPH.LEFT, "midden": WD_ALIGN_PARAGRAPH.CENTER,
                                            "rechts": WD_ALIGN_PARAGRAPH.RIGHT,
                                            "uitgevuld": WD_ALIGN_PARAGRAPH.JUSTIFY}[waarde]
        elif eig == "regelafstand":
            s.paragraph_format.line_spacing = float(waarde)
        elif eig in ("voor", "na"):
            setattr(s.paragraph_format, "space_before" if eig == "voor" else "space_after", Pt(float(waarde)))
        gedaan.append(regel)
    if marge is not None:
        for sec in doc.sections:
            sec.top_margin = sec.bottom_margin = sec.left_margin = sec.right_margin = Cm(marge)
        gedaan.append(f"marges {marge} cm")
    doc.save(str(doel))
    zet(f"templates.{naar}", {"bestand": f"{Path(e['mappen']['templates']).name}/{doel.name}", "soort": "docx",
                              "beschrijving": beschrijving or f"Aangepaste kopie van {van}"})
    return {"template": naar, "bestand": str(doel), "aanpassingen": gedaan,
            "volgende_stap": f"Maak hem de standaard met: dq config zet uitvoer.template {naar}"}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq template", description="Templates beheren")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lijst")
    sub.add_parser("check").add_argument("naam")
    a_ = sub.add_parser("aanpas")
    a_.add_argument("--van", required=True)
    a_.add_argument("--naar", required=True)
    a_.add_argument("--stijl", action="append", default=[])
    a_.add_argument("--marge", type=float)
    a_.add_argument("--beschrijving")
    a = p.parse_args(argv)
    try:
        if a.cmd == "lijst":
            uit = lijst()
        elif a.cmd == "check":
            uit = check(a.naam)
        else:
            uit = aanpas(a.van, a.naar, a.stijl, a.marge, a.beschrijving)
        print(json.dumps(uit, ensure_ascii=False, indent=2))
    except (ConfigFout, ExportFout) as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)
