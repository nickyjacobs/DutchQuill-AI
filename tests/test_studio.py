import base64
import json
import threading
import urllib.error
import urllib.request

import pytest
from dutchquill import config, paden
from dutchquill.studio import server


@pytest.fixture
def studio():
    s = server.start(open_browser=False)
    t = threading.Thread(target=s.server.serve_forever, daemon=True)
    t.start()
    yield s
    s.server.shutdown()


def vraag(s, methode, pad, body=None, token=True, host=None, origin=None):
    req = urllib.request.Request(f"http://127.0.0.1:{s.poort}{pad}", method=methode,
                                 data=json.dumps(body).encode() if body is not None else None)
    if token:
        req.add_header("X-DQ-Token", s.token)
    if host:
        req.add_header("Host", host)
    if origin:
        req.add_header("Origin", origin)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"{}") if pad.startswith("/api") else r.read()
    except urllib.error.HTTPError as e:
        inhoud = e.read()
        return e.code, (json.loads(inhoud) if inhoud.startswith(b"{") else inhoud)


def test_beveiliging(studio):
    assert vraag(studio, "GET", "/api/status", token=False)[0] == 403
    assert vraag(studio, "GET", "/api/status", host="evil.example:80")[0] == 403
    assert vraag(studio, "POST", "/api/klaar", {}, origin="https://evil.example")[0] == 403
    status, html = vraag(studio, "GET", "/")
    assert status == 200 and b"DutchQuill Studio" in html
    assert vraag(studio, "GET", "/../../config.py")[0] == 404


def test_installatie_en_opslaan(studio, tmp_path):
    status, st = vraag(studio, "GET", "/api/status")
    assert status == 200 and st["ingesteld"] is False
    assert vraag(studio, "POST", "/api/werkmap", {"pad": "/etc/dq"})[0] == 400
    pad = tmp_path / "DutchQuill"
    status, r = vraag(studio, "POST", "/api/werkmap", {"pad": str(pad), "taal": "nl", "profiel": "student"})
    assert status == 200 and (pad / "dutchquill.yaml").is_file()
    _, c = vraag(studio, "GET", "/api/config")
    ruw = c["ruw"]
    ruw["profielen"] = {"mijn-linkedin": {"basis": "social", "toon": {"niveau": "luchtig"}}}
    ruw["profiel"] = "mijn-linkedin"
    _, v = vraag(studio, "POST", "/api/config/voorbeeld", {"ruw": ruw})
    assert v["fouten"] == [] and any("mijn-linkedin" in s for s in v["samenvatting"])
    slecht = json.loads(json.dumps(ruw))
    slecht["profielen"]["mijn-linkedin"]["toon"]["niveau"] = "superformeel"
    assert vraag(studio, "POST", "/api/config/opslaan", {"ruw": slecht})[0] == 400
    assert vraag(studio, "POST", "/api/config/opslaan", {"ruw": ruw})[0] == 200
    tekst = (pad / "dutchquill.yaml").read_text()
    assert "# Taal: nl, en of auto" in tekst  # commentaar is bewaard
    assert config.effectief()["toon"]["niveau"] == "luchtig"


def test_uploads(studio, tmp_path):
    vraag(studio, "POST", "/api/werkmap", {"pad": str(tmp_path / "DQ")})
    tekst = base64.b64encode(("Ik schrijf zoals ik praat. Soms kort. Soms wat langer, als het moet. " * 10).encode())
    upload = {"bestandsnaam": "../../stiekem.md", "data": tekst.decode()}
    assert vraag(studio, "POST", "/api/stem/upload", upload)[0] == 200
    assert (tmp_path / "DQ" / "1-input" / "mijn-stijl" / "stiekem.md").is_file()
    assert vraag(studio, "POST", "/api/stem/upload", {"bestandsnaam": "x.exe", "data": tekst.decode()})[0] == 400
    status, r = vraag(studio, "POST", "/api/stem/analyse", {})
    assert status == 200 and r["woorden"] > 50
    from docx import Document
    doc = Document()
    doc.save(tmp_path / "huis.docx")
    data = base64.b64encode((tmp_path / "huis.docx").read_bytes()).decode()
    status, r = vraag(studio, "POST", "/api/templates/upload", {"bestandsnaam": "Huis Stijl.docx", "data": data})
    assert status == 200 and r["check"]["bruikbaar"]
    status, r = vraag(studio, "POST", "/api/vakken/upload", {"vakcode": "sys", "soort": "quick-scan",
                                                             "bestandsnaam": "eisen.md",
                                                             "data": base64.b64encode(b"- Titelpagina").decode()})
    assert status == 200 and (tmp_path / "DQ" / "templates" / "vakken" / "SYS" / "quick-scan.md").is_file()


def test_klaar_schrijft_samenvatting(studio, tmp_path):
    vraag(studio, "POST", "/api/werkmap", {"pad": str(tmp_path / "DQ")})
    status, r = vraag(studio, "POST", "/api/klaar", {})
    assert status == 200
    laatste = json.loads((paden.data() / "studio-laatste.json").read_text())
    assert any("Werkmap ingesteld" in w for w in laatste["wijzigingen"])


def test_bronnen_nu_controleren(studio, monkeypatch):
    from dutchquill import bronnen
    gemarkeerd = []
    leeg = {"gewijzigd": [], "ongewijzigd": 3, "fouten": [], "gecontroleerd_op": "2026-11-24"}
    monkeypatch.setattr(bronnen, "check", lambda: leeg)
    monkeypatch.setattr(bronnen, "markeer", lambda: gemarkeerd.append(True))
    status, r = vraag(studio, "POST", "/api/bronnen/check", {})
    assert status == 200 and r["gemarkeerd"] and gemarkeerd
    veranderd = {**leeg, "gewijzigd": [{"url": "https://x", "gidsen": ["nl/apa"], "reden": "nieuw"}]}
    monkeypatch.setattr(bronnen, "check", lambda: veranderd)
    status, r = vraag(studio, "POST", "/api/bronnen/check", {})
    assert status == 200 and not r["gemarkeerd"] and r["gewijzigd"][0]["gidsen"] == ["nl/apa"]
