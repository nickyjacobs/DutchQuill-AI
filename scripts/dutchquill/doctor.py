"""Controleer de omgeving: Python, pakketten, pdf-conversie, werkmap.

  dq doctor [--json]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import sys

from dutchquill import __version__, paden
from dutchquill.config import ConfigFout, effectief

PAKKETTEN = ["docx", "lxml", "reportlab", "matplotlib", "PIL", "pypdf", "pptx", "openpyxl", "ruamel.yaml",
             "requests", "markdown"]


def controleer() -> dict:
    pakketten = {p: importlib.util.find_spec(p) is not None for p in PAKKETTEN}
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    word_mac = platform.system() == "Darwin" and any(
        __import__("pathlib").Path(p).exists() for p in ("/Applications/Microsoft Word.app",))
    try:
        e = effectief()
        werkmap, fout = e["werkmap"], None
    except ConfigFout as ex:
        werkmap, fout = None, str(ex)
    return {
        "plugin": __version__,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "pakketten_ok": all(pakketten.values()),
        "pakketten": pakketten,
        "pdf_via": "libreoffice" if soffice else ("word" if word_mac else "reportlab (eenvoudig)"),
        "werkmap": werkmap,
        "configfout": fout,
        "data": str(paden.data()),
    }


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq doctor")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    r = controleer()
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    print(f"DutchQuill {r['plugin']} | Python {r['python']} | {r['platform']}")
    ontbreekt = ", ".join(k for k, v in r["pakketten"].items() if not v)
    print(f"Pakketten: {'ok' if r['pakketten_ok'] else 'ontbreekt: ' + ontbreekt}")
    print(f"PDF maken via: {r['pdf_via']}")
    print(f"Werkmap: {r['werkmap'] or 'nog niet ingesteld'}")
    if r["configfout"]:
        print(f"Configfout: {r['configfout']}")
