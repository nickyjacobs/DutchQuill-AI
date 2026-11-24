import json
from pathlib import Path

import pytest
from dutchquill import beeld, extraheer, materiaal


@pytest.fixture
def bestanden(tmp_path):
    """Een set echte invoerbestanden van elk type."""
    d = tmp_path / "in"
    d.mkdir()
    from docx import Document
    doc = Document()
    doc.core_properties.author = "Jan Jansen"
    doc.add_heading("Onderzoek naar fietsgebruik", 1)
    doc.add_paragraph("In 2025 fietste 27 procent van de studenten dagelijks naar de campus.")
    doc.save(d / "rapport.docx")

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(str(d / "bron.pdf"), pagesize=A4)
    c.setAuthor("CBS")
    c.drawString(72, 750, "Pagina een: het aantal fietsen steeg met 12 procent.")
    c.showPage()
    c.drawString(72, 750, "Pagina twee: zie https://www.cbs.nl/fiets voor de cijfers.")
    c.save()

    from pptx import Presentation
    pr = Presentation()
    dia = pr.slides.add_slide(pr.slide_layouts[1])
    dia.shapes.title.text = "Resultaten"
    dia.placeholders[1].text = "Meer fietsers in de winter"
    dia.notes_slide.notes_text_frame.text = "Spreeknotitie"
    pr.save(d / "dia.pptx")

    from openpyxl import Workbook
    wb = Workbook()
    wb.active.title = "Cijfers"
    wb.active.append(["Jaar", "Fietsers"])
    wb.active.append([2025, 270])
    wb.save(d / "cijfers.xlsx")

    (d / "data.csv").write_text("naam;waarde\na;1\nb;2\n", encoding="utf-8")
    (d / "artikel.html").write_text(
        "<html><head><title>Fietsen in NL</title><meta name='author' content='Fietsersbond'>"
        "<meta property='article:published_time' content='2026-03-01T10:00'></head><body>"
        "<nav>Menu Home</nav><h1>Kop</h1><p>Eerste alinea &amp; meer.</p><script>var x=1;</script>"
        "<ul><li>punt een</li></ul><footer>Cookies</footer></body></html>", encoding="utf-8")
    (d / "notitie.md").write_text("# Idee\nZie https://example.org/a en verder.\n", encoding="utf-8")
    (d / "link.webloc").write_bytes(
        b'<?xml version="1.0" encoding="UTF-8"?><plist version="1.0"><dict><key>URL</key>'
        b"<string>https://example.org/webloc</string></dict></plist>")

    from PIL import Image
    img = Image.new("RGB", (3000, 1000), "red")
    exif = Image.Exif()
    exif[0x010F] = "CameraMerk"  # Make
    img.save(d / "foto.jpg", exif=exif)
    Image.new("RGBA", (200, 400), (0, 0, 255, 128)).save(d / "schets.webp")
    return d


def test_extraheer_alle_soorten(bestanden, tmp_path):
    uit = tmp_path / "uit"
    r = {p.name: extraheer.extraheer(p, uit) for p in bestanden.iterdir()}
    assert r["rapport.docx"]["metadata"]["auteur"] == "Jan Jansen"
    assert "27 procent" in Path(r["rapport.docx"]["uitvoer"]).read_text()
    pdf = Path(r["bron.pdf"]["uitvoer"]).read_text()
    assert "[pagina 1]" in pdf and "[pagina 2]" in pdf and r["bron.pdf"]["paginas"] == 2
    assert r["bron.pdf"]["metadata"]["auteur"] == "CBS"
    assert "https://www.cbs.nl/fiets" in r["bron.pdf"]["urls"]
    dia = Path(r["dia.pptx"]["uitvoer"]).read_text()
    assert "## Dia 1: Resultaten" in dia and "Meer fietsers" in dia and "Spreeknotitie" in dia
    assert "| Jaar | Fietsers |" in Path(r["cijfers.xlsx"]["uitvoer"]).read_text()
    assert "| naam | waarde |" in Path(r["data.csv"]["uitvoer"]).read_text()
    html = Path(r["artikel.html"]["uitvoer"]).read_text()
    assert "# Kop" in html and "Eerste alinea & meer." in html and "- punt een" in html
    assert "Menu" not in html and "var x" not in html and "Cookies" not in html
    assert r["artikel.html"]["metadata"] == {"titel": "Fietsen in NL", "auteur": "Fietsersbond",
                                             "gepubliceerd": "2026-03-01"}
    assert r["notitie.md"]["urls"] == ["https://example.org/a"]
    assert r["link.webloc"]["urls"] == ["https://example.org/webloc"]
    assert "overgeslagen" in r["foto.jpg"]


def test_kapot_bestand_stopt_niet(tmp_path):
    kapot = tmp_path / "kapot.docx"
    kapot.write_bytes(b"geen zip")
    r = extraheer.extraheer(kapot, tmp_path / "uit")
    assert "fout" in r


def test_beeld_normaliseren(bestanden, tmp_path):
    from PIL import Image
    r = beeld.normaliseer(bestanden / "foto.jpg", tmp_path / "b", max_zijde=1200)
    assert r["verkleind"] and r["breedte"] == 1200 and r["orientatie"] == "liggend"
    with Image.open(r["pad"]) as img:
        assert not img.getexif()
    r = beeld.normaliseer(bestanden / "schets.webp", tmp_path / "b")
    assert r["formaat"] == "png" and r["orientatie"] == "staand"
    assert (bestanden / "foto.jpg").stat().st_size > 0  # origineel blijft


def test_inventaris_en_verzamel(werkmap, bestanden):
    import shutil
    shutil.copy(bestanden / "rapport.docx", werkmap / "1-input" / "rapporten")
    shutil.copy(bestanden / "bron.pdf", werkmap / "1-input" / "bronnen")
    shutil.copy(bestanden / "foto.jpg", werkmap / "1-input" / "beeld")
    (werkmap / "1-input" / "mijn-stijl" / "blog.md").write_text("Mijn eigen tekst.")
    inv = materiaal.inventaris()
    assert {i["rel"] for i in inv if i["nieuw"]} == {
        "1-input/rapporten/rapport.docx", "1-input/bronnen/bron.pdf", "1-input/beeld/foto.jpg",
        "1-input/mijn-stijl/blog.md"}

    m = materiaal.verzamel("Fietsrapport")
    namen = {Path(b["bron"]).name for b in m["bestanden"]}
    assert namen == {"rapport.docx", "bron.pdf"}  # mijn-stijl niet, beeld apart
    assert len(m["beelden"]) == 1 and m["totaal_woorden"] > 10
    assert json.loads((Path(m["map"]) / "manifest.json").read_text())["opdracht"] == "Fietsrapport"

    # tweede keer: niets nieuw behalve mijn-stijl (die niet meedoet)
    assert materiaal.verzamel("Fietsrapport")["bestanden"] == []
    (werkmap / "1-input" / "notities" / "extra.md").write_text("Nieuwe notitie")
    m2 = materiaal.verzamel("Fietsrapport")
    assert [Path(b["bron"]).name for b in m2["bestanden"]] == ["extra.md"]
    assert len(materiaal.verzamel("Alles", keuze="alles")["bestanden"]) == 3


def test_schone_urls():
    urls = ["http://10.0.0.23.", "https://nmap.org/.", "http://localhost:8080/x", "https://a.local/b",
            "https://cwe.mitre.org)", "http://192.168.1.1/", "https://8.8.8.8/x"]
    assert extraheer.schone_urls(urls) == ["https://8.8.8.8/x", "https://cwe.mitre.org", "https://nmap.org/"]


def test_aangeleverde_en_genoemde_links(werkmap):
    (werkmap / "1-input" / "bronnen" / "links.md").write_text("- https://example.org/bron\n")
    (werkmap / "1-input" / "notities" / "n.md").write_text("Zie https://example.org/genoemd\n")
    m = materiaal.verzamel("x")
    assert m["urls"] == ["https://example.org/bron"]
    assert m["urls_genoemd"] == ["https://example.org/genoemd"]
