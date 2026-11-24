"""AI-patronen (tells) vinden in Nederlandse en Engelse tekst.

  dq tells --input <bestand> [--taal nl|en|auto] [--genre G] [--json] [--geen-stem]
  dq tells --compare <origineel> <nieuw> [--taal ..] [--genre ..] [--json]
  cat tekst.md | dq tells

Wat het meet (uitleg: gidsen/nl/humaniseren.md en gidsen/en/humanize.md):
  woordkeus (sterk/zwak, clusters, anglicismen), frasen (aanloop, aankondiging, afsluiter, vulling, vage bron,
  chatbotresten, LinkedIn-formules), structuur (niet-X-maar-Y, retorische aanloop, drieslagen, herhaalde
  zins- en alineabegins, connectoren), ritme (te gelijk, of overgecorrigeerd: te veel korte zinnen), opmaak
  (streepjes, vet in lopende tekst, emoji, title case, hashtags, broetry), passief, eigen regels uit de werkmap.

Het eigen stemprofiel (dq stem analyse) gaat voor: gebruikt de schrijver zelf veel streepjes of korte zinnen,
dan telt dat niet als tell. De score is per 1000 woorden; de lat ligt hoger bij informele genres.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

from dutchquill import paden
from dutchquill import tekst as tk

LOS = {"mail", "linkedin", "social", "kort"}
CITAAT = re.compile(r'"[^"\n]{2,300}"|“[^”\n]{2,300}”|„[^”“\n]{2,300}[”“]|‘[^’\n]{2,200}’')
DREMPELS = {"streng": (4, 9), "los": (6, 12)}  # (laag <, gemiddeld <) punten per 1000 woorden


@lru_cache(maxsize=4)
def data(taal: str) -> dict:
    from ruamel.yaml import YAML
    eigen = paden.data() / "gidsen" / "data" / f"tells_{taal}.yaml"  # bijgewerkt via /dutchquill:bijwerken
    basis = paden.root() / "gidsen" / "data" / f"tells_{taal}.yaml"
    kandidaten = [p for p in (eigen, basis) if p.is_file()]
    y = YAML(typ="safe")
    geladen = [(y.load(p.read_text(encoding="utf-8")), p) for p in kandidaten]
    geladen.sort(key=lambda dp: str(dp[0].get("bijgewerkt", "")), reverse=True)
    return geladen[0][0]


def _patroon(term: str) -> re.Pattern:
    return re.compile(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", re.IGNORECASE)


def _context(tekst: str, start: int, eind: int, marge: int = 40) -> str:
    return ("…" if start > marge else "") + tekst[max(0, start - marge):eind + marge].replace("\n", " ").strip() + (
        "…" if eind + marge < len(tekst) else "")


def eigen_regels() -> tuple[list[str], list[str]]:
    """Lees 'Nooit gebruiken' en 'Juist wel' uit eigen-regels.md in de werkmap (als die er is)."""
    try:
        from dutchquill.config import effectief
        pad = effectief()["mappen"].get("eigen_regels")
    except Exception:
        return [], []
    if not pad or not Path(pad).is_file():
        return [], []
    nooit, wel, sectie = [], [], None
    for r in Path(pad).read_text(encoding="utf-8").splitlines():
        s = r.strip()
        if s.startswith("#"):
            k = s.lower()
            sectie = "nooit" if "nooit" in k or "never" in k else "wel" if ("juist" in k or "allowed" in k) else None
            continue
        if not s or s.startswith("<!--") or sectie is None:
            continue
        s = re.sub(r"^[-*]\s*", "", s).strip()
        (nooit if sectie == "nooit" else wel).append(s)
    return nooit, wel


def stemprofiel() -> dict | None:
    try:
        from dutchquill.config import effectief
        e = effectief()
        if not e["stem"].get("gebruiken"):
            return None
        pad = Path(e["mappen"]["intern"]) / "stem.json"
        return json.loads(pad.read_text(encoding="utf-8")) if pad.is_file() else None
    except Exception:
        return None


def analyseer(tekst: str, taal: str = "auto", genre: str | None = None, stem: dict | None = None,
              nooit: list[str] | None = None, wel: list[str] | None = None) -> dict:
    taal = tk.taal_van(tekst) if taal in ("auto", None) else taal
    d = data(taal)
    rs = tk.regels(tekst)
    als = tk.alineas(rs)
    stat = tk.statistiek(tekst, taal)
    bev: list[dict] = []
    uitzonderingen = [u.lower() for u in (d.get("genre_uitzonderingen", {}).get(genre or "", []) or [])]
    witte = [w.lower() for w in d.get("whitelist", [])] + [w.lower() for w in (wel or [])]

    # Teksten om in te zoeken: proza en lijsten, per regel (voor regelnummers)
    zoekregels = [r for r in rs if r.soort in ("proza", "lijst")]

    def in_citaat(regeltekst: str, pos: int) -> bool:
        """Staat deze positie tussen aanhalingstekens? Citaten en voorbeelden tellen niet mee."""
        for m in CITAAT.finditer(regeltekst):
            if m.start() < pos < m.end():
                return True
        return False

    def treffers(rx: re.Pattern, woord: bool = False, filter_: bool = True):
        for r in zoekregels:
            for m in rx.finditer(r.tekst):
                if in_citaat(r.tekst, m.start()):
                    continue
                ctx = r.tekst.lower()
                if not filter_:  # eigen 'nooit'-regels gaan altijd voor
                    yield r, m
                    continue
                if any(w in ctx and m.group(0).lower() in w for w in witte):
                    continue
                if any(u == m.group(0).lower() for u in uitzonderingen):
                    continue  # genre-uitzondering: alleen een exacte treffer ("trots" wel, "trots en dankbaar" niet)
                yield r, m

    bezet: dict[int, list[tuple[int, int]]] = {}

    def voeg(cat, punten, r, m_or_tekst, uitleg, alt=None, sterkte="sterk"):
        if isinstance(m_or_tekst, re.Match) and cat in ("woord", "woord_zwak", "anglicisme", "eigen_regel"):
            span = m_or_tekst.span()
            if any(span[0] < e and s < span[1] for s, e in bezet.get(r.nr, [])):
                return  # valt binnen een langere treffer ("breed scala aan" en "scala aan")
            bezet.setdefault(r.nr, []).append(span)
        if isinstance(m_or_tekst, re.Match):
            ctx = _context(r.tekst, m_or_tekst.start(), m_or_tekst.end())
            match = m_or_tekst.group(0)
        else:
            ctx, match = m_or_tekst, None
        bev.append({"cat": cat, "sterkte": sterkte, "punten": punten, "regel": r.nr if r else None,
                    "match": match, "context": ctx, "uitleg": uitleg, **({"alt": alt} if alt else {})})

    # 1. Eigen regels (hard)
    for term in nooit or []:
        for r, m in treffers(_patroon(term), filter_=False):
            voeg("eigen_regel", 2, r, m, "Staat in jouw eigen-regels.md onder 'nooit'.")

    # 2. Woordkeus
    per_term = Counter()
    for item in sorted(d["woorden"].get("sterk", []), key=lambda x: -len(x["term"])):
        for r, m in treffers(_patroon(item["term"]), woord=True):
            per_term[item["term"]] += 1
            if per_term[item["term"]] <= 3:
                voeg("woord", 1, r, m, "Sterke AI-tell" + (f" ({item['tijdperk']})" if item.get("tijdperk") else ""),
                     item.get("alt"))
    zwak_hits: list[tuple[int, str]] = []
    for item in sorted(d["woorden"].get("zwak", []), key=lambda x: -len(x["term"])):
        for r, m in treffers(_patroon(item["term"]), woord=True):
            zwak_hits.append((r.nr, item["term"]))
            voeg("woord_zwak", 0, r, m, "Zwakke tell: alleen een probleem in een cluster.", item.get("alt"), "zwak")
    for item in d["woorden"].get("stammen", []) or []:
        for r, m in treffers(re.compile(item["regex"], re.IGNORECASE)):
            sterk = item.get("sterkte") == "sterk"
            voeg("woord" if sterk else "woord_zwak", 1 if sterk else 0, r, m, f"Vorm van '{item['term']}'.",
                 item.get("alt"), item.get("sterkte", "zwak"))
            if not sterk:
                zwak_hits.append((r.nr, item["term"]))
    for item in d.get("anglicismen", []) or []:
        for r, m in treffers(_patroon(item["term"])):
            voeg("anglicisme", 1, r, m, "Letterlijk vertaald uit het Engels.", item.get("alt"))

    # Clusters van zwakke tells: 3+ verschillende binnen ± 8 regels
    gemeld: list[set] = []
    for nr, _ in sorted(zwak_hits):
        buren = {t for n, t in zwak_hits if abs(n - nr) <= 8}
        if len(buren) >= 3 and not any(len(buren & g) >= 0.6 * len(buren) for g in gemeld):
            gemeld.append(buren)
            bev.append({"cat": "cluster", "sterkte": "sterk", "punten": 1.5, "regel": nr, "match": None,
                        "context": ", ".join(sorted(buren)),
                        "uitleg": "Meerdere zwakke tells dicht bij elkaar: zo klinkt AI-tekst."})
    if stat["woorden"] >= 150 and len(zwak_hits) / stat["woorden"] > 0.02:
        bev.append({"cat": "dichtheid", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                    "context": f"{len(zwak_hits)} zwakke tells op {stat['woorden']} woorden",
                    "uitleg": "Hoge dichtheid van zwakke tells."})

    # 3. Frasen
    frases = d.get("frases", {})
    uitleg_frase = {
        "aanloop": "Brede aanloop zonder inhoud: begin met de zaak zelf.",
        "aankondiging": "Tekst over de tekst: zeg het gewoon.",
        "afsluiter": "Samenvattende afsluiter die niets toevoegt.",
        "vulling": "Vulzin: schrappen of concreet maken.",
        "vage_bron": "Vage bron: wie precies? Noem de bron of schrap de claim.",
        "chatbot": "Restje chatbot-taal.",
        "linkedin": "Bekende LinkedIn-formule.",
    }
    for soort, lijst in frases.items():
        if soort == "linkedin" and genre not in ("linkedin", "social"):
            continue
        punten = 2 if soort == "chatbot" else 1
        for rx in lijst or []:
            for r, m in treffers(re.compile(rx, re.IGNORECASE | re.MULTILINE)):
                voeg(f"frase_{soort}", punten, r, m, uitleg_frase.get(soort, "Formule."))

    # 4. Structuur
    struct = d.get("structuur", {})
    n_par = 0
    for rx in struct.get("negatief_parallel", []):
        for r, m in treffers(re.compile(rx, re.IGNORECASE)):
            n_par += 1
            voeg("niet_x_maar_y", 1 if n_par <= 3 else 0, r, m,
                 "Niet-X-maar-Y-constructie: zeg gewoon wat het wél is.")
    if struct.get("retorische_aanloop"):
        rx = re.compile(struct["retorische_aanloop"])
        n = 0
        for r, m in treffers(rx):
            if len(tk.woorden(m.group(1))) <= 4:
                n += 1
                voeg("retorische_aanloop", 0.5 if n <= 4 else 0, r, m,
                     "Korte vraag als aanloop ('Het resultaat? ...').")

    drie = re.compile(r"\b\w+(?:\s\w+)?,\s\w+(?:\s\w+)?,?\s(?:en|of|and|or)\s\w+", re.IGNORECASE)
    n_drie = sum(len(drie.findall(r.tekst)) for r in zoekregels if r.soort == "proza")
    if stat["woorden"] >= 120 and n_drie / stat["woorden"] * 150 > 1.2:
        bev.append({"cat": "drieslag", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                    "context": f"{n_drie} opsommingen van drie",
                    "uitleg": "Veel drieslagen: AI zet dingen graag in drieën. Varieer: twee, vier, of één."})

    alle_zinnen = [(nr, z) for a in als for nr, z in a.zinnen]
    begins = [tk.woorden(z)[0].lower() for _, z in alle_zinnen if tk.woorden(z)]
    for a in als:
        b = Counter(tk.woorden(z)[0].lower() for _, z in a.zinnen if tk.woorden(z))
        for w, n in b.items():
            if n >= 3 and w not in ("de", "het", "the", "ik", "i", "we", "wij"):
                bev.append({"cat": "zinsbegin", "sterkte": "sterk", "punten": 0.5, "regel": a.regel, "match": w,
                            "context": f"'{w}' begint {n} zinnen in één alinea", "uitleg": "Herhaald zinsbegin."})
    if len(als) >= 4:
        ab = Counter(tk.woorden(a.tekst)[0].lower() for a in als if tk.woorden(a.tekst))
        for w, n in ab.items():
            if n >= 3 and w not in ("de", "het", "the"):
                bev.append({"cat": "alineabegin", "sterkte": "sterk", "punten": 1, "regel": None, "match": w,
                            "context": f"{n} alinea's beginnen met '{w}'", "uitleg": "Herhaald alineabegin."})
    connectoren = {c.lower() for c in d.get("connectoren", [])}
    if len(begins) >= 6:
        aandeel = sum(b in connectoren for b in begins) / len(begins)
        if aandeel > 0.25:
            bev.append({"cat": "connectoren", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                        "context": f"{round(aandeel * 100)}% van de zinnen begint met een verbindingswoord",
                        "uitleg": "Te veel zinnen beginnen met bovendien/daarnaast/echter."})

    # 5. Ritme
    stem = stem or {}
    if stat["zinnen"] >= 8:
        if stat["stdev_zinslengte"] < 4:
            bev.append({"cat": "ritme_gelijk", "sterkte": "sterk", "punten": 1.5, "regel": None, "match": None,
                        "context": f"zinslengte {stat['gem_zinslengte']} ± {stat['stdev_zinslengte']} woorden",
                        "uitleg": "Zinnen zijn bijna allemaal even lang. Wissel kort en lang af."})
        eigen_kort = stem.get("korte_zinnen_pct", 0)
        if genre not in LOS and stat["korte_zinnen_pct"] > max(45, eigen_kort + 15):
            bev.append({"cat": "ritme_overgecorrigeerd", "sterkte": "sterk", "punten": 1.5, "regel": None,
                        "match": None, "context": f"{stat['korte_zinnen_pct']}% van de zinnen is korter dan 8 woorden",
                        "uitleg": "Overcorrectie: te veel korte, afgekapte zinnen (de nieuwe tell sinds 2026)."})
    al_lengtes = [len(tk.woorden(a.tekst)) for a in als]
    if len(al_lengtes) >= 4 and statistics.mean(al_lengtes) > 20:
        cv = statistics.pstdev(al_lengtes) / statistics.mean(al_lengtes)
        if cv < 0.2:
            bev.append({"cat": "alinea_gelijk", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                        "context": f"alinea's van {min(al_lengtes)}-{max(al_lengtes)} woorden",
                        "uitleg": "Alle alinea's zijn ongeveer even lang."})
    # Bij procedures en README's is herhaling van vaste termen juist goed.
    if genre not in ("sop", "readme") and stat["mattr"] is not None and stat["woorden"] >= 300 and stat["mattr"] < 0.68:
        bev.append({"cat": "woordenschat", "sterkte": "zwak", "punten": 1, "regel": None, "match": None,
                    "context": f"MATTR {stat['mattr']}", "uitleg": "Weinig variatie in woordkeus: veel herhaling."})

    # 6. Opmaak en interpunctie
    if stem.get("streepjes_per_1000", 0) < 1.5:
        n = 0
        for r, m in treffers(tk.STREEPJE):
            n += 1
            voeg("streepje", 0.5 if n <= 4 else 0, r, m,
                 "Gedachtestreepje als leesteken: zwak signaal (sinds 2026 minder typisch). Komma of punt?",
                 sterkte="zwak")
    vet = re.compile(r"(?<=\w[ ,])\*\*[^*\n]{2,60}\*\*(?=[ ,.]\w)")
    n = 0
    for r, m in treffers(vet):
        if r.soort == "proza":
            n += 1
            voeg("vet", 0.5 if n <= 4 else 0, r, m, "Vet midden in een zin, als versiering.", sterkte="zwak")
    for r in rs:
        if r.soort in ("kop", "lijst") and tk.EMOJI.match(r.tekst.strip()):
            if genre in ("linkedin", "social") and r.soort == "lijst":
                continue
            bev.append({"cat": "emoji", "sterkte": "sterk", "punten": 1, "regel": r.nr, "match": r.tekst[:40],
                        "context": r.tekst[:80], "uitleg": "Emoji vooraan in een kop of opsomming."})
    if genre in ("linkedin", "social"):
        n_emoji_lijst = sum(1 for r in rs if r.soort in ("lijst", "proza") and tk.EMOJI.match(r.tekst.strip()))
        if n_emoji_lijst >= 3:
            bev.append({"cat": "emoji", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                        "context": f"{n_emoji_lijst} opsommingen beginnen met een emoji",
                        "uitleg": "Emoji-opsommingen: herkenbare AI-post."})
        hashtags = re.findall(r"(?<!\w)#\w+", tekst)
        if len(hashtags) > 3:
            bev.append({"cat": "hashtags", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                        "context": " ".join(hashtags[:8]), "uitleg": "Meer dan drie hashtags."})
        if len(als) >= 6 and sum(len(a.zinnen) == 1 for a in als) / len(als) > 0.6:
            bev.append({"cat": "broetry", "sterkte": "sterk", "punten": 1, "regel": None, "match": None,
                        "context": f"{sum(len(a.zinnen) == 1 for a in als)} van {len(als)} alinea's is één zin",
                        "uitleg": "Elke zin een eigen alinea ('broetry')."})
    if taal == "nl":
        n = 0
        for r in rs:
            if r.soort != "kop":
                continue
            w = r.tekst.split()
            hoofd = [x for x in w[1:] if len(x) > 3 and x[0].isupper() and not x.isupper()]
            if len(w) >= 3 and len(hoofd) >= 2:
                n += 1
                bev.append({"cat": "title_case", "sterkte": "zwak", "punten": 0.5 if n <= 3 else 0, "regel": r.nr,
                            "match": r.tekst, "context": r.tekst,
                            "uitleg": "Hoofdletters Als In Een Engelse Kop; Nederlands schrijft alleen de eerste."})
    # Kop herhaald in eerste zin
    for i, r in enumerate(rs):
        if r.soort != "kop" or len(tk.woorden(r.tekst)) < 2:
            continue
        volgende = next((x for x in rs[i + 1:] if x.soort != "leeg"), None)
        if volgende and volgende.soort == "proza":
            kopw = {w.lower() for w in tk.woorden(r.tekst) if len(w) > 3}
            eerste = tk.zinnen(volgende.tekst)[:1]
            if kopw and eerste:
                zw = {w.lower() for w in tk.woorden(eerste[0])}
                if len(kopw & zw) / len(kopw) >= 0.75 and len(kopw) >= 2:
                    bev.append({"cat": "kop_herhaald", "sterkte": "zwak", "punten": 0.5, "regel": volgende.nr,
                                "match": None, "context": eerste[0][:100],
                                "uitleg": "De eerste zin herhaalt de kop."})

    # 7. Passief
    if stat["zinnen"] >= 6:
        pas = [re.compile(p, re.IGNORECASE) for p in d.get("passief", [])]
        n_pas = sum(any(p.search(z) for p in pas) for _, z in alle_zinnen)
        aandeel = n_pas / stat["zinnen"]
        grens = 0.45 if genre in ("rapport", "onderzoeksrapport", "adviesrapport") else 0.30
        if aandeel > grens:
            bev.append({"cat": "passief", "sterkte": "zwak", "punten": 1, "regel": None, "match": None,
                        "context": f"{round(aandeel * 100)}% van de zinnen is passief",
                        "uitleg": "Veel lijdende vorm: wie doet wat? Passief mag in een methodesectie."})

    # Score
    punten = sum(b["punten"] for b in bev)
    per1000 = round(punten / max(stat["woorden"], 250) * 1000, 1)
    laag, midden = DREMPELS["los" if genre in LOS else "streng"]
    niveau = "laag" if per1000 < laag else "gemiddeld" if per1000 < midden else "hoog"

    stem_adv = []
    if stem:
        for sleutel, naam in (("gem_zinslengte", "gemiddelde zinslengte"), ("korte_zinnen_pct", "aandeel korte zinnen"),
                              ("dubbelepunt_per_1000", "dubbele punten"), ("uitroep_per_1000", "uitroeptekens")):
            eigen, nu = stem.get(sleutel), stat.get(sleutel)
            if eigen and nu is not None and eigen > 0 and abs(nu - eigen) / eigen > 0.4 and stat["woorden"] >= 120:
                stem_adv.append(f"{naam}: jij {eigen}, deze tekst {nu}")
    return {
        "taal": taal,
        "genre": genre,
        "score_per_1000": per1000,
        "punten": round(punten, 1),
        "niveau": niveau,
        "drempels": {"laag_onder": laag, "gemiddeld_onder": midden},
        "statistiek": stat,
        "bevindingen": sorted(bev, key=lambda b: (-b["punten"], b["regel"] or 0)),
        "per_categorie": dict(Counter(b["cat"] for b in bev if b["punten"] > 0)),
        "stem_afwijkingen": stem_adv,
    }


# Weergave in het Engels voor Engelse tekst. Alleen de mensleesbare uitvoer; de JSON blijft gelijk voor de skills.
EN_UITLEG = {
    "Alle alinea's zijn ongeveer even lang.": "All paragraphs are about the same length.",
    "Bekende LinkedIn-formule.": "Well-known LinkedIn formula.",
    "Brede aanloop zonder inhoud: begin met de zaak zelf.":
        "Broad opening without content: start with the point itself.",
    "De eerste zin herhaalt de kop.": "The first sentence repeats the heading.",
    "Elke zin een eigen alinea ('broetry').": "Every sentence its own paragraph ('broetry').",
    "Emoji vooraan in een kop of opsomming.": "Emoji at the start of a heading or list item.",
    "Emoji-opsommingen: herkenbare AI-post.": "Emoji lists: a recognisable AI post.",
    "Gedachtestreepje als leesteken: zwak signaal (sinds 2026 minder typisch). Komma of punt?":
        "Dash as punctuation: weak signal (less typical since 2026). Comma or full stop?",
    "Herhaald alineabegin.": "Repeated paragraph opening.",
    "Herhaald zinsbegin.": "Repeated sentence opening.",
    "Hoge dichtheid van zwakke tells.": "High density of weak tells.",
    "Hoofdletters Als In Een Engelse Kop; Nederlands schrijft alleen de eerste.":
        "Title Case Headings; Dutch only capitalises the first word.",
    "Korte vraag als aanloop ('Het resultaat? ...').": "Short question as a lead-in ('The result? ...').",
    "Letterlijk vertaald uit het Engels.": "Literal translation from English.",
    "Meer dan drie hashtags.": "More than three hashtags.",
    "Meerdere zwakke tells dicht bij elkaar: zo klinkt AI-tekst.":
        "Several weak tells close together: this is how AI text sounds.",
    "Niet-X-maar-Y-constructie: zeg gewoon wat het wél is.": "Not-X-but-Y construction: just say what it is.",
    "Overcorrectie: te veel korte, afgekapte zinnen (de nieuwe tell sinds 2026).":
        "Overcorrection: too many short, clipped sentences (the new tell since 2026).",
    "Restje chatbot-taal.": "Leftover chatbot language.",
    "Samenvattende afsluiter die niets toevoegt.": "Summarising closer that adds nothing.",
    "Staat in jouw eigen-regels.md onder 'nooit'.": "Listed in your eigen-regels.md under 'never'.",
    "Te veel zinnen beginnen met bovendien/daarnaast/echter.":
        "Too many sentences start with moreover/furthermore/however.",
    "Tekst over de tekst: zeg het gewoon.": "Text about the text: just say it.",
    "Vage bron: wie precies? Noem de bron of schrap de claim.":
        "Vague source: who exactly? Name the source or drop the claim.",
    "Veel drieslagen: AI zet dingen graag in drieën. Varieer: twee, vier, of één.":
        "Many triplets: AI likes to list things in threes. Vary: two, four, or one.",
    "Veel lijdende vorm: wie doet wat? Passief mag in een methodesectie.":
        "Lots of passive voice: who does what? Passive is fine in a methods section.",
    "Vet midden in een zin, als versiering.": "Bold in the middle of a sentence, as decoration.",
    "Vulzin: schrappen of concreet maken.": "Filler sentence: cut it or make it concrete.",
    "Weinig variatie in woordkeus: veel herhaling.": "Little variety in word choice: lots of repetition.",
    "Zinnen zijn bijna allemaal even lang. Wissel kort en lang af.":
        "Sentences are almost all the same length. Mix short and long.",
    "Zwakke tell: alleen een probleem in een cluster.": "Weak tell: only a problem in a cluster.",
    "Formule.": "Formula.",
}
EN_PATRONEN = [
    (r"^Sterke AI-tell(.*)$", r"Strong AI tell\1"),
    (r"^Vorm van '(.+)'\.$", r"Form of '\1'."),
    (r"^(\d+) zwakke tells op (\d+) woorden$", r"\1 weak tells in \2 words"),
    (r"^(\d+) opsommingen van drie$", r"\1 lists of three"),
    (r"^'(.+)' begint (\d+) zinnen in één alinea$", r"'\1' starts \2 sentences in one paragraph"),
    (r"^(\d+) alinea's beginnen met '(.+)'$", r"\1 paragraphs start with '\2'"),
    (r"^(\d+)% van de zinnen begint met een verbindingswoord$", r"\1% of sentences start with a connector"),
    (r"^zinslengte (.+) woorden$", r"sentence length \1 words"),
    (r"^(\d+)% van de zinnen is korter dan 8 woorden$", r"\1% of sentences are shorter than 8 words"),
    (r"^alinea's van (.+) woorden$", r"paragraphs of \1 words"),
    (r"^(\d+) opsommingen beginnen met een emoji$", r"\1 list items start with an emoji"),
    (r"^(\d+) van (\d+) alinea's is één zin$", r"\1 of \2 paragraphs are a single sentence"),
    (r"^(\d+)% van de zinnen is passief$", r"\1% of sentences are passive"),
]
NIVEAU_EN = {"laag": "LOW", "gemiddeld": "MEDIUM", "hoog": "HIGH"}


def _en(tekst: str) -> str:
    if tekst in EN_UITLEG:
        return EN_UITLEG[tekst]
    for patroon, vervanging in EN_PATRONEN:
        if re.match(patroon, tekst):
            return re.sub(patroon, vervanging, tekst)
    return tekst


def rapport(r: dict, titel: str | None = None) -> str:
    s = r["statistiek"]
    en = r.get("taal") == "en"
    if en:
        titel = {"Voor": "Before", "Na": "After"}.get(titel, titel) or "Analysis"
        regels = [f"{titel}: AI patterns {NIVEAU_EN[r['niveau']]} ({r['score_per_1000']} per 1000 words; "
                  f"low < {r['drempels']['laag_onder']}) | {s['woorden']} words, {s['zinnen']} sentences, "
                  f"sentence length {s['gem_zinslengte']} ± {s['stdev_zinslengte']}"
                  + (f", readability {s['flesch']}" if s.get("flesch") is not None else "")]
    else:
        regels = [f"{titel or 'Analyse'}: AI-patronen {r['niveau'].upper()} ({r['score_per_1000']} per 1000 woorden; "
                  f"laag < {r['drempels']['laag_onder']}) | {s['woorden']} woorden, {s['zinnen']} zinnen, "
                  f"zinslengte {s['gem_zinslengte']} ± {s['stdev_zinslengte']}"
                  + (f", leesbaarheid {s['flesch']}" if s.get("flesch") is not None else "")]
    vertaal = _en if en else (lambda x: x)
    tellend = [b for b in r["bevindingen"] if b["punten"] > 0]
    zwak = [b for b in r["bevindingen"] if b["punten"] == 0 and b["cat"] == "woord_zwak"]
    for b in tellend[:25]:
        plek = f"r{b['regel']}" if b["regel"] else ("text" if en else "tekst")
        alt = f"  → {', '.join(b['alt'][:3])}" if b.get("alt") else ""
        regels.append(f"- [{b['cat']}] {plek}: {vertaal(b['context'])}\n    {vertaal(b['uitleg'])}{alt}")
    if len(tellend) > 25:
        regels.append(f"- ... and {len(tellend) - 25} more findings (see --json)" if en
                      else f"- ... en nog {len(tellend) - 25} bevindingen (zie --json)")
    if zwak:
        woorden = ", ".join(sorted({b["match"].lower() for b in zwak}))
        regels.append(f"Weak tells (only a problem in a cluster): {woorden}" if en
                      else f"Zwakke tells (alleen erg in een cluster): {woorden}")
    if r["stem_afwijkingen"]:
        regels.append(("Different from your voice: " if en else "Afwijkend van jouw stem: ")
                      + "; ".join(r["stem_afwijkingen"]))
    if not tellend:
        regels.append("No counting patterns found." if en else "Geen tellende patronen gevonden.")
    return "\n".join(regels)


def _lees(pad: str | None) -> str:
    if not pad or pad == "-":
        return sys.stdin.read()
    p = Path(pad)
    if p.suffix.lower() == ".docx":
        from dutchquill.docx_tekst import extract_text
        return extract_text(str(p))
    return p.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    p = argparse.ArgumentParser(prog="dq tells", description="AI-patronen vinden (NL en EN)")
    p.add_argument("--input", "-i", help="Bestand (.md, .txt, .docx); zonder: stdin")
    p.add_argument("--compare", nargs=2, metavar=("ORIGINEEL", "NIEUW"))
    p.add_argument("--taal", default="auto", choices=["auto", "nl", "en"])
    p.add_argument("--genre")
    p.add_argument("--json", action="store_true")
    p.add_argument("--geen-stem", action="store_true", help="Eigen stemprofiel niet meewegen")
    a = p.parse_args(argv)
    nooit, wel = eigen_regels()
    stem = None if a.geen_stem else stemprofiel()
    if a.compare:
        voor = analyseer(_lees(a.compare[0]), a.taal, a.genre, stem, nooit, wel)
        na = analyseer(_lees(a.compare[1]), a.taal, a.genre, stem, nooit, wel)
        uit = {"voor": voor, "na": na, "delta_per_1000": round(na["score_per_1000"] - voor["score_per_1000"], 1)}
        if a.json:
            print(json.dumps(uit, ensure_ascii=False, indent=2))
        else:
            print(rapport(voor, "Voor"))
            print()
            print(rapport(na, "Na"))
            if voor.get("taal") == "en":
                print(f"\nDifference: {uit['delta_per_1000']:+} per 1000 words "
                      f"({voor['niveau']} → {na['niveau']})".replace("laag", "low").replace("gemiddeld", "medium")
                      .replace("hoog", "high"))
            else:
                print(f"\nVerschil: {uit['delta_per_1000']:+} per 1000 woorden ({voor['niveau']} → {na['niveau']})")
        return
    r = analyseer(_lees(a.input), a.taal, a.genre, stem, nooit, wel)
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else rapport(r))
