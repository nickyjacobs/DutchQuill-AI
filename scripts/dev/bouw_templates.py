"""Bouw de meegeleverde .docx-templates opnieuw (alleen voor onderhoud aan de plugin).

  uv run --no-project --with-requirements requirements.txt python scripts/dev/bouw_templates.py

Maakt templates/docx/apa-hbo.docx (de APA-opmaak uit export_apa.setup_document), zakelijk.docx, notitie.docx en
review.docx (voor review- en humaniseringsrapporten).
Pas je de opmaak aan, draai dit script dan opnieuw en commit de .docx-bestanden.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from docx import Document  # noqa: E402
from docx.enum.style import WD_STYLE_TYPE  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt, RGBColor  # noqa: E402
from dutchquill import export_apa  # noqa: E402

TEAL = RGBColor(0x1F, 0x4E, 0x5F)
ACCENT = RGBColor(0x2A, 0x9D, 0xAF)
GRIJS = RGBColor(0x59, 0x5F, 0x66)
DOEL = ROOT / "templates" / "docx"


def leeg(doc: Document) -> None:
    body = doc.element.body
    for el in list(body):
        if not el.tag.endswith("}sectPr"):
            body.remove(el)
    cp = doc.core_properties
    for veld in ("author", "last_modified_by", "comments", "subject", "category", "keywords", "title"):
        setattr(cp, veld, "")
    cp.revision = 1


def stijl(doc, naam, font=None, size=None, bold=None, italic=None, color=None, before=None, after=None,
          spacing=None, align=None, indent=None, base="Normal", soort=WD_STYLE_TYPE.PARAGRAPH):
    try:
        s = doc.styles[naam]
    except KeyError:
        s = doc.styles.add_style(naam, soort)
        s.base_style = doc.styles[base]
    f = s.font
    if font:
        f.name = font
        rpr = s.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attr), font)
        for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if rfonts.get(qn(attr)) is not None:
                del rfonts.attrib[qn(attr)]
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if italic is not None:
        f.italic = italic
    if color is not None:
        f.color.rgb = color
    pf = s.paragraph_format
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if spacing is not None:
        pf.line_spacing = spacing
    if align is not None:
        pf.alignment = align
    if indent is not None:
        pf.left_indent = Cm(indent)
    return s


def zonder_rand(s) -> None:
    """De standaard Title-stijl van python-docx heeft een lijn eronder; die willen we niet."""
    ppr = s.element.get_or_add_pPr()
    for rand in ppr.findall(qn("w:pBdr")):
        ppr.remove(rand)


def paginanummer(sectie, tekst_voor: str = "") -> None:
    p = sectie.footer.paragraphs[0] if sectie.footer.paragraphs else sectie.footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if tekst_voor:
        r = p.add_run(tekst_voor)
        r.font.size = Pt(9)
        r.font.color.rgb = GRIJS
    export_apa.add_field_code(p, " PAGE ")
    for r in p.runs:
        r.font.size = Pt(9)
        r.font.color.rgb = GRIJS


def a4(doc, marge=2.5):
    s = doc.sections[0]
    s.page_width, s.page_height = Cm(21.0), Cm(29.7)
    s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Cm(marge)
    return s


def apa_hbo() -> None:
    doc = Document()
    export_apa.setup_document(doc, export_apa.get_font_config("times"))
    zonder_rand(stijl(doc, "Title", font="Times New Roman", size=12, bold=True, color=RGBColor(0, 0, 0),
                      align=WD_ALIGN_PARAGRAPH.CENTER))
    stijl(doc, "Caption", font="Times New Roman", size=12, bold=False, italic=True, color=RGBColor(0, 0, 0))
    leeg(doc)
    doc.save(DOEL / "apa-hbo.docx")


def zakelijk(naam: str, body: float, titel: float, h1: float, h2: float, h3: float, regel: float, na: float,
             marge: float, voettekst: str = "") -> None:
    doc = Document()
    sectie = a4(doc, marge)
    stijl(doc, "Normal", font="Calibri", size=body, after=na, spacing=regel, color=RGBColor(0x22, 0x26, 0x2A))
    t = stijl(doc, "Title", font="Calibri", size=titel, bold=True, color=TEAL, after=4)
    zonder_rand(t)
    stijl(doc, "Subtitle", font="Calibri", size=body + 2, italic=False, color=GRIJS, after=14)
    stijl(doc, "Heading 1", font="Calibri", size=h1, bold=True, color=TEAL, before=h1 + 2, after=6)
    stijl(doc, "Heading 2", font="Calibri", size=h2, bold=True, color=TEAL, before=12, after=4)
    stijl(doc, "Heading 3", font="Calibri", size=h3, bold=True, color=RGBColor(0x33, 0x3A, 0x40), before=10, after=3)
    stijl(doc, "Heading 4", font="Calibri", size=body, bold=True, italic=True, color=RGBColor(0x33, 0x3A, 0x40),
          before=8, after=2)
    stijl(doc, "Caption", font="Calibri", size=body - 2, italic=True, bold=False, color=GRIJS, after=10)
    stijl(doc, "Quote", font="Calibri", size=body, italic=True, color=GRIJS, indent=1)
    code = stijl(doc, "Code", font="Consolas", size=body - 1.5, after=0, spacing=1.0)
    code.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    stijl(doc, "List Bullet", font="Calibri", size=body)
    stijl(doc, "List Number", font="Calibri", size=body)
    paginanummer(sectie, voettekst)
    leeg(doc)
    doc.save(DOEL / f"{naam}.docx")


if __name__ == "__main__":
    DOEL.mkdir(parents=True, exist_ok=True)
    apa_hbo()
    zakelijk("zakelijk", body=11, titel=26, h1=16, h2=13, h3=11.5, regel=1.15, na=8, marge=2.5)
    zakelijk("notitie", body=10.5, titel=18, h1=13, h2=11.5, h3=10.5, regel=1.05, na=5, marge=2.0)
    zakelijk("review", body=10.5, titel=20, h1=14, h2=12, h3=10.5, regel=1.1, na=6, marge=2.0,
             voettekst="DutchQuill-review  ·  ")
    print("\n".join(str(p) for p in sorted(DOEL.glob("*.docx"))))
