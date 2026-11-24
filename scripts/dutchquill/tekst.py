"""Gedeelde tekstfuncties: opmaak strippen met behoud van regelnummers, zinnen en alinea's, statistiek."""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

AFKORTINGEN = {
    "bijv", "bv", "o.a", "d.w.z", "m.a.w", "i.p.v", "t.o.v", "z.g.a.n", "e.d", "enz", "etc", "nr", "dr", "drs",
    "ir", "mr", "prof", "ca", "jl", "vs", "e.g", "i.e", "mrs", "ms", "st", "no", "fig", "p", "pp", "vol",
    "red", "e.a", "al", "z.d", "n.d", "resp", "evt", "incl", "excl", "max", "min", "zgn", "m.b.t", "t.a.v",
}
WOORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:['’\-][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)*")
NL_STOP = {"de", "het", "een", "en", "van", "is", "dat", "die", "niet", "op", "te", "voor", "met", "zijn", "er",
           "ook", "maar", "als", "bij", "wordt", "naar", "je", "we", "ik", "om", "aan", "dit", "worden"}
EN_STOP = {"the", "a", "an", "and", "of", "is", "that", "to", "in", "for", "with", "it", "on", "as", "are", "be",
           "this", "was", "by", "or", "not", "but", "you", "we", "i", "at", "from", "have"}


@dataclass
class Regel:
    nr: int
    tekst: str
    soort: str  # proza | kop | lijst | leeg


@dataclass
class Alinea:
    regel: int
    tekst: str
    zinnen: list[tuple[int, str]] = field(default_factory=list)


def taal_van(tekst: str) -> str:
    woorden = [w.lower() for w in WOORD.findall(tekst[:5000])]
    nl = sum(w in NL_STOP for w in woorden)
    en = sum(w in EN_STOP for w in woorden)
    return "en" if en > nl * 1.2 else "nl"


def regels(tekst: str) -> list[Regel]:
    """Deel de tekst op in regels; code, tabellen, frontmatter, HTML-commentaar en URL-regels worden 'leeg'
    gemaakt (regelnummers blijven kloppen)."""
    uit: list[Regel] = []
    in_code = in_front = in_comment = False
    for i, r in enumerate(tekst.splitlines(), 1):
        s = r.strip()
        if i == 1 and s == "---":
            in_front = True
            uit.append(Regel(i, "", "leeg"))
            continue
        if in_front:
            if s == "---":
                in_front = False
            uit.append(Regel(i, "", "leeg"))
            continue
        if s.startswith("```") or s.startswith("~~~"):
            in_code = not in_code
            uit.append(Regel(i, "", "leeg"))
            continue
        if in_code:
            uit.append(Regel(i, "", "leeg"))
            continue
        if "<!--" in s and "-->" not in s:
            in_comment = True
        if in_comment or (s.startswith("<!--") and s.endswith("-->")):
            if "-->" in s:
                in_comment = False
            uit.append(Regel(i, "", "leeg"))
            continue
        if re.search(r"</?[a-zA-Z][^>]*>", s):  # HTML (bijvoorbeeld in een README): alleen de tekst telt
            r = re.sub(r"<[^>]*>", " ", r)
            s = re.sub(r"\s+", " ", r).strip()
            if len(WOORD.findall(s)) < 4 or "·" in s:  # badges, navigatie, losse labels
                s = ""
        overslaan = s.startswith(("|", "[pagina ", "![")) or re.fullmatch(r"[-*_=]{3,}", s)
        if not s or overslaan:
            uit.append(Regel(i, "", "leeg"))
            continue
        schoon = re.sub(r"`[^`]*`", "code", r)
        schoon = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", schoon)
        schoon = re.sub(r"https?://\S+?(?=[.,;:!?)\]]*(?:\s|$))", "link", schoon)  # leesteken erna blijft staan
        if re.match(r"\s{0,3}>", schoon):  # blokcitaat: tekst van een ander of een voorbeeld
            uit.append(Regel(i, re.sub(r"^\s*>+\s?", "", schoon).strip(), "citaat"))
        elif re.match(r"\s{0,3}#{1,6}\s", schoon):
            uit.append(Regel(i, re.sub(r"^\s*#+\s*", "", schoon).strip(), "kop"))
        elif (uit and uit[-1].soort == "lijst" and re.match(r"(?:\s{2,}|\t)\S", schoon)
              and not re.match(r"\s*(?:[-*+•]|\d+[.)])\s+", schoon)):
            # vervolgregel van een opsommingspunt: hoort bij dat punt
            uit[-1].tekst = f"{uit[-1].tekst} {schoon.strip()}"
            uit.append(Regel(i, "", "leeg"))
        elif re.match(r"\s*(?:[-*+•]|\d+[.)])\s+", schoon):
            uit.append(Regel(i, re.sub(r"^\s*(?:[-*+•]|\d+[.)])\s+", "", schoon).strip(), "lijst"))
        else:
            uit.append(Regel(i, schoon.strip(), "proza"))
    return uit


def zinnen(tekst: str) -> list[str]:
    """Splits op . ! ? gevolgd door spatie en hoofdletter/cijfer/aanhalingsteken, behalve na afkortingen."""
    delen, start = [], 0
    for m in re.finditer(r"[.!?…]+[\"'”’)]*\s+(?=[A-ZÀ-Ö0-9\"'“‘(])", tekst):
        voor = tekst[start:m.start()]
        laatste = re.search(r"(\S+)$", voor)
        woord = (laatste.group(1).lower().rstrip(".") if laatste else "")
        if tekst[m.start()] == "." and (woord in AFKORTINGEN or re.fullmatch(r"[a-z]", woord)):
            continue
        delen.append(tekst[start:m.end()].strip())
        start = m.end()
    rest = tekst[start:].strip()
    if rest:
        delen.append(rest)
    return [d for d in delen if WOORD.search(d)]


def alineas(rs: list[Regel]) -> list[Alinea]:
    """Proza-regels die aaneensluiten vormen een alinea. Koppen en lijsten breken een alinea af."""
    uit: list[Alinea] = []
    huidig: list[Regel] = []

    def sluit():
        if huidig:
            a = Alinea(huidig[0].nr, " ".join(r.tekst for r in huidig))
            # zinnen met (benaderd) regelnummer
            for z in zinnen(a.tekst):
                nr = next((r.nr for r in huidig if z[:25] in r.tekst), huidig[0].nr)
                a.zinnen.append((nr, z))
            uit.append(a)
            huidig.clear()

    for r in rs:
        if r.soort == "proza":
            huidig.append(r)
        else:
            sluit()
    sluit()
    return uit


def woorden(tekst: str) -> list[str]:
    return WOORD.findall(tekst)


def lettergrepen(woord: str, taal: str) -> int:
    w = woord.lower()
    if taal == "nl":
        n = len(re.findall(r"[aeiouyáéíóúëïöü]+", w))
        return max(1, n)
    w = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def leeszinnen(rs: list[Regel]) -> list[str]:
    """Zinnen voor de leesbaarheid: lopende tekst plus elk opsommingspunt; koppen, code en tabellen tellen niet."""
    uit = [z for a in alineas(rs) for _, z in a.zinnen]
    for r in rs:
        if r.soort == "lijst":
            uit += zinnen(r.tekst)
    return uit


def flesch(tekst: str, taal: str, zs: list[str] | None = None) -> float | None:
    """Flesch-Douma (nl) of Flesch Reading Ease (en). Geef `zs` mee om de zinsindeling vast te leggen."""
    zs = zinnen(tekst) if zs is None else zs
    ws = [w for z in zs for w in woorden(z)] if zs else woorden(tekst)
    if len(ws) < 30 or not zs:
        return None
    lpw = sum(lettergrepen(w, taal) for w in ws) / len(ws)
    wpz = len(ws) / len(zs)
    if taal == "nl":  # Flesch-Douma
        return round(206.84 - 77 * lpw - 0.93 * wpz, 1)
    return round(206.835 - 84.6 * lpw - 1.015 * wpz, 1)  # Flesch Reading Ease


def mattr(ws: list[str], venster: int = 100) -> float | None:
    ws = [w.lower() for w in ws]
    if len(ws) < venster:
        return round(len(set(ws)) / len(ws), 3) if len(ws) >= 50 else None
    waarden = [len(set(ws[i:i + venster])) / venster for i in range(0, len(ws) - venster + 1, 10)]
    return round(statistics.mean(waarden), 3)


EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
STREEPJE = re.compile(r"\s[—–-]\s|\w—\w")


def statistiek(tekst: str, taal: str | None = None) -> dict:
    taal = taal or taal_van(tekst)
    rs = regels(tekst)
    proza = " ".join(r.tekst for r in rs if r.soort in ("proza", "lijst"))
    als = alineas(rs)
    zs = [z for a in als for _, z in a.zinnen]
    lengtes = [len(woorden(z)) for z in zs]
    ws = woorden(proza)
    n = max(len(ws), 1)
    per1000 = lambda x: round(x / n * 1000, 2)  # noqa: E731
    eerste = [woorden(z)[0].lower() for z in zs if woorden(z)]
    al_lengtes = [len(woorden(a.tekst)) for a in als]
    return {
        "taal": taal,
        "woorden": len(ws),
        "zinnen": len(zs),
        "alineas": len(als),
        "gem_zinslengte": round(statistics.mean(lengtes), 1) if lengtes else 0,
        "stdev_zinslengte": round(statistics.pstdev(lengtes), 1) if len(lengtes) > 1 else 0,
        "korte_zinnen_pct": round(100 * sum(x < 8 for x in lengtes) / len(lengtes)) if lengtes else 0,
        "lange_zinnen_pct": round(100 * sum(x > 25 for x in lengtes) / len(lengtes)) if lengtes else 0,
        "gem_alinealengte": round(statistics.mean(al_lengtes), 1) if al_lengtes else 0,
        "streepjes_per_1000": per1000(len(STREEPJE.findall(proza))),
        "dubbelepunt_per_1000": per1000(proza.count(":")),
        "puntkomma_per_1000": per1000(proza.count(";")),
        "uitroep_per_1000": per1000(proza.count("!")),
        "vraag_per_1000": per1000(proza.count("?")),
        "haakjes_per_1000": per1000(proza.count("(")),
        "emoji_per_1000": per1000(len(EMOJI.findall(tekst))),
        "mattr": mattr(ws),
        "flesch": flesch(proza, taal, leeszinnen(rs)),
        "top_zinsbegin": [w for w, _ in __import__("collections").Counter(eerste).most_common(8)],
        "je_u": {"je": sum(w.lower() in ("je", "jij", "jouw", "jou") for w in ws),
                 "u": sum(w.lower() in ("u", "uw") for w in ws)},
    }
