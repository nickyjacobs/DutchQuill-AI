"""DutchQuill Studio: een lokale web-app voor installatie en instellingen.

  dq studio [--geen-browser] [--poort 0]

Draait alleen op 127.0.0.1, met een eenmalig token. Leest en schrijft de config via dezelfde code als dq config
(schema-validatie, commentaar blijft, .bak). Stopt na "Klaar" of na 15 minuten zonder activiteit, en laat in
<data>/studio-laatste.json achter wat er veranderd is, zodat /dutchquill:instellen het kan samenvatten.
"""

from __future__ import annotations

import argparse
import base64
import copy
import difflib
import hmac
import io
import json
import mimetypes
import platform
import re
import secrets
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from dutchquill import __version__, paden
from dutchquill import config as cfg
from dutchquill.schema_check import standaardwaarden

STATIC = Path(__file__).parent / "static"
mimetypes.add_type("font/woff2", ".woff2")
MAX_BODY = 15 * 1024 * 1024
STIL = 15 * 60
UPLOAD = {
    "template": {".docx"},
    "stem": {".md", ".txt", ".docx", ".pdf"},
    "vak": {".md", ".txt", ".docx", ".pdf"},
}
VERBODEN_MAPPEN = ("/System", "/usr", "/bin", "/sbin", "/etc", "/private/etc", "/Library", "/Applications",
                   "C:\\Windows", "C:\\Program Files")


class Fout(Exception):
    def __init__(self, bericht: str, status: int = 400):
        super().__init__(bericht)
        self.status = status


class Studio:
    def __init__(self):
        self.token = secrets.token_urlsafe(24)
        self.poort = 0
        self.laatst = time.time()
        self.wijzigingen: list[str] = []
        self.server: ThreadingHTTPServer | None = None

    # -------------------------------------------------------------- hulpfuncties

    def werkmap(self) -> Path | None:
        e = cfg.effectief()
        return Path(e["werkmap"]) if e["ingesteld"] else None

    def ruw(self) -> dict:
        _, pad, data, *_ = cfg.werkmap_en_bestanden()
        return data if pad and pad.is_file() else {}

    def profiel_effectief(self, ruw: dict, naam: str) -> dict:
        sch = cfg.schema()
        keten = cfg.profiel_keten(naam, ruw.get("profielen") or {}, cfg.ingebouwde_profielen())
        prof = standaardwaarden(sch["$defs"]["profiel"], sch) or {}
        for _, deel in keten:
            prof = cfg.diep_samenvoegen(prof, {k: v for k, v in deel.items() if k in cfg.PROFIEL_SLEUTELS})
        return {"keten": [n for n, _ in keten], **prof}

    def veilig_pad(self, pad: str) -> Path:
        p = Path(pad).expanduser()
        if not p.is_absolute():
            raise Fout("Geef een volledig pad, bijvoorbeeld ~/Documents/DutchQuill.")
        p = p.resolve()
        if str(p) in ("/", str(Path.home())) or any(str(p).startswith(v) for v in VERBODEN_MAPPEN):
            raise Fout("Kies een gewone map, zoals Bureaublad of Documenten, en niet de systeem- of thuismap zelf.")
        return p

    @staticmethod
    def schone_naam(naam: str) -> str:
        naam = Path(naam).name
        naam = re.sub(r"[^\w\-. ]", "_", naam).strip(" .")
        if not naam:
            raise Fout("Ongeldige bestandsnaam.")
        return naam

    def bewaar_upload(self, soort: str, doelmap: Path, bestandsnaam: str, data_b64: str) -> Path:
        naam = self.schone_naam(bestandsnaam)
        if Path(naam).suffix.lower() not in UPLOAD[soort]:
            raise Fout(f"Dit bestandstype kan hier niet. Toegestaan: {', '.join(sorted(UPLOAD[soort]))}.")
        try:
            data = base64.b64decode(data_b64, validate=True)
        except Exception as e:
            raise Fout("Het bestand kwam niet goed door. Probeer het opnieuw.") from e
        if len(data) > 10 * 1024 * 1024:
            raise Fout("Het bestand is groter dan 10 MB.")
        doelmap.mkdir(parents=True, exist_ok=True)
        doel = doelmap / naam
        n = 2
        while doel.exists():
            doel = doelmap / f"{Path(naam).stem}-{n}{Path(naam).suffix}"
            n += 1
        doel.write_bytes(data)
        return doel

    # -------------------------------------------------------------- API

    def status(self, _: dict) -> dict:
        e = cfg.effectief()
        stand = json.loads((paden.root() / "gidsen" / "stand.json").read_text(encoding="utf-8"))
        try:
            bw = json.loads((paden.data() / "bijwerken.json").read_text(encoding="utf-8"))
        except Exception:
            bw = {}
        home = Path.home()
        snel = {"bureaublad": home / "Desktop" / "DutchQuill", "documenten": home / "Documents" / "DutchQuill"}
        return {
            "versie": __version__,
            "ingesteld": e["ingesteld"],
            "werkmap": e["werkmap"],
            "taal": e["taal"],
            "snelkeuzes": {k: str(v) for k, v in snel.items()},
            "gidsen_gecontroleerd": max(filter(None, [stand.get("gecontroleerd"), bw.get("laatst_gecontroleerd")])),
            "platform": platform.system(),
        }

    def config_lezen(self, _: dict) -> dict:
        ruw = self.ruw()
        ingebouwd = cfg.ingebouwde_profielen()
        actief = ruw.get("profiel") or "zakelijk"
        return {
            "ruw": ruw,
            "schema": cfg.schema(),
            "ingebouwd": ingebouwd,
            "standaard": standaardwaarden(cfg.schema(), cfg.schema()),
            "actief_effectief": self.profiel_effectief(ruw, actief) if self.werkmap() else None,
        }

    def profiel_bekijk(self, body: dict) -> dict:
        return self.profiel_effectief(body.get("ruw") or {}, body["naam"])

    def config_voorbeeld(self, body: dict) -> dict:
        nieuw = body.get("ruw") or {}
        fouten = cfg.valideer_config(nieuw)
        oud_tekst, nieuw_tekst = self._yaml_tekst(self.ruw()), self._yaml_tekst(nieuw)
        diff = "".join(difflib.unified_diff(oud_tekst.splitlines(True), nieuw_tekst.splitlines(True),
                                            "nu", "straks", n=1))
        return {"fouten": fouten, "diff": diff, "samenvatting": self._samenvatting(self.ruw(), nieuw)}

    def config_opslaan(self, body: dict) -> dict:
        nieuw = body.get("ruw") or {}
        fouten = cfg.valideer_config(nieuw)
        if fouten:
            raise Fout("Niet opgeslagen:\n- " + "\n- ".join(fouten))
        werkmap = self.werkmap()
        if not werkmap:
            raise Fout("Kies eerst een werkmap.")
        pad = werkmap / paden.WERKMAP_CONFIG
        rt = cfg.laad_yaml(pad) if pad.is_file() else cfg._yaml().load("{}")
        samenvatting = self._samenvatting(self.ruw(), nieuw)
        _sync(rt, nieuw)
        cfg.schrijf_config(pad, rt)
        self.wijzigingen += samenvatting
        return {"opgeslagen": True, "samenvatting": samenvatting}

    def werkmap_init(self, body: dict) -> dict:
        from dutchquill import werkmap
        pad = self.veilig_pad(body["pad"])
        uit = werkmap.init(pad, body.get("taal", "nl"), body.get("profiel", "zakelijk"),
                           bool(body.get("languagetool")))
        self.wijzigingen.append(f"Werkmap ingesteld: {uit['werkmap']}")
        return uit

    def kies_map(self, _: dict) -> dict:
        if platform.system() == "Darwin":
            r = subprocess.run(["osascript", "-e",
                                'POSIX path of (choose folder with prompt "Kies waar je DutchQuill-map komt")'],
                               capture_output=True, text=True, timeout=300)
            pad = r.stdout.strip()
            return {"pad": pad.rstrip("/") or None}
        try:
            r = subprocess.run([sys.executable, "-c",
                                "import tkinter as t,tkinter.filedialog as f;r=t.Tk();r.withdraw();"
                                "print(f.askdirectory() or '')"], capture_output=True, text=True, timeout=300)
            return {"pad": r.stdout.strip() or None}
        except Exception:
            return {"pad": None, "melding": "Geen mapkiezer beschikbaar; typ het pad."}

    def templates(self, _: dict) -> dict:
        from dutchquill import templates_docx
        return {"templates": templates_docx.lijst()}

    def template_upload(self, body: dict) -> dict:
        from dutchquill import templates_docx
        werkmap = self._vereist_werkmap()
        e = cfg.effectief()
        doel = self.bewaar_upload("template", Path(e["mappen"]["templates"]), body["bestandsnaam"], body["data"])
        naam = re.sub(r"[^a-z0-9\-]", "-", doel.stem.lower()).strip("-") or "eigen"
        cfg.zet(f"templates.{naam}", {"bestand": str(doel.relative_to(werkmap)), "soort": "docx",
                                      "beschrijving": body.get("beschrijving") or f"Geüpload: {doel.name}"})
        self.wijzigingen.append(f"Template toegevoegd: {naam}")
        return {"naam": naam, "check": templates_docx.check(naam)}

    def template_check(self, body: dict) -> dict:
        from dutchquill import templates_docx
        return templates_docx.check(body["naam"])

    def template_aanpas(self, body: dict) -> dict:
        from dutchquill import templates_docx
        r = templates_docx.aanpas(body["van"], body["naar"], body.get("stijlen", []), body.get("marge"),
                                  body.get("beschrijving"))
        self.wijzigingen.append(f"Template gemaakt: {body['naar']}")
        return r

    def stem(self, _: dict) -> dict:
        self._vereist_werkmap()
        e = cfg.effectief()
        map_ = Path(e["mappen"]["mijn_stijl"])
        bestanden = sorted(f.name for f in map_.iterdir() if f.is_file() and not f.name.startswith(".")) \
            if map_.is_dir() else []
        pad = Path(e["mappen"]["intern"]) / "stem.json"
        profiel = json.loads(pad.read_text(encoding="utf-8")) if pad.is_file() else None
        return {"map": str(map_), "bestanden": bestanden, "profiel": profiel}

    def stem_upload(self, body: dict) -> dict:
        self._vereist_werkmap()
        e = cfg.effectief()
        doel = self.bewaar_upload("stem", Path(e["mappen"]["mijn_stijl"]), body["bestandsnaam"], body["data"])
        self.wijzigingen.append(f"Eigen tekst toegevoegd: {doel.name}")
        return {"bestand": doel.name}

    def stem_analyse(self, _: dict) -> dict:
        from dutchquill import stem
        try:
            r = stem.analyse()
        except cfg.ConfigFout as e:
            raise Fout(str(e)) from e
        self.wijzigingen.append("Stemprofiel gemeten")
        return r

    def vak_upload(self, body: dict) -> dict:
        werkmap = self._vereist_werkmap()
        code = re.sub(r"[^\w\-]", "", body.get("vakcode", "")).upper()
        soort = body.get("soort")
        if not code or soort not in ("quick-scan", "beoordelingscriteria"):
            raise Fout("Geef een vakcode en kies: inlevereisen of beoordelingscriteria.")
        map_ = Path(cfg.effectief()["mappen"]["templates"]) / "vakken" / code
        doel = self.bewaar_upload("vak", map_ / "origineel", body["bestandsnaam"], body["data"])
        if doel.suffix.lower() in (".docx", ".pdf"):
            from dutchquill import extraheer
            r = extraheer.extraheer(doel, map_ / "origineel", beelden=False)
            tekst = Path(r["uitvoer"]).read_text(encoding="utf-8") if r.get("uitvoer") else ""
        else:
            tekst = doel.read_text(encoding="utf-8", errors="replace")
        (map_ / f"{soort}.md").write_text(tekst, encoding="utf-8")
        self.wijzigingen.append(f"{soort} voor {code} toegevoegd")
        return {"vak": code, "bestand": str((map_ / f"{soort}.md").relative_to(werkmap))}

    def vakken(self, _: dict) -> dict:
        werkmap = self.werkmap()
        if not werkmap:
            return {"vakken": {}}
        basis = Path(cfg.effectief()["mappen"]["templates"]) / "vakken"
        uit = {}
        if basis.is_dir():
            for d in sorted(p for p in basis.iterdir() if p.is_dir()):
                uit[d.name] = sorted(f.stem for f in d.glob("*.md"))
        return {"vakken": uit}

    def bronnen_check(self, _: dict) -> dict:
        """Controleer nu of de bronnen van de gidsen veranderd zijn. Niets veranderd: meteen als gecontroleerd
        markeren (de maandmelding begint opnieuw). Wel veranderd: bijwerken gaat via /dutchquill:bijwerken."""
        from dutchquill import bronnen
        r = bronnen.check()
        gewijzigd = [{"url": g["url"], "gidsen": g["gidsen"], "reden": g["reden"]} for g in r["gewijzigd"]]
        gemarkeerd = False
        if not gewijzigd and not r["fouten"]:
            bronnen.markeer()
            gemarkeerd = True
            self.wijzigingen.append("Gidsen gecontroleerd: alles actueel")
        return {"gewijzigd": gewijzigd, "ongewijzigd": r["ongewijzigd"], "fouten": r["fouten"],
                "gemarkeerd": gemarkeerd, "gecontroleerd_op": r["gecontroleerd_op"]}

    def klaar(self, _: dict) -> dict:
        (paden.data() / "studio-laatste.json").write_text(json.dumps(
            {"tijd": datetime.now().isoformat(timespec="seconds"), "wijzigingen": self.wijzigingen},
            ensure_ascii=False, indent=2), encoding="utf-8")
        threading.Thread(target=self._stop, daemon=True).start()
        return {"gestopt": True, "wijzigingen": self.wijzigingen}

    # -------------------------------------------------------------- intern

    def _vereist_werkmap(self) -> Path:
        w = self.werkmap()
        if not w:
            raise Fout("Kies eerst een werkmap.")
        return w

    @staticmethod
    def _yaml_tekst(data) -> str:
        buf = io.StringIO()
        cfg._yaml().dump(cfg.naar_dict(data) if data else {}, buf)
        return buf.getvalue()

    @staticmethod
    def _samenvatting(oud: dict, nieuw: dict, prefix: str = "") -> list[str]:
        uit = []
        for k in sorted(set(oud) | set(nieuw)):
            pad = f"{prefix}{k}"
            a, b = oud.get(k), nieuw.get(k)
            if isinstance(a, dict) and isinstance(b, dict):
                uit += Studio._samenvatting(a, b, pad + ".")
            elif a != b:
                if b is None:
                    uit.append(f"{pad} verwijderd")
                else:
                    uit.append(f"{pad}: {json.dumps(a, ensure_ascii=False)} wordt {json.dumps(b, ensure_ascii=False)}")
        return uit

    def _stop(self):
        time.sleep(0.3)
        if self.server:
            self.server.shutdown()

    def waakhond(self):
        while True:
            time.sleep(20)
            if time.time() - self.laatst > STIL:
                self.wijzigingen.append("Studio gestopt na 15 minuten zonder activiteit")
                self.klaar({})
                return


def _sync(rt, nieuw: dict) -> None:
    """Breng de round-trip YAML (met commentaar) in lijn met de nieuwe dict, zonder commentaar te verliezen."""
    for k in list(rt.keys()):
        if k not in nieuw:
            del rt[k]
    for k, v in nieuw.items():
        if isinstance(v, dict) and k in rt and isinstance(rt[k], dict):
            _sync(rt[k], v)
        elif rt.get(k) != v:
            rt[k] = copy.deepcopy(v)


ROUTES = {
    ("GET", "/api/status"): "status",
    ("GET", "/api/config"): "config_lezen",
    ("POST", "/api/profiel"): "profiel_bekijk",
    ("POST", "/api/config/voorbeeld"): "config_voorbeeld",
    ("POST", "/api/config/opslaan"): "config_opslaan",
    ("POST", "/api/werkmap"): "werkmap_init",
    ("POST", "/api/kies-map"): "kies_map",
    ("GET", "/api/templates"): "templates",
    ("POST", "/api/templates/upload"): "template_upload",
    ("POST", "/api/templates/check"): "template_check",
    ("POST", "/api/templates/aanpas"): "template_aanpas",
    ("GET", "/api/stem"): "stem",
    ("POST", "/api/stem/upload"): "stem_upload",
    ("POST", "/api/stem/analyse"): "stem_analyse",
    ("GET", "/api/vakken"): "vakken",
    ("POST", "/api/vakken/upload"): "vak_upload",
    ("POST", "/api/bronnen/check"): "bronnen_check",
    ("POST", "/api/klaar"): "klaar",
}


def maak_handler(studio: Studio):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DutchQuillStudio"
        sys_version = ""

        def log_message(self, *_):  # stil
            pass

        def _stuur(self, status: int, data: bytes, soort: str):
            self.send_response(status)
            self.send_header("Content-Type", soort)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy",
                             "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                             "connect-src 'self'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(data)

        def _json(self, status: int, obj):
            self._stuur(status, json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8")

        def _host_ok(self) -> bool:
            return self.headers.get("Host") in (f"127.0.0.1:{studio.poort}", f"localhost:{studio.poort}")

        def _api(self, methode: str):
            if not hmac.compare_digest(self.headers.get("X-DQ-Token", ""), studio.token):
                return self._json(403, {"fout": "Geen toegang."})
            origin = self.headers.get("Origin")
            if methode == "POST" and origin and origin not in (f"http://127.0.0.1:{studio.poort}",
                                                                f"http://localhost:{studio.poort}"):
                return self._json(403, {"fout": "Geen toegang."})
            naam = ROUTES.get((methode, urlparse(self.path).path))
            if not naam:
                return self._json(404, {"fout": "Onbekend."})
            body = {}
            if methode == "POST":
                lengte = int(self.headers.get("Content-Length") or 0)
                if lengte > MAX_BODY:
                    return self._json(413, {"fout": "Te groot (maximaal 10 MB per bestand)."})
                if lengte:
                    try:
                        body = json.loads(self.rfile.read(lengte))
                    except json.JSONDecodeError:
                        return self._json(400, {"fout": "Ongeldige aanvraag."})
            studio.laatst = time.time()
            try:
                self._json(200, getattr(studio, naam)(body))
            except Fout as e:
                self._json(e.status, {"fout": str(e)})
            except cfg.ConfigFout as e:
                self._json(400, {"fout": str(e)})
            except KeyError as e:
                self._json(400, {"fout": f"Veld ontbreekt: {e}"})
            except Exception as e:  # nooit een stacktrace naar de browser
                self._json(500, {"fout": f"Er ging iets mis ({type(e).__name__}). Probeer het opnieuw."})

        def do_GET(self):  # noqa: N802
            if not self._host_ok():
                return self._stuur(403, b"", "text/plain")
            pad = urlparse(self.path).path
            if pad.startswith("/api/"):
                return self._api("GET")
            bestand = "index.html" if pad in ("/", "") else pad.lstrip("/")
            doel = (STATIC / bestand).resolve()
            if STATIC.resolve() not in doel.parents or not doel.is_file():
                return self._stuur(404, b"Niet gevonden", "text/plain")
            soort = mimetypes.guess_type(doel.name)[0] or "application/octet-stream"
            if soort.startswith("text/") or soort.endswith("javascript"):
                soort += "; charset=utf-8"
            self._stuur(200, doel.read_bytes(), soort)

        def do_POST(self):  # noqa: N802
            if not self._host_ok():
                return self._stuur(403, b"", "text/plain")
            self._api("POST")

    return Handler


def start(open_browser: bool = True, poort: int = 0) -> Studio:
    studio = Studio()
    server = ThreadingHTTPServer(("127.0.0.1", poort), maak_handler(studio))
    studio.server, studio.poort = server, server.server_address[1]
    return studio


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq studio", description="DutchQuill Studio openen")
    p.add_argument("--geen-browser", action="store_true")
    p.add_argument("--poort", type=int, default=0)
    a = p.parse_args(argv)
    studio = start(not a.geen_browser, a.poort)
    url = f"http://127.0.0.1:{studio.poort}/#t={studio.token}"
    melding = "DutchQuill Studio draait. Klik in de Studio op 'Klaar' als je klaar bent."
    print(json.dumps({"url": url, "melding": melding}, ensure_ascii=False), flush=True)
    if not a.geen_browser:
        webbrowser.open(url)
    threading.Thread(target=studio.waakhond, daemon=True).start()
    try:
        studio.server.serve_forever()
    except KeyboardInterrupt:
        studio.klaar({})
    print(json.dumps({"gestopt": True, "wijzigingen": studio.wijzigingen}, ensure_ascii=False), flush=True)

