from datetime import datetime, timezone
from pathlib import Path

import pytest
from docx import Document
from dutchquill import config, export, templates_docx
from dutchquill.paden import root

BRON = """---
titel: Fietsgebruik onder studenten
auteur: Jan Jansen
---

# Samenvatting

In 2025 fietste 27% van de studenten dagelijks.

*Sleutelwoorden:* fietsen, studenten

# Inleiding

Zie het [CBS](https://www.cbs.nl) voor **cijfers**.

- punt een
  - punt twee

![Fietsers per maand](beeld.png)

**Tabel 1**
*Per opleiding*

| Opleiding | Dagelijks |
|---|---|
| ICT | 24% |

# Literatuurlijst

Jansen, J. (2024). *Fietsen*. Uitgever.
"""


@pytest.fixture
def bron(tmp_path):
    from PIL import Image
    Image.new("RGB", (400, 200), "teal").save(tmp_path / "beeld.png")
    p = tmp_path / "bron.md"
    p.write_text(BRON, encoding="utf-8")
    return p


def stijlen(pad):
    return [p.style.name for p in Document(str(pad)).paragraphs]


def test_generiek_alle_formaten(bron, tmp_path, monkeypatch):
    monkeypatch.setattr(export, "_browser", lambda: None)
    monkeypatch.setattr(export.shutil, "which", lambda _: None)
    r = export.exporteer(bron, "Fiets", tmp_path / "uit", ["docx", "pdf", "html", "md", "txt"],
                         genre="zakelijk-rapport")
    namen = sorted(Path(b).name for b in r["bestanden"])
    assert namen == ["Fiets.docx", "Fiets.html", "Fiets.md", "Fiets.pdf", "Fiets.txt"]
    assert r["pdf_via"] == "reportlab"
    doc = Document(r["bestanden"][0])
    tekst = [p.text for p in doc.paragraphs]
    assert "Figuur 1. Fietsers per maand" in tekst and "Tabel 1. Per opleiding" in tekst
    assert {"Title", "Heading 1", "List Bullet", "List Bullet 2", "Caption"} <= set(stijlen(r["bestanden"][0]))
    cp = doc.core_properties
    assert cp.author == "Jan Jansen" and cp.revision == 1 and cp.title == "Fietsgebruik onder studenten"
    assert abs((datetime.now(timezone.utc) - cp.created.replace(tzinfo=timezone.utc)).total_seconds()) < 120
    html = (tmp_path / "uit" / "Fiets.html").read_text()
    assert "<figcaption>Figuur 1. Fietsers per maand</figcaption>" in html and "data:image/png;base64" in html
    assert "Figuur 1. Fietsers per maand" in (tmp_path / "uit" / "Fiets.txt").read_text()
    pdf = (tmp_path / "uit" / "Fiets.pdf").read_bytes()
    assert b"/Producer (ReportLab" not in pdf and b"/Creator (ReportLab" not in pdf


def test_apa_volgorde_en_eerlijke_metadata(bron, tmp_path):
    r = export.exporteer(bron, "Fiets APA", tmp_path / "apa", ["docx"], genre="rapport",
                         sets=["controles.apa=true"])
    doc = Document(r["bestanden"][0])
    tekst = [p.text for p in doc.paragraphs if p.text.strip()]
    assert tekst.index("Samenvatting") < tekst.index("Inhoudsopgave") < tekst.index("Literatuurlijst")
    assert any("CBS (https://www.cbs.nl)" in t for t in tekst)
    assert any(t.endswith("punt twee") for t in tekst)
    assert doc.core_properties.revision == 1


def test_apa_template_gelijk_aan_code(tmp_path):
    from dutchquill import export_apa
    payload = {"metadata": {"title": "T"}, "body": [{"type": "paragraph", "text": "x"}]}
    export_apa.build_document(payload, str(tmp_path / "code.docx"))
    export_apa.build_document(payload, str(tmp_path / "tpl.docx"), template=str(root() / "templates/docx/apa-hbo.docx"))
    a, b = Document(str(tmp_path / "code.docx")), Document(str(tmp_path / "tpl.docx"))
    for naam in ("Normal", "Heading 1", "Heading 2", "Heading 3"):
        sa, sb = a.styles[naam], b.styles[naam]
        assert (sa.font.name, sa.font.size, sa.font.bold, sa.paragraph_format.alignment) == \
               (sb.font.name, sb.font.size, sb.font.bold, sb.paragraph_format.alignment), naam
    assert a.sections[0].left_margin == b.sections[0].left_margin
    assert a.styles["Normal"].paragraph_format.line_spacing == b.styles["Normal"].paragraph_format.line_spacing


def test_eigen_template_met_nederlandse_stijlnamen(werkmap, bron, tmp_path):
    doc = Document()
    for naam in ("Heading 1", "Heading 2"):  # een eigen template met alleen Nederlandse kopnamen
        el = doc.styles[naam].element
        el.getparent().remove(el)
    for naam in ("Kop 1", "Kop 2"):
        doc.styles.add_style(naam, 1)
    tpl = werkmap / "templates" / "huisstijl.docx"
    doc.save(tpl)
    config.zet("templates.huisstijl", {"bestand": "templates/huisstijl.docx", "soort": "docx"})
    c = templates_docx.check("huisstijl")
    assert c["voorstel_mapping"]["kop1"] == "Kop 1"
    config.zet("stijlen.kop1", "Kop 1")
    r = export.exporteer(bron, "Huis", tmp_path / "h", ["docx"], template="huisstijl")
    assert "Kop 1" in stijlen(r["bestanden"][0])


def test_template_aanpassen(werkmap):
    r = templates_docx.aanpas("zakelijk", "mijn-blauw", ["kop1.font=Arial", "kop1.grootte=14", "kop1.kleur=1F4E79",
                                                          "normaal.regelafstand=1.5"], 2.0, "Blauwe koppen")
    doc = Document(r["bestand"])
    h1 = doc.styles["Heading 1"]
    assert h1.font.name == "Arial" and h1.font.size.pt == 14 and str(h1.font.color.rgb) == "1F4E79"
    assert config.effectief()["templates"]["mijn-blauw"]["beschrijving"] == "Blauwe koppen"
    assert any(t["naam"] == "mijn-blauw" for t in templates_docx.lijst())
    with pytest.raises(config.ConfigFout):
        templates_docx.aanpas("zakelijk", "mijn-blauw", [], None, None)


def test_onbekend_formaat_en_template(bron):
    with pytest.raises(export.ExportFout):
        export.exporteer(bron, "x", formaten=["odt"])
    with pytest.raises(export.ExportFout):
        export.exporteer(bron, "x", formaten=["docx"], template="bestaat-niet")


@pytest.mark.parametrize("apa", [False, True])
def test_metadata_leeg(bron, tmp_path, monkeypatch, apa):
    import zipfile

    from pypdf import PdfReader
    monkeypatch.setattr(export, "_browser", lambda: None)
    monkeypatch.setattr(export.shutil, "which", lambda _: None)
    r = export.exporteer(bron, "Fiets", tmp_path / "uit", ["docx", "pdf"], genre="rapport",
                         sets=["uitvoer.metadata=leeg", f"controles.apa={str(apa).lower()}"])
    assert r["metadata"] == "leeg"
    docx = tmp_path / "uit" / "Fiets.docx"
    cp = Document(str(docx)).core_properties
    assert (cp.author, cp.last_modified_by, cp.title, cp.subject, cp.keywords, cp.comments) == ("",) * 6
    assert cp.revision == 1  # niets verzonnen: de standaard van python-docx
    with zipfile.ZipFile(docx) as z:
        props = z.read("docProps/app.xml").decode() + z.read("docProps/core.xml").decode()
    for spoor in ("Jan Jansen", "Fietsgebruik", "Microsoft", "Normal.dotm", "python-docx"):
        assert spoor not in props, spoor
    info = PdfReader(str(tmp_path / "uit" / "Fiets.pdf")).metadata or {}
    assert not info.get("/Title") and not info.get("/Author") and not info.get("/Producer")
    assert not info.get("/Creator")


def test_metadata_normaal_houdt_titel_en_auteur(bron, tmp_path, monkeypatch):
    from pypdf import PdfReader
    monkeypatch.setattr(export, "_browser", lambda: None)
    monkeypatch.setattr(export.shutil, "which", lambda _: None)
    export.exporteer(bron, "Fiets", tmp_path / "uit", ["pdf"], genre="zakelijk-rapport")
    info = PdfReader(str(tmp_path / "uit" / "Fiets.pdf")).metadata
    assert info["/Title"] == "Fietsgebruik onder studenten" and info["/Author"] == "Jan Jansen"
