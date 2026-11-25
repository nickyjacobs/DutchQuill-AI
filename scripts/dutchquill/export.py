"""Exporteer één Markdown-bron naar .docx, .pdf, .html, .md en .txt, met de template uit de config.

  dq export --bron <bron.md> --naam "<titel>" [--map <map>] [--formaten docx,pdf] [--template <naam|pad>]
            [--genre G] [--profiel P] [--set sleutel=waarde ...]

- APA aan (controles.apa): de APA-engine (titelpagina, samenvatting, inhoudsopgave, literatuurlijst, bijlagen),
  met de opmaak uit de template (standaard apa-hbo).
- APA uit: een template-gestuurde export. De stijlen (Heading 1-4, Title, Caption, List Bullet, ...) komen uit de
  template; afwijkende stijlnamen vertaal je met `stijlen:` in dutchquill.yaml.
- PDF: via LibreOffice (beste gelijkenis met de .docx), anders headless Chrome of Edge (vanuit de html),
  anders een eenvoudige opmaak met reportlab.
- Metadata is eerlijk: titel, auteur en het echte tijdstip van maken. Geen sporen van de gebruikte libraries.

Markdown-afspraken: gidsen/werkwijze/markdown.md
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from dutchquill import paden
from dutchquill.config import ConfigFout, effectief, naar_dict

FORMATEN = ("docx", "pdf", "html", "md", "txt")
INGEBOUWD = {"apa-hbo", "zakelijk", "notitie"}
LANG_RAPPORT = {"rapport", "onderzoeksrapport", "adviesrapport", "zakelijk-rapport", "technisch-rapport"}
STIJL_STANDAARD = {
    "titel": "Title", "ondertitel": "Subtitle", "kop1": "Heading 1", "kop2": "Heading 2", "kop3": "Heading 3",
    "kop4": "Heading 4", "normaal": "Normal", "lijst_bullet": "List Bullet", "lijst_nummer": "List Number",
    "bijschrift": "Caption", "citaat": "Quote", "code": "Code", "tabel": "Table Grid",
}
WOORDEN = {
    "nl": {"figuur": "Figuur", "tabel": "Tabel", "inhoud": "Inhoudsopgave",
           "toc": "Klik met de rechtermuisknop en kies 'Veld bijwerken' om de inhoudsopgave te vullen."},
    "en": {"figuur": "Figure", "tabel": "Table", "inhoud": "Contents",
           "toc": "Right-click and choose 'Update Field' to fill in the table of contents."},
}
MAAND = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober",
         "november", "december"]


class ExportFout(Exception):
    pass


# ---------------------------------------------------------------- bron lezen


def lees_bron(pad: Path) -> tuple[dict, str]:
    tekst = pad.read_text(encoding="utf-8")
    meta: dict = {}
    if tekst.startswith("---"):
        eind = tekst.find("\n---", 3)
        if eind != -1:
            from ruamel.yaml import YAML
            try:
                meta = naar_dict(YAML(typ="safe").load(tekst[3:eind])) or {}
            except Exception as e:
                raise ExportFout(f"De frontmatter van {pad.name} is geen geldige YAML: {e}") from e
            tekst = tekst[eind + 4:].lstrip("\n")
    # beeldpaden absoluut maken (relatief aan bron.md)
    def abs_beeld(m):
        p = Path(m.group(2).strip())
        if not p.is_absolute() and not m.group(2).startswith(("http://", "https://", "data:")):
            p = (pad.parent / p).resolve()
        return f"![{m.group(1)}]({p})"
    tekst = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", abs_beeld, tekst)
    return {str(k): ("" if v is None else str(v)) for k, v in meta.items()}, tekst


def datum_nl(d: date) -> str:
    return f"{d.day} {MAAND[d.month - 1]} {d.year}"


def template_pad(naam: str | None, e: dict) -> Path:
    if not naam:
        naam = e["uitvoer"].get("template") or "zakelijk"
    eigen = e.get("templates", {}).get(naam)
    if eigen:
        p = Path(eigen["bestand"]).expanduser()
        if not p.is_absolute() and e.get("werkmap"):
            p = Path(e["werkmap"]) / p
        if not p.is_file():
            raise ExportFout(f"Template '{naam}' verwijst naar {p}, maar dat bestand bestaat niet.")
        return p
    if naam in INGEBOUWD:
        return paden.root() / "templates" / "docx" / f"{naam}.docx"
    p = Path(naam).expanduser()
    if p.is_file():
        return p
    raise ExportFout(f"Onbekende template '{naam}'. Meegeleverd: {', '.join(sorted(INGEBOUWD))}; "
                     f"eigen: {', '.join(e.get('templates', {})) or 'geen'}.")


# ---------------------------------------------------------------- markdown naar blokken


def blokken(tekst: str) -> list[dict]:
    regels = tekst.splitlines()
    uit: list[dict] = []
    i = 0
    alinea: list[str] = []

    def sluit_alinea():
        if alinea:
            uit.append({"type": "alinea", "tekst": " ".join(x.strip() for x in alinea)})
            alinea.clear()

    while i < len(regels):
        r = regels[i]
        s = r.strip()
        if not s:
            sluit_alinea()
            i += 1
            continue
        if s in ("\\pagebreak", "<!-- pagina -->", "\\newpage"):
            sluit_alinea()
            uit.append({"type": "pagina"})
            i += 1
            continue
        if s.startswith("<!--"):
            sluit_alinea()
            while i < len(regels) and "-->" not in regels[i]:
                i += 1
            i += 1
            continue
        if s.startswith("```") or s.startswith("~~~"):
            sluit_alinea()
            taal, code = s[3:].strip(), []
            i += 1
            while i < len(regels) and not regels[i].strip().startswith(("```", "~~~")):
                code.append(regels[i])
                i += 1
            uit.append({"type": "code", "taal": taal, "tekst": "\n".join(code)})
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            sluit_alinea()
            uit.append({"type": "kop", "niveau": len(m.group(1)), "tekst": m.group(2).strip()})
            i += 1
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", s)
        if m:
            sluit_alinea()
            uit.append({"type": "beeld", "bijschrift": m.group(1).strip(), "pad": m.group(2).strip()})
            i += 1
            continue
        if s.startswith("|"):
            sluit_alinea()
            rijen = []
            while i < len(regels) and regels[i].strip().startswith("|"):
                cellen = [c.strip() for c in regels[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cellen if c):
                    rijen.append(cellen)
                i += 1
            titel = None
            # **Tabel 1** en *titel* vlak boven de tabel
            while uit and uit[-1]["type"] == "alinea" and len(uit[-1]["tekst"]) < 120:
                t = uit[-1]["tekst"]
                lm = re.fullmatch(r"\*\*(?:Tabel|Table)\s+(\d+)\.?\*\*(?:\s+\*(.+)\*)?", t)
                tm = re.fullmatch(r"\*(.+)\*", t)
                if lm:
                    titel = titel or lm.group(2)
                    uit.pop()
                    break
                if tm and titel is None:
                    titel = tm.group(1)
                    uit.pop()
                    continue
                break
            if rijen:
                uit.append({"type": "tabel", "kop": rijen[0], "rijen": rijen[1:], "titel": titel})
            continue
        if s.startswith(">"):
            sluit_alinea()
            citaat = []
            while i < len(regels) and regels[i].strip().startswith(">"):
                citaat.append(re.sub(r"^\s*>\s?", "", regels[i]))
                i += 1
            uit.append({"type": "citaat", "tekst": " ".join(c.strip() for c in citaat if c.strip())})
            continue
        m = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", r)
        if m:
            sluit_alinea()
            items = []
            genummerd = m.group(2)[0].isdigit()
            while i < len(regels):
                m2 = re.match(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$", regels[i])
                if not m2:
                    if regels[i].startswith("   ") and regels[i].strip() and items:
                        items[-1] = (items[-1][0], items[-1][1] + " " + regels[i].strip())
                        i += 1
                        continue
                    break
                items.append((len(m2.group(1).replace("\t", "    ")) // 2, m2.group(3).strip()))
                i += 1
            uit.append({"type": "lijst", "genummerd": genummerd, "items": items})
            continue
        if re.fullmatch(r"[-*_]{3,}", s):
            sluit_alinea()
            i += 1
            continue
        alinea.append(r)
        i += 1
    sluit_alinea()
    return uit


INLINE = re.compile(r"(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def inline_delen(tekst: str):
    """Splits tekst in (soort, tekst, url) voor vet, cursief, code en links."""
    pos = 0
    for m in INLINE.finditer(tekst):
        if m.start() > pos:
            yield ("tekst", tekst[pos:m.start()], None)
        t = m.group(0)
        if t.startswith("**"):
            yield ("vet", t[2:-2], None)
        elif t.startswith("`"):
            yield ("code", t[1:-1], None)
        elif t.startswith("["):
            lm = re.match(r"\[([^\]]+)\]\(([^)]+)\)", t)
            yield ("link", lm.group(1), lm.group(2))
        else:
            yield ("cursief", t[1:-1], None)
        pos = m.end()
    if pos < len(tekst):
        yield ("tekst", tekst[pos:], None)


def platte_tekst(tekst: str) -> str:
    return "".join(t if s != "link" else f"{t} ({u})" for s, t, u in inline_delen(tekst))


# ---------------------------------------------------------------- docx (generiek)


def _stijlnaam(doc, sleutel: str, mapping: dict) -> str | None:
    namen = {s.name for s in doc.styles}
    voorkeur = mapping.get(sleutel) or STIJL_STANDAARD[sleutel]
    for kandidaat in (voorkeur, STIJL_STANDAARD[sleutel]):
        if kandidaat in namen:
            return kandidaat
    return None


def _voeg_inline(p, tekst: str) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    for soort, t, url in inline_delen(tekst):
        if soort == "link":
            deel = p.part
            r_id = deel.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                  is_external=True)
            hl = OxmlElement("w:hyperlink")
            hl.set(qn("r:id"), r_id)
            run = OxmlElement("w:r")
            rpr = OxmlElement("w:rPr")
            stijl = OxmlElement("w:rStyle")
            stijl.set(qn("w:val"), "Hyperlink")
            u = OxmlElement("w:u")
            u.set(qn("w:val"), "single")
            kleur = OxmlElement("w:color")
            kleur.set(qn("w:val"), "1F6FB2")
            rpr.extend([stijl, kleur, u])
            run.append(rpr)
            tt = OxmlElement("w:t")
            tt.text = t
            tt.set(qn("xml:space"), "preserve")
            run.append(tt)
            hl.append(run)
            p._p.append(hl)
            continue
        run = p.add_run(t)
        if soort == "vet":
            run.bold = True
        elif soort == "cursief":
            run.italic = True
        elif soort == "code":
            run.font.name = "Consolas"


def _toc(doc, woorden: dict, kopstijl: str | None) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    doc.add_paragraph(woorden["inhoud"], style=kopstijl) if kopstijl else doc.add_paragraph(woorden["inhoud"])
    p = doc.add_paragraph()
    run = p.add_run()
    for soort, tekst in (("begin", None), (None, 'TOC \\o "1-3" \\h \\z \\u'), ("separate", None),
                         ("t", woorden["toc"]), ("end", None)):
        if soort in ("begin", "separate", "end"):
            fc = OxmlElement("w:fldChar")
            fc.set(qn("w:fldCharType"), soort)
            run._r.append(fc)
        elif soort == "t":
            t = OxmlElement("w:t")
            t.text = tekst
            run._r.append(t)
        else:
            it = OxmlElement("w:instrText")
            it.set(qn("xml:space"), "preserve")
            it.text = tekst
            run._r.append(it)
    instellingen = doc.settings.element
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    instellingen.append(upd)


def _beeldbreedte(doc):
    from docx.shared import Cm, Emu
    s = doc.sections[-1]
    beschikbaar = s.page_width - s.left_margin - s.right_margin
    return min(beschikbaar, Emu(Cm(16)))


def docx_generiek(meta: dict, bl: list[dict], template: Path, uit: Path, e: dict, genre: str | None) -> list[str]:
    from docx import Document
    from docx.enum.text import WD_BREAK
    from docx.shared import Pt, RGBColor
    taal = "en" if e["taal"] == "en" else "nl"
    w = WOORDEN[taal]
    waarsch: list[str] = []
    doc = Document(str(template))
    body = doc.element.body
    for el in list(body):
        if not el.tag.endswith("}sectPr"):
            body.remove(el)
    mp = e.get("stijlen") or {}
    st = {k: _stijlnaam(doc, k, mp) for k in STIJL_STANDAARD}
    for k in ("kop1", "kop2", "normaal"):
        if st[k] is None:
            waarsch.append(f"Template mist de stijl '{mp.get(k) or STIJL_STANDAARD[k]}'; dq template check helpt.")

    def para(tekst="", stijl=None):
        p = doc.add_paragraph(style=stijl) if stijl else doc.add_paragraph()
        if tekst:
            _voeg_inline(p, tekst)
        return p

    # titelblok
    if meta.get("titel"):
        para(meta["titel"], st["titel"])
        if meta.get("ondertitel"):
            para(meta["ondertitel"], st["ondertitel"])
        regel = " · ".join(x for x in (meta.get("auteur"), meta.get("organisatie"), meta.get("datum")) if x)
        regel2 = " · ".join(x for x in ((f"Versie {meta['versie']}" if meta.get("versie") else ""),
                                         meta.get("classificatie", "")) if x)
        for r in (regel, regel2):
            if r:
                p = para(r)
                for run in p.runs:
                    run.font.size = Pt(9.5)
                    run.font.color.rgb = RGBColor(0x59, 0x5F, 0x66)
    n_koppen = sum(1 for b in bl if b["type"] == "kop" and b["niveau"] <= 2)
    if genre in LANG_RAPPORT and n_koppen >= 6:
        _toc(doc, w, st["kop1"])
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    n_fig = n_tab = 0
    for b in bl:
        t = b["type"]
        if t == "kop":
            niveau = min(b["niveau"], 4)
            para(b["tekst"], st[f"kop{niveau}"] or st["normaal"])
        elif t == "alinea":
            para(b["tekst"], st["normaal"])
        elif t == "citaat":
            p = para(b["tekst"], st["citaat"] or st["normaal"])
            if not st["citaat"]:
                for run in p.runs:
                    run.italic = True
        elif t == "lijst":
            basis = st["lijst_nummer"] if b["genummerd"] else st["lijst_bullet"]
            for niveau, tekst in b["items"]:
                naam = basis
                if basis and niveau:
                    kandidaat = f"{basis} {min(niveau + 1, 3)}"
                    naam = kandidaat if kandidaat in {s.name for s in doc.styles} else basis
                p = para(tekst, naam)
                if not basis:
                    p.paragraph_format.left_indent = Pt(18 * (niveau + 1))
        elif t == "code":
            for regel in b["tekst"].splitlines() or [""]:
                p = doc.add_paragraph(style=st["code"]) if st["code"] else doc.add_paragraph()
                run = p.add_run(regel)
                if not st["code"]:
                    run.font.name = "Consolas"
                    run.font.size = Pt(9.5)
        elif t == "beeld":
            pad = Path(b["pad"])
            if not pad.is_file():
                waarsch.append(f"Beeld niet gevonden: {pad}")
                para(f"[{w['figuur']}: {b['bijschrift']}]", st["normaal"])
                continue
            if pad.suffix.lower() == ".svg":
                waarsch.append(f"SVG kan niet in .docx: {pad.name}. Zet hem om naar png.")
                continue
            n_fig += 1
            p = doc.add_paragraph()
            try:
                p.add_run().add_picture(str(pad), width=_beeldbreedte(doc))
            except Exception as ex:
                waarsch.append(f"Beeld {pad.name} niet in te voegen: {ex}")
            cap = para(f"{w['figuur']} {n_fig}. {b['bijschrift']}" if b["bijschrift"] else f"{w['figuur']} {n_fig}",
                       st["bijschrift"] or st["normaal"])
            if not st["bijschrift"]:
                for run in cap.runs:
                    run.italic = True
        elif t == "tabel":
            n_tab += 1
            titel = f"{w['tabel']} {n_tab}" + (f". {b['titel']}" if b.get("titel") else "")
            para(titel, st["bijschrift"] or st["normaal"])
            kolommen = max(len(b["kop"]), *(len(r) for r in b["rijen"])) if b["rijen"] else len(b["kop"])
            tabel = doc.add_table(rows=1, cols=kolommen)
            if st["tabel"]:
                tabel.style = doc.styles[st["tabel"]]
            for j, c in enumerate(b["kop"]):
                cel = tabel.rows[0].cells[j]
                cel.text = ""
                _voeg_inline(cel.paragraphs[0], f"**{c}**" if c else "")
            for rij in b["rijen"]:
                cellen = tabel.add_row().cells
                for j, c in enumerate(rij[:kolommen]):
                    cellen[j].text = ""
                    _voeg_inline(cellen[j].paragraphs[0], c)
            doc.add_paragraph()
        elif t == "pagina":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    _eerlijke_metadata(doc, meta)
    doc.save(str(uit))
    return waarsch


def _eerlijke_metadata(doc, meta: dict) -> None:
    cp = doc.core_properties
    nu = datetime.now(timezone.utc).replace(microsecond=0)
    cp.title = meta.get("titel", "")
    cp.author = meta.get("auteur", "")
    cp.last_modified_by = meta.get("auteur", "")
    cp.subject = meta.get("ondertitel", "")
    cp.comments = cp.keywords = cp.category = ""
    cp.revision = 1
    cp.created = cp.modified = nu


# ---------------------------------------------------------------- docx (APA)


def docx_apa(meta: dict, tekst: str, template: Path, uit: Path, e: dict) -> list[str]:
    from dutchquill import export_apa, md_docx
    # De APA-parser herkent de titelpagina aan een frontmatter-blok; zonder blok neemt hij de eerste kop als
    # titel. Links worden "tekst (url)" en geneste opsommingen één niveau (APA kent er maar één).
    tekst = re.sub(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", tekst)
    tekst = re.sub(r"(?m)^[ \t]+([-*+]|\d+[.)])\s+", r"\1 ", tekst)
    tekst = f"---\nTitel: {meta.get('titel', '')}\n---\n\n{tekst}"
    titel, bl, refs, fm, bijlagen = md_docx.parse_markdown(tekst)
    extra = {k: v for k, v in {
        "titel": meta.get("titel"), "ondertitel": meta.get("ondertitel"), "naam": meta.get("auteur"),
        "studentnummer": meta.get("studentnummer"), "instelling": meta.get("instelling"),
        "faculteit": meta.get("faculteit"), "opleiding": meta.get("opleiding"), "vak": meta.get("vak"),
        "begeleider": meta.get("begeleider"), "datum": meta.get("datum"),
    }.items() if v}
    profiel = md_docx._load_user_profile()
    payload = md_docx.build_payload(titel, bl, refs, extra, fm, bijlagen, user_profile=profiel)
    export_apa._build_warnings.clear()
    export_apa.build_document(payload, str(uit), template=str(template))
    return list(export_apa._build_warnings)


# ---------------------------------------------------------------- html, txt, md


def _template_fonts(template: Path | None) -> tuple[str, str]:
    try:
        from docx import Document
        d = Document(str(template))
        body = d.styles["Normal"].font.name or "Calibri"
        kop = d.styles["Heading 1"].font.name or body
        return body, kop
    except Exception:
        return "Calibri", "Calibri"


def html_maken(meta: dict, tekst: str, taal: str, template: Path | None) -> str:
    import markdown
    w = WOORDEN["en" if taal == "en" else "nl"]
    n = {"fig": 0}

    def figuur(m):
        n["fig"] += 1
        pad = Path(m.group(2))
        bron = m.group(2)
        if pad.is_file():
            mime = mimetypes.guess_type(pad.name)[0] or "image/png"
            bron = f"data:{mime};base64,{base64.b64encode(pad.read_bytes()).decode()}"
        cap = f"{w['figuur']} {n['fig']}." + (f" {html.escape(m.group(1))}" if m.group(1) else "")
        return f'\n<figure><img src="{bron}" alt="{html.escape(m.group(1))}"><figcaption>{cap}</figcaption></figure>\n'

    tekst = re.sub(r"(?m)^!\[([^\]]*)\]\(([^)]+)\)\s*$", figuur, tekst)
    lichaam = markdown.markdown(tekst, extensions=["tables", "fenced_code", "sane_lists"])
    body_font, kop_font = _template_fonts(template)
    kop = ""
    if meta.get("titel"):
        kop = f"<h1 class='titel'>{html.escape(meta['titel'])}</h1>"
        if meta.get("ondertitel"):
            kop += f"<p class='ondertitel'>{html.escape(meta['ondertitel'])}</p>"
        delen = (meta.get("auteur"), meta.get("organisatie"), meta.get("datum"))
        regel = " · ".join(html.escape(x) for x in delen if x)
        if regel:
            kop += f"<p class='meta'>{regel}</p>"
    css = f"""
    :root {{ --tekst: #22262a; --accent: #1f4e5f; --grijs: #595f66; --lijn: #d7dde2; }}
    body {{ font-family: '{body_font}', 'Segoe UI', Arial, sans-serif; color: var(--tekst); max-width: 46rem;
           margin: 2.5rem auto; padding: 0 1rem; line-height: 1.55; font-size: 11pt; background: #fff; }}
    h1, h2, h3, h4 {{ font-family: '{kop_font}', '{body_font}', Arial, sans-serif; color: var(--accent);
           line-height: 1.25; margin: 1.6em 0 .5em; }}
    h1.titel {{ font-size: 2em; margin-top: 0; }} .ondertitel {{ color: var(--grijs); font-size: 1.15em; margin: 0; }}
    .meta {{ color: var(--grijs); font-size: .9em; margin-bottom: 2em; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1em 0; font-size: .95em; }}
    th, td {{ border: 1px solid var(--lijn); padding: .35em .6em; text-align: left; vertical-align: top; }}
    th {{ background: #eef3f5; }}
    figure {{ margin: 1.2em 0; }} img {{ max-width: 100%; height: auto; }}
    figcaption {{ color: var(--grijs); font-style: italic; font-size: .9em; margin-top: .3em; }}
    blockquote {{ margin: 1em 0; padding-left: 1em; border-left: 3px solid var(--lijn); color: var(--grijs); }}
    pre, code {{ font-family: Consolas, Menlo, monospace; font-size: .92em; }}
    pre {{ background: #f4f6f8; padding: .8em; overflow-x: auto; }}
    @media print {{ body {{ margin: 0; max-width: none; }} }}
    """
    return (f"<!doctype html><html lang='{taal}'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
            f"<title>{html.escape(meta.get('titel', ''))}</title><style>{css}</style></head>"
            f"<body>{kop}{lichaam}</body></html>")


def txt_maken(meta: dict, bl: list[dict], taal: str) -> str:
    w = WOORDEN["en" if taal == "en" else "nl"]
    regels, n_fig, n_tab = [], 0, 0
    if meta.get("titel"):
        regels += [meta["titel"].upper(), ""]
    for b in bl:
        t = b["type"]
        if t == "kop":
            regels += ["", platte_tekst(b["tekst"]).upper() if b["niveau"] == 1 else platte_tekst(b["tekst"]), ""]
        elif t in ("alinea", "citaat"):
            regels += [platte_tekst(b["tekst"]), ""]
        elif t == "lijst":
            for i, (niveau, tekst) in enumerate(b["items"], 1):
                teken = f"{i}." if b["genummerd"] else "-"
                regels.append("  " * niveau + f"{teken} {platte_tekst(tekst)}")
            regels.append("")
        elif t == "code":
            regels += [b["tekst"], ""]
        elif t == "beeld":
            n_fig += 1
            regels += [f"[{w['figuur']} {n_fig}. {b['bijschrift']}]", ""]
        elif t == "tabel":
            n_tab += 1
            regels.append(f"{w['tabel']} {n_tab}" + (f". {b['titel']}" if b.get("titel") else ""))
            for rij in [b["kop"], *b["rijen"]]:
                regels.append(" | ".join(platte_tekst(c) for c in rij))
            regels.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(regels)).strip() + "\n"


# ---------------------------------------------------------------- pdf


def _browser() -> str | None:
    kandidaten = {
        "Darwin": ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                   "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                   "/Applications/Chromium.app/Contents/MacOS/Chromium",
                   "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"],
        "Windows": [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"],
    }.get(platform.system(), [])
    for k in kandidaten:
        if Path(k).exists():
            return k
    for naam in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge"):
        if shutil.which(naam):
            return shutil.which(naam)
    return None


def pdf_metadata(uit: Path, meta: dict) -> None:
    """Titel en auteur van de gebruiker; geen sporen van het gereedschap (browser, LibreOffice, pypdf)."""
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        return
    try:
        w = PdfWriter(clone_from=PdfReader(str(uit)))
        w.metadata = {"/Title": meta.get("titel", ""), "/Author": meta.get("auteur", ""),
                      "/Creator": "", "/Producer": ""}
        tmp = uit.with_suffix(".tmp.pdf")
        with open(tmp, "wb") as f:
            w.write(f)
        tmp.replace(uit)
    except Exception:  # noqa: BLE001 - metadata is bijzaak, de pdf zelf is goed
        pass


def pdf_maken(docx: Path | None, html_tekst: str, bl: list[dict], meta: dict, uit: Path, taal: str) -> tuple[str, list]:
    via, waarschuwingen = _pdf_route(docx, html_tekst, bl, meta, uit, taal)
    pdf_metadata(uit, meta)
    return via, waarschuwingen


def _pdf_route(docx: Path | None, html_tekst: str, bl: list[dict], meta: dict, uit: Path,
               taal: str) -> tuple[str, list]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice and docx and docx.is_file():
        with tempfile.TemporaryDirectory() as tmp:
            r = subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(docx)],
                               capture_output=True, timeout=180)
            kandidaat = Path(tmp) / (docx.stem + ".pdf")
            if r.returncode == 0 and kandidaat.is_file():
                shutil.move(str(kandidaat), uit)
                return "libreoffice", []
    browser = _browser()
    if browser:
        with tempfile.TemporaryDirectory() as tmp:
            h = Path(tmp) / "doc.html"
            h.write_text(html_tekst, encoding="utf-8")
            r = subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                                f"--print-to-pdf={uit}", h.as_uri()], capture_output=True, timeout=180)
            if uit.is_file() and uit.stat().st_size > 0:
                return "browser", ["PDF gemaakt via de browser: de opmaak volgt de html, "
                                   "niet precies de Word-template. "
                                   "Met LibreOffice volgt de pdf de template."]
    _pdf_reportlab(bl, meta, uit, taal)
    return "reportlab", ["PDF in eenvoudige opmaak (geen LibreOffice of Chrome gevonden)."]


def _pdf_reportlab(bl: list[dict], meta: dict, uit: Path, taal: str) -> None:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image,
        ListFlowable,
        ListItem,
        Paragraph,
        Preformatted,
        SimpleDocTemplate,
        Spacer,
        Table,
    )
    w = WOORDEN["en" if taal == "en" else "nl"]
    ss = getSampleStyleSheet()

    def rl(tekst):
        uit_ = ""
        for soort, t, url in inline_delen(tekst):
            t = html.escape(t)
            uit_ += {"vet": f"<b>{t}</b>", "cursief": f"<i>{t}</i>", "code": f"<font face='Courier'>{t}</font>",
                     "link": f"<link href='{html.escape(url or '')}' color='blue'>{t}</link>"}.get(soort, t)
        return uit_

    verhaal = []
    if meta.get("titel"):
        verhaal += [Paragraph(html.escape(meta["titel"]), ss["Title"])]
    n_fig = n_tab = 0
    for b in bl:
        t = b["type"]
        if t == "kop":
            verhaal.append(Paragraph(rl(b["tekst"]), ss[f"Heading{min(b['niveau'], 4)}"]))
        elif t == "alinea":
            verhaal.append(Paragraph(rl(b["tekst"]), ss["BodyText"]))
        elif t == "citaat":
            verhaal.append(Paragraph(f"<i>{rl(b['tekst'])}</i>", ss["BodyText"]))
        elif t == "lijst":
            verhaal.append(ListFlowable([ListItem(Paragraph(rl(x), ss["BodyText"])) for _, x in b["items"]],
                                        bulletType="1" if b["genummerd"] else "bullet"))
        elif t == "code":
            verhaal.append(Preformatted(b["tekst"], ss["Code"]))
        elif t == "beeld" and Path(b["pad"]).is_file() and not b["pad"].endswith(".svg"):
            n_fig += 1
            img = Image(b["pad"])
            schaal = min(1.0, (16 * cm) / img.drawWidth)
            img.drawWidth, img.drawHeight = img.drawWidth * schaal, img.drawHeight * schaal
            verhaal += [img, Paragraph(f"<i>{w['figuur']} {n_fig}. {html.escape(b['bijschrift'])}</i>", ss["BodyText"])]
        elif t == "tabel":
            n_tab += 1
            titel = f"{w['tabel']} {n_tab}" + (f". {html.escape(b['titel'])}" if b.get("titel") else "")
            verhaal.append(Paragraph(f"<i>{titel}</i>", ss["BodyText"]))
            data = [[Paragraph(rl(c), ss["BodyText"]) for c in rij] for rij in [b["kop"], *b["rijen"]]]
            tab = Table(data, repeatRows=1)
            tab.setStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                          ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef3f5"))])
            verhaal.append(tab)
        verhaal.append(Spacer(1, 4))
    doc = SimpleDocTemplate(str(uit), pagesize=A4, title=meta.get("titel", ""), author=meta.get("auteur", ""),
                            creator="", producer="", subject="")
    doc.build(verhaal)


# ---------------------------------------------------------------- hoofdlijn


def exporteer(bron: Path, naam: str, map_: Path | None = None, formaten: list[str] | None = None,
              template: str | None = None, genre: str | None = None, profiel: str | None = None,
              sets: list[str] | None = None) -> dict:
    e = effectief(genre, profiel, sets)
    formaten = formaten or e["uitvoer"]["formaten"]
    onbekend = [f for f in formaten if f not in FORMATEN]
    if onbekend:
        raise ExportFout(f"Onbekend formaat: {', '.join(onbekend)}. Kies uit: {', '.join(FORMATEN)}.")
    map_ = map_ or bron.parent
    map_.mkdir(parents=True, exist_ok=True)
    meta, tekst = lees_bron(bron)
    taal = e["taal"] if e["taal"] in ("nl", "en") else "nl"
    st = e.get("student") or {}
    if e["controles"].get("apa") and not meta.get("auteur"):
        meta["auteur"] = " ".join(x for x in (st.get("voornaam"), st.get("tussenvoegsel"), st.get("achternaam")) if x)
    meta.setdefault("datum", datum_nl(date.today()) if taal == "nl" else date.today().strftime("%-d %B %Y"
                    if platform.system() != "Windows" else "%d %B %Y"))
    if not meta.get("titel"):
        meta["titel"] = naam
    apa = bool(e["controles"].get("apa"))
    tpl = template_pad(template or ("apa-hbo" if apa and not template and e["uitvoer"].get("template") in
                                    (None, "zakelijk", "notitie") else None), e)
    bl = blokken(tekst)
    veilig = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", naam).strip() or "document"
    resultaat: dict = {"map": str(map_), "template": str(tpl), "apa": apa, "bestanden": [], "waarschuwingen": []}

    docx_pad = map_ / f"{veilig}.docx"
    tijdelijke_docx = None
    if "docx" in formaten or ("pdf" in formaten and (shutil.which("soffice") or shutil.which("libreoffice"))):
        doel = docx_pad if "docx" in formaten else Path(tempfile.mkdtemp()) / f"{veilig}.docx"
        if "docx" not in formaten:
            tijdelijke_docx = doel
        w = docx_apa(meta, tekst, tpl, doel, e) if apa else docx_generiek(meta, bl, tpl, doel, e, genre)
        resultaat["waarschuwingen"] += w
        if "docx" in formaten:
            resultaat["bestanden"].append(str(doel))
    html_tekst = html_maken(meta, tekst, taal, tpl) if ("html" in formaten or "pdf" in formaten) else ""
    if "html" in formaten:
        p = map_ / f"{veilig}.html"
        p.write_text(html_tekst, encoding="utf-8")
        resultaat["bestanden"].append(str(p))
    if "pdf" in formaten:
        p = map_ / f"{veilig}.pdf"
        via, w = pdf_maken(docx_pad if docx_pad.is_file() else tijdelijke_docx, html_tekst, bl, meta, p, taal)
        resultaat["pdf_via"] = via
        resultaat["waarschuwingen"] += w
        resultaat["bestanden"].append(str(p))
    if "md" in formaten:
        p = map_ / f"{veilig}.md"
        if p.resolve() != bron.resolve():
            fm = "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in meta.items())
            p.write_text(f"---\n{fm}---\n\n{tekst}", encoding="utf-8")
        resultaat["bestanden"].append(str(p))
    if "txt" in formaten:
        p = map_ / f"{veilig}.txt"
        p.write_text(txt_maken(meta, bl, taal), encoding="utf-8")
        resultaat["bestanden"].append(str(p))
    if tijdelijke_docx and tijdelijke_docx.exists():
        shutil.rmtree(tijdelijke_docx.parent, ignore_errors=True)
    return resultaat


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq export", description="Markdown naar docx, pdf, html, md en txt")
    p.add_argument("--bron", required=True)
    p.add_argument("--naam", required=True, help="Bestandsnaam zonder extensie (meestal de titel)")
    p.add_argument("--map", help="Uitvoermap (standaard: de map van de bron)")
    p.add_argument("--formaten", help="Komma-gescheiden; standaard uit de config (uitvoer.formaten)")
    p.add_argument("--template")
    p.add_argument("--genre")
    p.add_argument("--profiel")
    p.add_argument("--set", action="append", default=[])
    a = p.parse_args(argv)
    try:
        r = exporteer(Path(a.bron).expanduser(), a.naam, Path(a.map).expanduser() if a.map else None,
                      [f.strip() for f in a.formaten.split(",")] if a.formaten else None,
                      a.template, a.genre, a.profiel, a.set)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    except (ExportFout, ConfigFout, FileNotFoundError) as e:
        print(f"DutchQuill: {e}", file=sys.stderr)
        sys.exit(2)

