import json
import sys
from pathlib import Path

from docx import Document
from dutchquill import export, reviewgrafiek, tells

F = Path(__file__).parent / "fixtures"


def test_waarden_komen_uit_tells():
    tekst = (F / "rapport_moeilijk_nl.md").read_text(encoding="utf-8")
    r = tells.analyseer(tekst, taal="nl", genre="rapport")
    w = reviewgrafiek.waarden(r, taalronde=2, oordeel="Kleine aanpassingen")
    assert w["niveau"] == r["niveau"] and w["score_per_1000"] == r["score_per_1000"]
    assert w["flesch"] == r["statistiek"]["flesch"] and w["mattr"] is None  # onder 300 woorden niet getoond
    assert w["patronen"] == sum(1 for b in r["bevindingen"] if b["punten"] > 0)
    assert w["top"][0]["cat"] == "leesbaarheid" and w["top"][0]["punten"] == 2
    assert w["acceptatie"] and w["acceptatie"]["voldaan"] is False
    assert w["taalronde"] == 2 and w["oordeel"] == "Kleine aanpassingen"


def test_png_via_cli(tmp_path, capsys, monkeypatch):
    uit = tmp_path / "grafiek" / "overzicht.png"
    monkeypatch.setattr(sys, "argv", ["dq reviewgrafiek", "--input", str(F / "ai_en.md"), "--output", str(uit),
                                      "--genre", "memo", "--json"])
    reviewgrafiek.main()
    r = json.loads(capsys.readouterr().out)
    assert uit.is_file() and r["png"].endswith("overzicht.png") and r["taal"] == "en"
    from PIL import Image
    with Image.open(uit) as im:
        assert im.size == (1800, 840)


def test_reviewexport_nooit_apa(tmp_path):
    png = reviewgrafiek.teken(reviewgrafiek.waarden(tells.analyseer("Een korte tekst.", taal="nl")),
                              tmp_path / "overzicht.png")
    bron = tmp_path / "bron.md"
    bron.write_text(f"# Review: Test\n\n![Overzicht]({png.name})\n\n## Eindoordeel\n\nKleine aanpassingen.\n",
                    encoding="utf-8")
    r = export.exporteer(bron, "Review Test", tmp_path / "uit", ["docx"], template="review",
                         sets=["controles.apa=true"])
    assert r["apa"] is False and r["template"].endswith("review.docx")
    doc = Document(r["bestanden"][0])
    assert len(doc.inline_shapes) == 1
    assert "Inhoudsopgave" not in [p.text for p in doc.paragraphs]
