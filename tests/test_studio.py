import base64
import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

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
    paden = [w["pad"] for w in v["wijzigingen"]]
    assert ["profiel"] in paden and ["profielen", "mijn-linkedin", "toon", "niveau"] in paden
    vak = json.loads(json.dumps(c["ruw"]))
    vak.setdefault("student", {})["vakken"] = [{"naam": "Bedrijfskunde", "code": "BK1"}]
    vak["student"]["voornaam"] = ""  # leeg tegenover niet ingesteld is geen wijziging
    _, v = vraag(studio, "POST", "/api/config/voorbeeld", {"ruw": vak})
    student = [w for w in v["wijzigingen"] if w["pad"][0] == "student"]
    assert student == [{"pad": ["student", "vakken"], "oud": None, "nieuw": [{"naam": "Bedrijfskunde", "code": "BK1"}]}]
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


def test_sjablonen_en_professioneel(studio, tmp_path):
    pad = tmp_path / "DutchQuill"
    vraag(studio, "POST", "/api/werkmap", {"pad": str(pad), "taal": "nl", "profiel": "zakelijk"})
    _, r = vraag(studio, "GET", "/api/sjablonen")
    mail = next(x for x in r["sjablonen"] if x["genre"] == "mail")
    assert mail["eigen"] is False and "Afsluiting en handtekening" in mail["inhoud"]
    assert vraag(studio, "POST", "/api/sjablonen/opslaan", {"genre": "../../x", "inhoud": "x"})[0] == 400
    assert vraag(studio, "POST", "/api/sjablonen/opslaan", {"genre": "mail", "inhoud": "  "})[0] == 400
    assert vraag(studio, "POST", "/api/sjablonen/opslaan", {"genre": "mail", "inhoud": "# Eigen mail\n"})[0] == 200
    _, r = vraag(studio, "GET", "/api/sjablonen")
    mail = next(x for x in r["sjablonen"] if x["genre"] == "mail")
    assert mail["eigen"] is True and mail["inhoud"].startswith("# Eigen mail")
    assert vraag(studio, "POST", "/api/sjablonen/herstel", {"genre": "mail"})[0] == 200
    assert not (pad / "templates" / "genres" / "mail.md").exists()
    assert len(list((pad / "templates" / "genres" / "oud").glob("mail-*.md"))) == 1

    png = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"0" * 40).decode()
    assert vraag(studio, "POST", "/api/professioneel/upload",
                 {"soort": "stempel", "bestandsnaam": "a.png", "data": png})[0] == 400
    assert vraag(studio, "POST", "/api/professioneel/upload",
                 {"soort": "banner", "bestandsnaam": "a.svg", "data": png})[0] == 400
    status, r = vraag(studio, "POST", "/api/professioneel/upload",
                      {"soort": "banner", "bestandsnaam": "mijn banner.png", "data": png})
    assert status == 200 and r["pad"] == "templates/email/banner.png" and r["voorbeeld"].startswith("data:image/png")
    # De upload schrijft de config niet zelf: dat gaat via opslaan.
    assert not (config.laad_yaml(pad / "dutchquill.yaml") or {}).get("professioneel")


def test_mijn_teksten_en_map_openen(studio, tmp_path, monkeypatch):
    from dutchquill import versies
    assert vraag(studio, "GET", "/api/teksten")[1]["teksten"] == []
    pad = tmp_path / "DutchQuill"
    vraag(studio, "POST", "/api/werkmap", {"pad": str(pad), "taal": "nl", "profiel": "zakelijk"})
    v1 = versies.volgende("schrijven", "Plan voor Q1")
    (Path(v1["map"]) / "Plan voor Q1.docx").write_bytes(b"x")
    versies.volgende("schrijven", "Plan voor Q1")
    versies.volgende("reviewen", "Mail aan team")
    status, r = vraag(studio, "GET", "/api/teksten")
    assert status == 200 and {t["titel"] for t in r["teksten"]} == {"Plan voor Q1", "Mail aan team"}
    plan = next(t for t in r["teksten"] if t["titel"] == "Plan voor Q1")
    assert [v["versie"] for v in plan["versies"]] == [2, 1] and plan["actie"] == "schrijven"
    assert plan["versies"][1]["bestanden"] == ["Plan voor Q1.docx"]
    assert plan["map"] == "2-output/schrijven/Plan voor Q1"

    geopend = []
    monkeypatch.setattr(server.subprocess, "run", lambda args, **kw: geopend.append(args))
    status, r = vraag(studio, "POST", "/api/open-map", {"map": plan["versies"][0]["map"]})
    assert status == 200 and geopend and Path(geopend[0][-1]).parts[-2:] == ("Plan voor Q1", "v2")
    assert vraag(studio, "POST", "/api/open-map", {"map": "../../"})[0] == 400
    assert vraag(studio, "POST", "/api/open-map", {"map": "/etc"})[0] == 400
    assert len(geopend) == 1
    # Een document openen; alleen documenten, en alleen uit die map
    v1map = plan["versies"][1]["map"]
    status, _ = vraag(studio, "POST", "/api/open-map", {"map": v1map, "bestand": "Plan voor Q1.docx"})
    assert status == 200 and Path(geopend[-1][-1]).name == "Plan voor Q1.docx"
    (pad / v1map / "kwaad.command").write_text("echo x")
    assert vraag(studio, "POST", "/api/open-map", {"map": v1map, "bestand": "kwaad.command"})[0] == 400
    assert vraag(studio, "POST", "/api/open-map", {"map": v1map, "bestand": "../../../dutchquill.yaml"})[0] == 400
    assert vraag(studio, "POST", "/api/open-map", {"map": v1map, "bestand": "bestaat-niet.pdf"})[0] == 400
    assert len(geopend) == 2
