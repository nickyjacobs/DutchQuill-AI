"""Maak van een invoerbestand Markdown-tekst, met bronmetadata en paginamarkeringen.

  dq extraheer <bestand> [<bestand> ...] --uit <map> [--geen-beelden]

Per bestand: <uit>/<naam>.md, afbeeldingen in <uit>/<naam>-beelden/. Uitvoer op stdout: JSON per bestand.
Ondersteund: .md .txt .markdown .docx .pdf .pptx .xlsx .csv .tsv .html .htm .url .webloc,
en .doc .odt .rtf .pages via LibreOffice of macOS textutil als die er zijn.
"""

from __future__ import annotations

import argparse
import csv
import json
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

SOORTEN = {
    "tekst": {".md", ".markdown", ".txt"},
    "document": {".docx", ".doc", ".odt", ".rtf", ".pages"},
    "pdf": {".pdf"},
    "presentatie": {".pptx"},
    "tabel": {".xlsx", ".csv", ".tsv"},
    "web": {".html", ".htm"},
    "link": {".url", ".webloc"},
    "beeld": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp", ".svg"},
}
URL_RE = re.compile(r"https?://[^\s<>()\"'\]]+")
MAX_RIJEN = 200
MAX_KOLOMMEN = 30


def schone_urls(urls) -> list[str]:
    """Leestekens aan het eind eraf, dubbele weg, en nooit interne adressen (localhost, privé-IP, .local):
    die mag niemand automatisch gaan ophalen."""
    import ipaddress
    from urllib.parse import urlparse
    uit = set()
    for u in urls:
        u = u.rstrip(".,;:!?)'\"")
        try:
            host = (urlparse(u).hostname or "").lower()
        except ValueError:
            continue
        if not host or host == "localhost" or host.endswith((".local", ".lan", ".internal", ".home.arpa")):
            continue
        try:
            ip = ipaddress.ip_address(host)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                continue
        except ValueError:
            pass
        uit.add(u)
    return sorted(uit)


def soort(pad: Path) -> str:
    ext = pad.suffix.lower()
    for naam, exts in SOORTEN.items():
        if ext in exts:
            return naam
    return "onbekend"


def _woorden(tekst: str) -> int:
    return len(re.findall(r"\w+", tekst))


def _md_tabel(rijen: list[list]) -> str:
    rijen = [[("" if c is None else str(c)).replace("|", "\\|").replace("\n", " ") for c in r[:MAX_KOLOMMEN]]
             for r in rijen[: MAX_RIJEN + 1]]
    rijen = [r for r in rijen if any(c.strip() for c in r)]
    if not rijen:
        return "_(leeg)_"
    breedte = max(len(r) for r in rijen)
    rijen = [r + [""] * (breedte - len(r)) for r in rijen]
    regels = ["| " + " | ".join(rijen[0]) + " |", "|" + "---|" * breedte]
    regels += ["| " + " | ".join(r) + " |" for r in rijen[1:]]
    return "\n".join(regels)


# ---------------------------------------------------------------- per soort


def _tekst(pad: Path, **_) -> dict:
    for codering in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return {"tekst": pad.read_text(encoding=codering)}
        except UnicodeDecodeError:
            continue
    return {"tekst": pad.read_bytes().decode("utf-8", errors="replace")}


def _docx(pad: Path, beelden: Path | None, **_) -> dict:
    from docx import Document

    from dutchquill.docx_tekst import extract_text
    if beelden:
        beelden.mkdir(parents=True, exist_ok=True)
    tekst = extract_text(str(pad), images_dir=beelden)
    cp = Document(str(pad)).core_properties
    meta = {"titel": cp.title or None, "auteur": cp.author or None,
            "gemaakt": cp.created.date().isoformat() if cp.created else None}
    return {"tekst": tekst, "metadata": {k: v for k, v in meta.items() if v}}


def _pdf(pad: Path, beelden: Path | None, **_) -> dict:
    from pypdf import PdfReader
    lezer = PdfReader(str(pad))
    if lezer.is_encrypted:
        try:
            lezer.decrypt("")
        except Exception:
            return {"tekst": "", "waarschuwingen": ["Pdf is beveiligd met een wachtwoord; niet te lezen."]}
    delen, leeg, n_beeld = [], 0, 0
    for i, pagina in enumerate(lezer.pages, 1):
        try:
            t = (pagina.extract_text() or "").strip()
        except Exception:
            t = ""
        if len(t) < 20:
            leeg += 1
        delen.append(f"[pagina {i}]\n{t}")
        if beelden and n_beeld < 40:
            try:
                for b in pagina.images:
                    if len(b.data) < 15_000:  # iconen en lijntjes overslaan
                        continue
                    beelden.mkdir(parents=True, exist_ok=True)
                    n_beeld += 1
                    (beelden / f"p{i}-{n_beeld}{Path(b.name).suffix or '.png'}").write_bytes(b.data)
            except Exception:
                pass
    waarsch = []
    if lezer.pages and leeg / len(lezer.pages) > 0.5:
        waarsch.append("Weinig tekst gevonden: waarschijnlijk een scan. Lees de pagina's als beeld met Read (pages).")
    info = lezer.metadata or {}
    meta = {"titel": info.get("/Title"), "auteur": info.get("/Author")}
    datum = str(info.get("/CreationDate") or "")
    if re.match(r"D:\d{8}", datum):
        meta["gemaakt"] = f"{datum[2:6]}-{datum[6:8]}-{datum[8:10]}"
    return {"tekst": "\n\n".join(delen), "paginas": len(lezer.pages), "waarschuwingen": waarsch,
            "metadata": {k: str(v) for k, v in meta.items() if v}}


def _pptx(pad: Path, beelden: Path | None, **_) -> dict:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    pres = Presentation(str(pad))
    delen, n = [], 0
    for i, dia in enumerate(pres.slides, 1):
        kop = dia.shapes.title
        titel = kop.text.strip() if kop is not None and kop.has_text_frame else ""
        regels = [f"## Dia {i}" + (f": {titel}" if titel else "")]
        for vorm in dia.shapes:
            if vorm.has_text_frame and vorm != dia.shapes.title:
                for par in vorm.text_frame.paragraphs:
                    t = "".join(r.text for r in par.runs).strip()
                    if t:
                        regels.append(("  " * par.level) + f"- {t}")
            if getattr(vorm, "has_table", False) and vorm.has_table:
                regels.append(_md_tabel([[c.text for c in rij.cells] for rij in vorm.table.rows]))
            if beelden and vorm.shape_type == MSO_SHAPE_TYPE.PICTURE:
                beelden.mkdir(parents=True, exist_ok=True)
                n += 1
                (beelden / f"dia{i}-{n}.{vorm.image.ext}").write_bytes(vorm.image.blob)
        if dia.has_notes_slide:
            noot = dia.notes_slide.notes_text_frame.text.strip()
            if noot:
                regels.append(f"\n_Notities:_ {noot}")
        delen.append("\n".join(regels))
    cp = pres.core_properties
    meta = {"titel": cp.title or None, "auteur": cp.author or None}
    return {"tekst": "\n\n".join(delen), "paginas": len(pres.slides),
            "metadata": {k: v for k, v in meta.items() if v}}


def _tabel(pad: Path, **_) -> dict:
    ext = pad.suffix.lower()
    if ext == ".xlsx":
        from openpyxl import load_workbook
        wb = load_workbook(str(pad), read_only=True, data_only=True)
        delen, waarsch = [], []
        for blad in wb.worksheets:
            rijen = [list(r) for r in blad.iter_rows(values_only=True)]
            if len(rijen) > MAX_RIJEN:
                waarsch.append(f"Blad '{blad.title}': {len(rijen)} rijen, eerste {MAX_RIJEN} meegenomen.")
            delen.append(f"## Blad: {blad.title}\n\n{_md_tabel(rijen)}")
        return {"tekst": "\n\n".join(delen), "waarschuwingen": waarsch}
    ruw = _tekst(pad)["tekst"]
    try:
        dialect = csv.Sniffer().sniff(ruw[:4096], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel_tab if ext == ".tsv" else csv.excel
    rijen = list(csv.reader(ruw.splitlines(), dialect))
    waarsch = [f"{len(rijen)} rijen, eerste {MAX_RIJEN} meegenomen."] if len(rijen) > MAX_RIJEN else []
    return {"tekst": _md_tabel(rijen), "waarschuwingen": waarsch}


class _HtmlTekst(HTMLParser):
    BLOK = {"p", "li", "blockquote", "pre", "td", "th", "figcaption", "dd", "dt"}
    KOP = {"h1", "h2", "h3", "h4", "h5", "h6"}
    NEGEER = {"script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg", "button", "template"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blokken: list[str] = []
        self.huidig: list[str] = []
        self.diepte_negeer = 0
        self.tag_stapel: list[str] = []
        self.meta: dict = {}
        self.in_titel = False
        self.titel = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.NEGEER:
            self.diepte_negeer += 1
        if tag == "title":
            self.in_titel = True
        if tag == "meta":
            naam = (a.get("name") or a.get("property") or "").lower()
            if naam in ("author", "article:author", "citation_author"):
                self.meta.setdefault("auteur", a.get("content"))
            if naam in ("article:published_time", "date", "citation_publication_date", "dc.date"):
                self.meta.setdefault("gepubliceerd", (a.get("content") or "")[:10])
            if naam in ("og:site_name",):
                self.meta.setdefault("website", a.get("content"))
            if naam in ("og:url",):
                self.meta.setdefault("url", a.get("content"))
        if tag == "link" and (a.get("rel") or "") == "canonical":
            self.meta.setdefault("url", a.get("href"))
        if tag in self.BLOK | self.KOP:
            self._sluit()
            self.tag_stapel.append(tag)
        if tag == "br":
            self.huidig.append("\n")

    def handle_endtag(self, tag):
        if tag in self.NEGEER and self.diepte_negeer:
            self.diepte_negeer -= 1
        if tag == "title":
            self.in_titel = False
        if tag in self.BLOK | self.KOP:
            self._sluit(tag)

    def handle_data(self, data):
        if self.in_titel:
            self.titel += data
        elif not self.diepte_negeer:
            self.huidig.append(data)

    def _sluit(self, tag: str | None = None):
        t = re.sub(r"[ \t\r\f\v]+", " ", "".join(self.huidig)).strip()
        self.huidig = []
        soort = tag or (self.tag_stapel[-1] if self.tag_stapel else "p")
        if self.tag_stapel and tag:
            self.tag_stapel.pop()
        if not t:
            return
        if soort in self.KOP:
            t = "#" * int(soort[1]) + " " + t
        elif soort == "li":
            t = "- " + t
        elif soort == "blockquote":
            t = "> " + t
        self.blokken.append(t)


def _html(pad: Path, **_) -> dict:
    p = _HtmlTekst()
    p.feed(_tekst(pad)["tekst"])
    p._sluit()
    meta = {"titel": p.titel.strip() or None, **p.meta}
    return {"tekst": "\n\n".join(p.blokken), "metadata": {k: v for k, v in meta.items() if v}}


def _link(pad: Path, **_) -> dict:
    url = None
    if pad.suffix.lower() == ".webloc":
        try:
            url = plistlib.loads(pad.read_bytes()).get("URL")
        except Exception:
            pass
    else:
        m = re.search(r"^URL=(.+)$", _tekst(pad)["tekst"], re.MULTILINE)
        url = m.group(1).strip() if m else None
    return {"tekst": url or "", "urls": [url] if url else []}


def _via_conversie(pad: Path, beelden: Path | None, **_) -> dict:
    """.doc .odt .rtf .pages: eerst omzetten met LibreOffice (naar docx) of macOS textutil (naar txt)."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    with tempfile.TemporaryDirectory() as tmp:
        if soffice:
            subprocess.run([soffice, "--headless", "--convert-to", "docx", "--outdir", tmp, str(pad)],
                           capture_output=True, timeout=120)
            uit = Path(tmp) / (pad.stem + ".docx")
            if uit.is_file():
                return _docx(uit, beelden)
        if shutil.which("textutil") and pad.suffix.lower() != ".pages":
            uit = Path(tmp) / (pad.stem + ".txt")
            subprocess.run(["textutil", "-convert", "txt", "-output", str(uit), str(pad)],
                           capture_output=True, timeout=120)
            if uit.is_file():
                return {"tekst": uit.read_text(encoding="utf-8", errors="replace"),
                        "waarschuwingen": ["Omgezet met textutil: opmaak en afbeeldingen zijn weg."]}
    return {"tekst": "", "waarschuwingen": [
        f"{pad.suffix} niet te lezen zonder LibreOffice. Sla het op als .docx of .pdf, of installeer LibreOffice."]}


LEZERS = {"tekst": _tekst, "pdf": _pdf, "presentatie": _pptx, "tabel": _tabel, "web": _html, "link": _link}


def extraheer(pad: Path, uit: Path, beelden: bool = True) -> dict:
    """Lees één bestand en schrijf <uit>/<naam>.md. Geeft een samenvatting voor het manifest terug."""
    s = soort(pad)
    resultaat = {"bron": str(pad), "soort": s}
    if s in ("beeld", "onbekend"):
        resultaat["overgeslagen"] = "beeld: gebruik dq beeld" if s == "beeld" else f"onbekend type {pad.suffix}"
        return resultaat
    uit.mkdir(parents=True, exist_ok=True)
    naam = re.sub(r"[^\w\-. ]", "_", pad.stem).strip() or "bestand"
    beeldmap = uit / f"{naam}-beelden" if beelden else None
    if s == "document":
        lezer = _docx if pad.suffix.lower() == ".docx" else _via_conversie
    else:
        lezer = LEZERS[s]
    try:
        r = lezer(pad, beelden=beeldmap)
    except Exception as e:  # één kapot bestand mag de rest niet stoppen
        return {**resultaat, "fout": f"{type(e).__name__}: {e}"}
    tekst = r.get("tekst", "")
    urls = r.get("urls") or []
    if s in ("tekst", "document", "web", "pdf"):
        urls = [*urls, *URL_RE.findall(tekst)]
    urls = schone_urls(urls)
    meta = r.get("metadata", {})
    kop = [f"<!-- bron: {pad} | soort: {s}"]
    if r.get("paginas"):
        kop.append(f"pagina's: {r['paginas']}")
    kop += [f"{k}: {v}" for k, v in meta.items()]
    doel, n = uit / f"{naam}.md", 2
    while doel.exists():  # twee bronnen met dezelfde naam (bijv. notities/a.md en bronnen/a.pdf)
        doel, n = uit / f"{naam}-{n}.md", n + 1
    doel.write_text(" | ".join(kop) + " -->\n\n# " + pad.name + "\n\n" + tekst.strip() + "\n", encoding="utf-8")
    beeldlijst = sorted(str(f) for f in beeldmap.iterdir()) if beeldmap and beeldmap.is_dir() else []
    return {**resultaat, "uitvoer": str(doel), "woorden": _woorden(tekst), "paginas": r.get("paginas"),
            "metadata": meta, "urls": urls, "afbeeldingen": beeldlijst,
            "waarschuwingen": r.get("waarschuwingen", [])}


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq extraheer", description="Bestanden omzetten naar Markdown")
    p.add_argument("bestanden", nargs="+")
    p.add_argument("--uit", required=True)
    p.add_argument("--geen-beelden", action="store_true")
    a = p.parse_args(argv)
    uitkomst = []
    for b in a.bestanden:
        pad = Path(b).expanduser()
        if not pad.is_file():
            uitkomst.append({"bron": b, "fout": "bestand niet gevonden"})
            continue
        uitkomst.append(extraheer(pad, Path(a.uit), beelden=not a.geen_beelden))
    print(json.dumps(uitkomst, ensure_ascii=False, indent=2))
    if any("fout" in u for u in uitkomst):
        sys.exit(1)
