"""Feitencontrole na herschrijven of humaniseren: is er iets verloren gegaan, veranderd of bijgekomen?

  dq feiten --origineel <bestand> --nieuw <bestand> [--json]

Vergelijkt getallen (met eenheid of %), jaartallen en datums, namen (woorden met hoofdletter midden in een zin),
citaten tussen aanhalingstekens, bronverwijzingen (Auteur, jaar), URL's en e-mailadressen.
Exitcode 1 als er iets ontbreekt of nieuw is: dan moet een mens (of Claude) kijken.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from dutchquill import tekst as tk

GETAL = re.compile(r"(?<![\w.])[-+]?\d{1,3}(?:[.\s]\d{3})*(?:[.,]\d+)?(?:\s?(?:%|procent|percent|euro|€|uur|min|"
                   r"km|kg|m|gb|mb|tb|ms|x))?(?![\w])", re.IGNORECASE)
DATUM = re.compile(r"\b\d{1,2}\s(?:jan|feb|maa|mrt|apr|mei|jun|jul|aug|sep|okt|nov|dec|mar|may|oct)\w*\s\d{4}\b|"
                   r"\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b", re.IGNORECASE)
CITAAT = re.compile(r"[\"“„«]([^\"”“«»]{12,300})[\"”»]")
BRONVERW = re.compile(r"\(([A-ZÀ-Ö][^()]{1,80}?),?\s(\d{4}[a-z]?|z\.d\.|n\.d\.)(?:,\s?(?:p|blz|pp)\.?\s?[\d\-–]+)?\)")
URL = re.compile(r"https?://[^\s)>\]]+")
MAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
NIET_NAAM = {"de", "het", "een", "in", "op", "bij", "voor", "met", "maar", "als", "dit", "dat", "deze", "die", "the",
             "a", "an", "this", "that", "but", "for", "with", "we", "wij", "ik", "i", "je", "u", "hij", "zij", "ze"}


def _normaliseer_getal(g: str) -> str:
    g = g.lower().replace(" ", "").replace("procent", "%").replace("percent", "%").replace("€", "euro")
    return g


def extraheer(tekst: str) -> dict[str, Counter]:
    rs = tk.regels(tekst)
    proza = "\n".join(r.tekst for r in rs if r.soort != "leeg")
    ruw = tekst  # URL's en mail uit de ruwe tekst (regels() vervangt URL's)
    namen = Counter()
    for z in tk.zinnen(proza.replace("\n", " ")):
        ws = z.split()
        for i, w in enumerate(ws[1:], 1):
            schoon = w.strip(".,;:!?()\"'“”‘’")
            if len(schoon) > 1 and schoon[0].isupper() and schoon.lower() not in NIET_NAAM and not schoon.isupper():
                vorige = ws[i - 1]
                if not vorige.endswith((".", "!", "?", ":")):
                    namen[schoon] += 1
            elif schoon.isupper() and len(schoon) >= 2 and schoon.isalpha():
                namen[schoon] += 1  # afkortingen als SOC, CBS
    datums = Counter(DATUM.findall(proza))
    zonder_datums = DATUM.sub(" ", proza)
    return {
        "getallen": Counter(_normaliseer_getal(g) for g in GETAL.findall(zonder_datums) if g.strip("-+ ")),
        "datums": datums,
        "namen": namen,
        "citaten": Counter(c.strip() for c in CITAAT.findall(proza)),
        "bronverwijzingen": Counter(f"{a.strip()}, {j}" for a, j in BRONVERW.findall(proza)),
        "urls": Counter(u.rstrip(".,;") for u in URL.findall(ruw)),
        "mail": Counter(MAIL.findall(ruw)),
    }


def vergelijk(origineel: str, nieuw: str) -> dict:
    a, b = extraheer(origineel), extraheer(nieuw)
    uit = {"ontbreekt": {}, "nieuw": {}}
    for soort in a:
        weg = sorted((a[soort] - b[soort]).elements()) if soort != "namen" else sorted(set(a[soort]) - set(b[soort]))
        bij = sorted((b[soort] - a[soort]).elements()) if soort != "namen" else sorted(set(b[soort]) - set(a[soort]))
        if weg:
            uit["ontbreekt"][soort] = sorted(set(weg))
        if bij:
            uit["nieuw"][soort] = sorted(set(bij))
    uit["ok"] = not uit["ontbreekt"] and not uit["nieuw"]
    return uit


def rapport(v: dict) -> str:
    if v["ok"]:
        return "Feitencontrole: niets verloren, niets bijgekomen."
    regels = ["Feitencontrole: controleer dit."]
    namen = {"getallen": "getallen", "datums": "datums", "namen": "namen/afkortingen", "citaten": "citaten",
             "bronverwijzingen": "bronverwijzingen", "urls": "links", "mail": "e-mailadressen"}
    for kant, kop in (("ontbreekt", "Ontbreekt in de nieuwe tekst"), ("nieuw", "Nieuw in de nieuwe tekst")):
        for soort, items in v[kant].items():
            regels.append(f"- {kop} ({namen[soort]}): {', '.join(items[:15])}" + (" ..." if len(items) > 15 else ""))
    regels.append("Een naam die alleen anders gespeld of verbogen is, is meestal geen probleem; "
                  "een getal, citaat of bron die ontbreekt of erbij komt wel.")
    return "\n".join(regels)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="dq feiten", description="Feiten in origineel en nieuwe versie vergelijken")
    p.add_argument("--origineel", required=True)
    p.add_argument("--nieuw", required=True)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    def lees(x):
        pad = Path(x)
        if pad.suffix.lower() == ".docx":
            from dutchquill.docx_tekst import extract_text
            return extract_text(str(pad))
        return pad.read_text(encoding="utf-8")

    v = vergelijk(lees(a.origineel), lees(a.nieuw))
    print(json.dumps(v, ensure_ascii=False, indent=2) if a.json else rapport(v))
    if not v["ok"]:
        sys.exit(1)
