"""dq reviewgrafiek: één overzichtsbeeld bovenaan een review- of humaniseringsrapport.

Vier kaarten (AI-patronen, leesbaarheid, woordvariatie, taalronde of aantal patronen) en een staafdiagram van de
patronen die het zwaarst wegen, in de kleuren van DutchQuill Studio. De cijfers komen uit `dq tells`; er wordt niets
geschat of aangevuld.

  dq reviewgrafiek --input <tekst> --output <png> [--genre G] [--taal nl|en|auto] [--titel T]
                   [--oordeel "Kleine aanpassingen"] [--taalronde 3] [--json]

Stdout: het pad naar de png (of met --json alle waarden).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from dutchquill import tells

INKT, ZACHT, LIJN, VLAK, BLOK = "#0f2a33", "#52666e", "#dfe7e9", "#f4f7f7", "#ffffff"
PRIMAIR, ACCENT, LET_OP, FOUT = "#155566", "#2bb3c4", "#9a5b00", "#b3332c"
NIVEAU_KLEUR = {"laag": PRIMAIR, "gemiddeld": LET_OP, "hoog": FOUT}

TEKST = {
    "nl": {"titel": "Overzicht", "woorden": "woorden", "ai": "AI-patronen",
           "per1000": "{s} per 1000 woorden (laag < {l})",
           "lees": "Leesbaarheid", "flesch": "Flesch-Douma", "doel": "doel {a}", "var": "Woordvariatie",
           "mattr": "MATTR", "kort_mattr": "te kort om te meten", "taalronde": "Taalronde",
           "verbeteringen": "verbeteringen", "patronen": "Tellende patronen", "gevonden": "gevonden",
           "zwaarst": "Wat het zwaarst weegt (punten)", "geen": "Geen tellende patronen gevonden.",
           "klaar_ja": "Klaar als rapport: ja", "klaar_nee": "Klaar als rapport: nog niet",
           "kort": "Korte tekst: de cijfers zeggen weinig", "hoger": "hoger = makkelijker",
           "niveau": {"laag": "LAAG", "gemiddeld": "GEMIDDELD", "hoog": "HOOG"}},
    "en": {"titel": "Overview", "woorden": "words", "ai": "AI patterns", "per1000": "{s} per 1000 words (low < {l})",
           "lees": "Readability", "flesch": "Flesch", "doel": "target {a}", "var": "Word variety",
           "mattr": "MATTR", "kort_mattr": "too short to measure", "taalronde": "Language round",
           "verbeteringen": "fixes", "patronen": "Counting patterns", "gevonden": "found",
           "zwaarst": "What weighs most (points)", "geen": "No counting patterns found.",
           "klaar_ja": "Ready as a report: yes", "klaar_nee": "Ready as a report: not yet",
           "kort": "Short text: the figures say little", "hoger": "higher = easier",
           "niveau": {"laag": "LOW", "gemiddeld": "MEDIUM", "hoog": "HIGH"}},
}

CATEGORIE = {
    "woord": ("Sterke AI-woorden", "Strong AI words"), "woord_zwak": ("Zwakke AI-woorden", "Weak AI words"),
    "cluster": ("Clusters", "Clusters"), "dichtheid": ("Dichtheid zwakke woorden", "Weak-word density"),
    "anglicisme": ("Anglicismen", "Anglicisms"), "eigen_regel": ("Eigen regels", "Your own rules"),
    "frase_aanloop": ("Lege aanloop", "Empty opener"), "frase_aankondiging": ("Tekst over de tekst", "Signposting"),
    "frase_afsluiter": ("Lege afsluiter", "Empty closer"), "frase_vulling": ("Vulzinnen", "Filler"),
    "frase_vage_bron": ("Vage bronnen", "Vague sources"), "frase_chatbot": ("Chatbotresten", "Chatbot leftovers"),
    "frase_linkedin": ("LinkedIn-formules", "LinkedIn formulas"), "niet_x_maar_y": ("Niet X maar Y", "Not X but Y"),
    "retorische_aanloop": ("Retorische aanloop", "Rhetorical set-up"), "drieslag": ("Drieslagen", "Rule of three"),
    "zinsbegin": ("Herhaald zinsbegin", "Repeated openers"), "alineabegin": ("Herhaald alineabegin",
                                                                              "Repeated paragraph openers"),
    "connectoren": ("Verbindingswoorden vooraan", "Connector openers"),
    "ritme_gelijk": ("Gelijk ritme", "Even rhythm"), "ritme_overgecorrigeerd": ("Overgecorrigeerd", "Overcorrected"),
    "alinea_gelijk": ("Gelijke alinea's", "Even paragraphs"), "woordenschat": ("Weinig variatie", "Low variety"),
    "streepje": ("Gedachtestreepjes", "Dashes"), "vet": ("Vet in de zin", "Bold in sentences"),
    "emoji": ("Emoji", "Emoji"), "hashtags": ("Hashtags", "Hashtags"), "broetry": ("Broetry", "Broetry"),
    "title_case": ("Title case", "Title case"), "kop_herhaald": ("Kop herhaald", "Heading echoed"),
    "passief": ("Lijdende vorm", "Passive voice"), "oxford_komma": ("Oxford-komma", "Oxford comma"),
    "bijvoeglijk_stapel": ("Gestapelde bijv. nw.", "Stacked adjectives"),
    "niveau3_dichtheid": ("Nadrukwoorden", "Emphasis words"), "leesbaarheid": ("Lage leesbaarheid",
                                                                               "Low readability"),
}


def _getal(x: float | None, taal: str, dec: int = 1) -> str:
    if x is None:
        return "-"
    s = f"{x:.{dec}f}"
    return s.replace(".", ",") if taal == "nl" else s


def waarden(r: dict, taalronde: int | None = None, oordeel: str | None = None) -> dict:
    """De cijfers die in het beeld komen, rechtstreeks uit het tells-resultaat."""
    s = r["statistiek"]
    per_cat: dict[str, float] = defaultdict(float)
    for b in r["bevindingen"]:
        if b["punten"] > 0:
            per_cat[b["cat"]] += b["punten"]
    top = sorted(per_cat.items(), key=lambda kv: (-kv[1], kv[0]))[:6]
    acc = r.get("acceptatie")
    return {
        "taal": r["taal"], "genre": r.get("genre"), "woorden": s["woorden"],
        "niveau": r["niveau"], "score_per_1000": r["score_per_1000"], "laag_onder": r["drempels"]["laag_onder"],
        "flesch": s.get("flesch"), "mattr": s.get("mattr") if s["woorden"] >= 300 else None,
        "patronen": sum(1 for b in r["bevindingen"] if b["punten"] > 0),
        "taalronde": taalronde, "oordeel": oordeel,
        "top": [{"cat": c, "punten": round(p, 1)} for c, p in top],
        "acceptatie": acc, "kort": bool(r.get("waarschuwingen")),
    }


def teken(w: dict, uit: Path, titel: str | None = None) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    taal = "en" if w["taal"] == "en" else "nl"
    t = TEKST[taal]
    acc = w.get("acceptatie") or {}
    eisen = acc.get("eisen") or {}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
    fig = plt.figure(figsize=(12, 5.6), dpi=150, facecolor=BLOK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 120)
    ax.set_ylim(0, 56)
    ax.axis("off")

    # kopregel
    ax.add_patch(FancyBboxPatch((0, 48), 120, 8, boxstyle="square,pad=0", fc=PRIMAIR, ec="none"))
    kop = t["titel"] + (f": {titel}" if titel else "")
    ax.text(3, 52, kop[:80], color="white", fontsize=15, fontweight="bold", va="center")
    sub = f"{w['woorden']} {t['woorden']}" + (f"  ·  {w['genre']}" if w.get("genre") else "")
    ax.text(117, 52, sub, color="#cfe3e7", fontsize=10, va="center", ha="right")

    # oordeel en klaar-regel
    y_oordeel = 44.3
    if w.get("oordeel"):
        ax.text(3, y_oordeel, w["oordeel"], color=INKT, fontsize=13, fontweight="bold", va="center")
    regel = []
    if acc:
        regel.append(t["klaar_ja"] if acc.get("voldaan") else t["klaar_nee"])
    if w.get("kort"):
        regel.append(t["kort"])
    if regel:
        ax.text(117, y_oordeel, "  ·  ".join(regel), color=ZACHT, fontsize=10, va="center", ha="right")

    # kaarten
    def kaart(x: float, kopje: str, groot: str, klein: str, kleur: str) -> None:
        ax.add_patch(FancyBboxPatch((x, 26), 26.5, 14.5, boxstyle="round,pad=0,rounding_size=1.6", fc=VLAK, ec=LIJN,
                                    lw=1))
        ax.add_patch(FancyBboxPatch((x, 26), 1.1, 14.5, boxstyle="square,pad=0", fc=kleur, ec="none"))
        ax.text(x + 3, 37.6, kopje, color=ZACHT, fontsize=10, va="center")
        ax.text(x + 3, 32.6, groot, color=kleur, fontsize=21, fontweight="bold", va="center")
        ax.text(x + 3, 28.4, klein, color=ZACHT, fontsize=8.5, va="center")

    kaart(2, t["ai"], t["niveau"][w["niveau"]], t["per1000"].format(s=_getal(w["score_per_1000"], taal),
          l=_getal(w["laag_onder"], taal, 0)), NIVEAU_KLEUR[w["niveau"]])

    f = w.get("flesch")
    fmin, fmax = eisen.get("flesch_min"), eisen.get("flesch_max")
    f_ok = f is None or not fmin or (f >= fmin and (not fmax or f <= fmax))
    doel = (f"{fmin}-{fmax}" if fmax else f"≥ {fmin}") if fmin else None
    kaart(31.5, f"{t['lees']} ({t['flesch']})", _getal(f, taal), t["doel"].format(a=doel) if doel else t["hoger"],
          PRIMAIR if f_ok else LET_OP)

    m = w.get("mattr")
    mmin = eisen.get("mattr_min")
    m_ok = m is None or not mmin or m >= mmin
    klein_m = t["kort_mattr"] if m is None else (t["doel"].format(a=f"≥ {_getal(mmin, taal, 2)}") if mmin else
                                                 t["mattr"])
    kaart(61, t["var"], _getal(m, taal, 2), klein_m, PRIMAIR if m_ok else LET_OP)

    if w.get("taalronde") is not None:
        kaart(90.5, t["taalronde"], str(w["taalronde"]), t["verbeteringen"], PRIMAIR)
    else:
        kaart(90.5, t["patronen"], str(w["patronen"]), t["gevonden"], PRIMAIR if w["patronen"] == 0 else LET_OP)

    # staafdiagram
    ax.text(3, 21.5, t["zwaarst"], color=INKT, fontsize=11, fontweight="bold", va="center")
    top = w["top"]
    if not top:
        ax.text(3, 15, t["geen"], color=ZACHT, fontsize=10, va="center")
    else:
        hoogste = max(x["punten"] for x in top)
        idx = 0 if taal == "nl" else 1
        for i, item in enumerate(top):
            y = 17.8 - i * 2.85
            label = CATEGORIE.get(item["cat"], (item["cat"], item["cat"]))[idx]
            ax.text(3, y, label, color=INKT, fontsize=9.5, va="center")
            breedte = 70 * item["punten"] / hoogste
            ax.add_patch(FancyBboxPatch((36, y - 0.9), max(breedte, 0.6), 1.8,
                                        boxstyle="round,pad=0,rounding_size=0.5", fc=ACCENT, ec="none"))
            ax.text(36 + max(breedte, 0.6) + 1.2, y, _getal(item["punten"], taal), color=ZACHT, fontsize=9,
                    va="center")

    uit.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(uit, dpi=150, facecolor=BLOK)
    plt.close(fig)
    return uit


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(prog="dq reviewgrafiek", description="Overzichtsbeeld voor een review")
    p.add_argument("--input", "-i", required=True, help="De beoordeelde tekst (.md, .txt, .docx)")
    p.add_argument("--output", "-o", required=True, help="Pad van de png")
    p.add_argument("--genre")
    p.add_argument("--taal", default="auto", choices=["auto", "nl", "en"])
    p.add_argument("--titel")
    p.add_argument("--oordeel", help='Het eindoordeel, bijvoorbeeld "Kleine aanpassingen"')
    p.add_argument("--taalronde", type=int, help="Aantal fouten uit de taalronde")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    nooit, wel = tells.eigen_regels()
    r = tells.analyseer(tells._lees(a.input), a.taal, a.genre, tells.stemprofiel(), nooit, wel)
    w = waarden(r, a.taalronde, a.oordeel)
    pad = teken(w, Path(a.output), a.titel).resolve()
    if a.json:
        print(json.dumps({"png": pad.as_posix(), **w}, ensure_ascii=False, indent=2))
    else:
        print(pad.as_posix())
