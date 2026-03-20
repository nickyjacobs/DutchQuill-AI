#!/usr/bin/env python3
"""
tools/humanizer_nl.py — DutchQuill AI

Detecteert AI-schrijfpatronen in Nederlandse tekst op basis van humanize_nl_gids.md.
Geeft een risicoscore (Laag / Gemiddeld / Hoog) en een gedetailleerde lijst van gevonden patronen.

Gebruik:
    python3 tools/humanizer_nl.py --input tekst.txt
    python3 tools/humanizer_nl.py --input tekst.txt --json
    python3 tools/humanizer_nl.py --compare origineel.txt herschreven.txt
    echo "Tekst hier" | python3 tools/humanizer_nl.py

Risicoscores:
    Laag      (0–2 patronen)  — kleine bijstellingen volstaan
    Gemiddeld (3–6 patronen)  — herschrijf betreffende alinea's
    Hoog      (7+ patronen)   — dringend herschrijven aanbevolen

Detectiecategorieën (20):
    1.  Niveau 1-woorden (directe AI-verraaders)
    2.  Niveau 2-dichtheid (verdacht bij hoge frequentie)
    3.  Niveau 3-dichtheid (context-afhankelijk, >3% drempel)
    4.  Formulaïsche openers (3 typen + contextuele frames)
    5.  Vullingszinnen (incl. vage toekomstsignalen)
    6.  Em dashes
    7.  Vage bronvermelding
    8.  Uniform zinsritme
    9.  Herhalende alineastarters
    10. Zinsstarter-diversiteit (binnen alinea's)
    11. Passief-dichtheid
    12. Connector-dichtheid
    13. Bijvoeglijk-naamwoordstapeling
    14. Tricolon-detectie
    15. MATTR (Moving Average Type-Token Ratio)
    16. Proportionele Niveau 1-scoring (schaalt met documentlengte)
    17. Oxford Comma detectie (komma vóór 'en' in driedelige opsomming — on-Nederlands)
    18. Anglicismen detectie (directe Engelse vertalingen die on-Nederlands klinken)
    19. Communicatievormen (chatbot/helper-taal)
    20. Alinea-lengtevariatie (structurele AI-uniformiteit)
"""

import sys
import re
import json
import argparse
import statistics
from typing import List, Tuple, Dict
from collections import Counter

# ─────────────────────────────────────────────
# WOORDENLIJSTEN (bron: humanize_nl_gids.md)
# ─────────────────────────────────────────────

NIVEAU_1 = [
    "cruciaal",
    "essentieel",
    "speelt een cruciale rol",
    "speelt een centrale rol",
    "speelt een sleutelrol",
    "naadloos",
    "synergie",
    "synergiën",
    "verdiepen in",
    "het landschap van",
    "het speelveld",
    "holistische aanpak",
    "baanbrekend",
    "grondig",
    "toonaangevend",
    "optimaliseren",
    "benutten",
    "ontsluiten",
    "biedt kansen en uitdagingen",
    "een breed scala aan",
    "in toenemende mate",
    "aanzienlijk",
    "inzichten",
    # Uitbreiding op basis van NL bronnen (aikundig.nl, frankwatching.com e.a.)
    "duiken in",
    "laten we duiken",
    "scala aan",
    "betekenisvol",
    "diepgaand",
    "transformatief",
    "katalysator",
    "speerpunt",
    "robuust",
    "faciliteert",
    "demonstreert",
    "onderstreept het belang",
    "weerspiegelt",
    "stroomlijnen",
    # Anglicismen (Categorie 7 gids) — directe Engelse vertalingen
    "fosteren",
    "testament aan",
    "impact hebben op",
]

# Morfologische varianten van Niveau 1-werkwoorden (Fase 4)
# Exacte matches missen "faciliteren", "gefaciliteerd" etc. — dit dekt die vormen
NIVEAU_1_STEMS = {
    "faciliteert":   r'\bfacilite(?:ert|ren|rende?|ring|eerde?)\b',
    "demonstreert":  r'\bdemonstree?r(?:t|en|de|d|end)\b',
    "onderstreept":  r'\bonderstreep(?:t|te|ten|en)\b',
    "weerspiegelt":  r'\bweerpiegel(?:t|de|den|en)\b|\bweerspiegelen?\b',
    "stroomlijnt":   r'\bstroomlijn(?:en|t|de|d|ing)\b',
}

NIVEAU_2 = [
    "bovendien",
    "tevens",
    "echter",
    "desalniettemin",
    "voorts",
    "derhalve",
    "aldus",
    "significant",
    "dynamisch",
    "innovatief",
    "innovatie",
    "complexiteit",
    "uitdaging",
    "in het kader van",
    "met betrekking tot",
    "ten aanzien van",
    "duidelijk",
    "evident",
    "uiteraard",
    "vanzelfsprekend",
    # Uitbreiding op basis van NL bronnen
    "genuanceerd",
    "uitgebreid",
    "proactief",
    "integraal",
    "zodoende",
    "passie",
    "verheugd",
    # Uitbreiding op basis van ChatGPT-rapporten (reviews 2026-03-20)
    "in veel gevallen",      # Rapport 3: "wordt in veel gevallen gezien als" — vage kwantificeerder
    "in sommige gevallen",   # variant — vage kwantificeerder
    "in zekere mate",        # vage kwantificeerder zonder onderbouwing
    "biedt",                 # ChatGPT-signaal (aikundig.nl): overmatig gebruik van "biedt X"
    "bieden",                # meervoudsvorm
]

# Niveau 3 — context-afhankelijk (bron: humanize_nl_gids.md Niveau 3)
# Acceptabel in kleine hoeveelheden, verdacht bij >3% dichtheid.
# "uiteraard" en "vanzelfsprekend" zitten al in NIVEAU_2 (strenger).
NIVEAU_3 = [
    "belangrijk",
    "effectief",
    "uniek",
    "waardevol",
    "opmerkelijk",
    "substantieel",
]

# ─────────────────────────────────────────────
# WHITELIST — vaktermen en eigennamen die false positives veroorzaken
# Bevat exacte substrings (case-insensitive). Als een Niveau 1-match volledig
# binnen een whitelisted uitdrukking valt, wordt de bevinding onderdrukt.
# ─────────────────────────────────────────────

WHITELIST_NIVEAU1 = [
    # Vaktermen waarin "scala" voorkomt maar niet als AI-patroon
    "scala-programmeertaal",
    "apache scala",
    # Vaktermen met "robuust"
    "robuuste optimalisatie",
    "robuuste schatting",
    # Vaktermen met "faciliteert"/"faciliteert"
    "perifaciliteert",
    # Eigennamen / merknamen die een Niveau 1-term bevatten
    "essentiële aminozuren",       # biologisch/medisch vakterm
    "essentieel tremor",           # medisch
    "cruciaal ligament",           # anatomisch
    "voorste kruisband",           # anatomisch
    "baanbrekend vonnis",          # juridisch vaste combinatie
]

# ─────────────────────────────────────────────
# SUGGESTIONS — alternatieven per Niveau 1-term
# Getoond bij --suggest flag. Bron: humanize_nl_gids.md Niveau 1-tabel.
# ─────────────────────────────────────────────

SUGGESTIONS = {
    "cruciaal": ["bepalend", "doorslaggevend", "van groot belang"],
    "essentieel": ["noodzakelijk", "onmisbaar", "vereist"],
    "speelt een cruciale rol": ["[beschrijf de specifieke functie]"],
    "speelt een centrale rol": ["[beschrijf de specifieke functie]"],
    "speelt een sleutelrol": ["[beschrijf de specifieke functie]"],
    "naadloos": ["soepel", "vlekkeloos", "[beschrijf waarom het goed werkt]"],
    "synergie": ["samenwerking", "combinatie", "wisselwerking"],
    "synergiën": ["samenwerkingsvoordelen", "combinaties"],
    "verdiepen in": ["onderzoeken", "bestuderen", "analyseren"],
    "het landschap van": ["de sector", "het veld", "[wees specifiek]"],
    "het speelveld": ["de sector", "de markt", "[wees specifiek]"],
    "holistische aanpak": ["[beschrijf wat er precies wordt meegenomen]"],
    "baanbrekend": ["nieuw", "vernieuwend", "eerste in zijn soort"],
    "grondig": ["gedetailleerd", "stap voor stap", "[beschrijf wat er grondig werd gedaan]"],
    "toonaangevend": ["vooraanstaand", "groot", "invloedrijk"],
    "optimaliseren": ["verbeteren", "efficiënter maken", "aanpassen"],
    "benutten": ["gebruiken", "inzetten", "toepassen"],
    "ontsluiten": ["openen", "beschikbaar maken", "vrijgeven"],
    "biedt kansen en uitdagingen": ["[noem de specifieke kansen en problemen]"],
    "een breed scala aan": ["veel", "diverse", "[geef concrete voorbeelden]"],
    "in toenemende mate": ["steeds meer", "[geef data of datum]"],
    "aanzienlijk": ["[geef een getal of percentage]"],
    "inzichten": ["bevindingen", "conclusies", "resultaten"],
    "duiken in": ["analyseer", "onderzoek", "bekijk nader"],
    "laten we duiken": ["we onderzoeken", "we analyseren"],
    "scala aan": ["veel", "diverse", "[geef concrete voorbeelden]"],
    "betekenisvol": ["zinvol", "nuttig", "relevant"],
    "diepgaand": ["uitgebreid", "[beschrijf ook wát er uitgebreid werd onderzocht]"],
    "transformatief": ["veranderend", "ingrijpend", "structureel anders"],
    "katalysator": ["aanjager", "trigger", "directe oorzaak"],
    "speerpunt": ["prioriteit", "focus", "hoofddoel"],
    "robuust": ["stabiel", "betrouwbaar", "[beschrijf waarom]"],
    "faciliteert": ["maakt mogelijk", "helpt", "zorgt voor"],
    "demonstreert": ["laat zien", "toont", "bewijst"],
    "onderstreept het belang": ["bevestigt", "toont aan", "maakt duidelijk"],
    "weerspiegelt": ["toont", "is te zien in", "volgt uit"],
    "stroomlijnen": ["vereenvoudigen", "efficiënter maken", "samenvoegen"],
    "fosteren": ["bevorderen", "stimuleren", "aanmoedigen"],
    "testament aan": ["bewijs van", "aanwijzing voor"],
    "impact hebben op": ["invloed hebben op", "effect hebben op", "gevolgen hebben voor"],
}

# ─────────────────────────────────────────────
# ANGLICISMS — directe Engelse vertalingen (Categorie 7 gids)
# Worden apart gescoord als categorie 18.
# ─────────────────────────────────────────────

ANGLICISMS = [
    "duiken in",
    "laten we duiken",
    "het landschap van",
    "fosteren",
    "stakeholders",
    "impact hebben op",
    "testament aan",
    "het speelveld",
    "synergie creëren",
]

# Communicatievormen — helper/chatbot-taal (Fase 6, Categorie 19)
COMMUNICATIEVORMEN_PATTERNS = [
    r'\bu\s+kunt\s+zien\s+dat\b',
    r'\bzoals\s+u\s+wellicht\s+weet\b',
    r'\bik\s+hoop\s+dat\s+(?:dit|u)\b',
    r'\blaat\s+(?:me|mij)\s+(?:u\s+)?(?:uitleggen|weten)\b',
    r'\bvoel\s+je\s+vrij\s+om\b',
    r'\bals\s+taalmodel\b',
    r'\bop\s+basis\s+van\s+mijn\s+training\b',
    r'\bhet\s+is\s+(?:opvallend|interessant)\s+om\s+(?:op\s+te\s+merken|te\s+zien)\b',
    r'\bdit\s+is\s+een\s+interessante\s+bevinding\b',
]

# ─────────────────────────────────────────────
# Formulaïsche openers — Type 1 (brede aanloop)
TYPE_1_OPENERS = [
    r"in de huidige samenleving",
    r"tegenwoordig is het duidelijk dat",
    r"in de afgelopen jaren is er veel veranderd",
    r"het onderwerp van dit rapport is actueler dan ooit",
    r"in een wereld waar",
    r"in het huidige tijdperk",
    r"het is belangrijker dan ooit",
    # Uitbreiding: ChatGPT-openers gevonden in reviews 2026-03-20
    r"in de hedendaagse maatschappij",          # Rapport 3 exact
    r"in een steeds veranderende (?:wereld|samenleving|context)",
    r"in deze tijd van \w+",
]

# Type 2 (aankondiging van wat je gaat doen)
TYPE_2_OPENERS = [
    r"in dit rapport wordt onderzocht",
    r"dit rapport richt zich op",
    r"het doel van dit rapport is",
    r"in dit hoofdstuk zal ik bespreken",
    r"hieronder volgt een overzicht van",
    r"allereerst wordt ingegaan op",
    r"in wat volgt wordt",
    r"in het navolgende",
]

# Type 2b — Contextuele frames (NIEUW: vage achtergrondstellingen zonder agent/bron)
# Rapport 3 patronen: "Tegen deze achtergrond...", "Vanuit een algemeen perspectief..."
TYPE_2B_OPENERS = [
    r"tegen deze achtergrond",
    r"vanuit een \w+ perspectief",
    r"in brede zin (?:kan worden gesteld|wordt|is)",
    r"in het algemeen (?:kan worden gesteld|geldt|wordt)",
    r"in algemene (?:zin|termen) (?:kan worden|wordt)",
]

# Type 3 (samenvatting van wat je net hebt gezegd)
TYPE_3_OPENERS = [
    r"kortom[,\s]+het is duidelijk dat",
    r"al met al kan gesteld worden dat",
    r"zoals eerder vermeld",
    r"op basis van het voorgaande kan geconcludeerd worden dat",
    r"bovenstaande analyse toont aan dat",
    r"aan de hand van het bovenstaande",
    # Uitbreiding: ChatGPT-conclusiepatronen gevonden in reviews 2026-03-20
    r"samenvattend kan worden gesteld dat",      # Rapport 3 conclusie exact
    r"vanuit een algemeen perspectief (?:lijkt|is|kan)",
    r"het mag duidelijk zijn dat",
    r"op basis van (?:de geraadpleegde bronnen|de literatuur|het bovenstaande) kan \w*\s*worden (?:gesteld|geconcludeerd)",
]

# Vullingszinnen (exacte patronen uit gids)
FILLER_PATTERNS = [
    r"dit is een relevant onderwerp",
    r"er is veel geschreven over dit thema",
    r"het spreekt voor zich dat",
    r"uiteraard is dit slechts één van de mogelijke perspectieven",
    r"vanzelfsprekend zijn er ook andere invalshoeken mogelijk",
    r"dit rapport tracht een bijdrage te leveren aan",
    r"een goede definitie is hier op zijn plaats",
    r"alvorens verder te gaan[,\s]+is het nuttig om",
    r"het is interessant om op te merken dat",
    r"het is belangrijk om te benadrukken dat",
    r"er dient rekening mee gehouden te worden dat",
    r"zoals eerder vermeld",
    r"zoals al aangegeven",
    # Generieke conclusies (NL-equivalent van "the future looks bright")
    r"de toekomst ziet er rooskleurig uit",
    r"de mogelijkheden zijn eindeloos",
    r"naar een hoger niveau tillen",
    r"er liggen grote kansen",
    r"dit is slechts het begin",
    r"dit vraagt om verdere aandacht",
    # Uitbreiding: extra Nederlandse AI-fillers
    r"het is van belang dat",
    r"dit draagt bij aan",
    r"hierbij dient opgemerkt te worden dat",
    r"het kan geconcludeerd worden dat",
    r"zo kan gesteld worden dat",
    r"het verdient aanbeveling om",
    r"in dit verband is het relevant om",
    # Vage toekomstsignalen zonder onderbouwing (Rapport 3: "naar verwachting relevant zal blijven")
    r"naar verwachting (?:zal|blijft|worden)",
    r"in de toekomst naar verwachting",
    r"zal in de toekomst \w+ blijven",
    r"naar verwachting relevant",
]

# Vage bronvermelding — AI-patroon én APA-overtreding
VAGUE_ATTRIBUTION_PATTERNS = [
    r"uit onderzoek blijkt dat",
    r"experts stellen dat",
    r"studies tonen aan dat",
    r"het is algemeen bekend dat",
    r"wetenschappers zijn het erover eens dat",
    r"onderzoek wijst uit dat",
    r"uit de literatuur blijkt dat",
    r"zoals bekend is",
    # Uitbreiding: semantische varianten gevonden in Rapport 1 (thuiswerken)
    r"eerdere studies laten zien dat",           # Rapport 1 exact: niet gedetecteerd
    r"in de literatuur wordt (?:gesteld|beschreven|aangegeven|beargumenteerd)",
    r"studies (?:laten|laat) zien dat",          # variant van "studies tonen aan"
    r"onderzoeken tonen aan dat",                # variant van "studies tonen aan"
    r"er is (?:aangetoond|bewezen) dat",         # claim zonder citatie
    r"men (?:stelt|weet|zegt) dat",              # vage actor ("men")
    r"het is (?:aangetoond|bewezen) dat",        # variant zonder bron
    r"eerder onderzoek (?:toont|laat) (?:zien|aan) dat",
    r"uit (?:diverse|verschillende|meerdere) studies blijkt",
]

# Passief-constructie patronen (Nederlands)
PASSIVE_PATTERNS = [
    r'\bwordt\s+\w+d\b',
    r'\bworden\s+\w+d\b',
    r'\bwerden?\s+\w+d\b',
    r'\bis\s+\w+d\b',
    r'\bzijn\s+\w+d\b',
    r'\bkan\s+worden\b',
    r'\bkunnen\s+worden\b',
    r'\bdient\s+.*?te\s+worden\b',
    r'\ber\s+wordt\b',
    r'\ber\s+werd\b',
    r'\ber\s+kan\b',
    r'\ber\s+zijn\b',
]

# Connectors die AI als zinsopener overgebruikt
CONNECTORS = [
    "bovendien", "tevens", "daarnaast", "echter", "desalniettemin",
    "voorts", "derhalve", "aldus", "verder", "daarentegen",
    "niettemin", "evenwel", "immers", "namelijk", "daarom",
    "zodoende", "hierdoor", "hierbij", "daarenboven",
]


# ─────────────────────────────────────────────
# HULPFUNCTIES
# ─────────────────────────────────────────────

def _is_likely_citation(text: str, match_start: int, match_end: int) -> bool:
    """
    Controleer of een match waarschijnlijk deel is van een directe citatie (blokcitaat).
    Onderdrukt alleen matches die LETTERLIJK binnen aanhalingstekens staan,
    zodat direct geciteerde tekst van anderen niet als AI-patroon wordt gemeld.
    De auteur's eigen parafrasen (ook met citatie) worden wel gemeld.
    """
    # Zoek aanhalingstekens rondom de match
    # Controleer of de match tussen dubbele of enkele aanhalingstekens valt
    # door te kijken naar de omringende tekst (max 200 chars context)
    search_start = max(0, match_start - 200)
    search_end = min(len(text), match_end + 200)
    before = text[search_start:match_start]
    after = text[match_end:search_end]

    # Tel aanhalingstekens voor en na de match
    # Als er een oneven aantal aanhalingstekens voor de match staat, zit de match in een quote
    double_before = before.count('"')
    double_after = after.count('"')
    if double_before % 2 == 1 and double_after % 2 == 1:
        return True

    single_before = before.count("'")
    single_after = after.count("'")
    if single_before % 2 == 1 and single_after % 2 == 1:
        return True

    return False


def split_sentences(text: str) -> List[str]:
    """Splits tekst in zinnen op punt, uitroep- of vraagteken."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def split_paragraphs(text: str) -> List[str]:
    """Splits tekst in alinea's op lege regels."""
    paragraphs = re.split(r'\n\s*\n', text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


def count_words(text: str) -> int:
    return len(text.split())


# ─────────────────────────────────────────────
# CHECKS
# ─────────────────────────────────────────────

def find_niveau1(text: str) -> List[Tuple[str, str]]:
    """Zoek Niveau 1-woorden. Geeft lijst van (gevonden_term, context).
    Matches die binnen een whitelisted vakterm of eigennaam vallen worden onderdrukt."""
    text_lower = text.lower()
    findings = []
    # Sorteer op lengte aflopend zodat langere phrases eerst matchen
    sorted_terms = sorted(NIVEAU_1, key=len, reverse=True)
    matched_ranges = []

    for term in sorted_terms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        for match in pattern.finditer(text_lower):
            # Voorkom dubbele meldingen voor overlappende matches
            overlap = any(s <= match.start() < e for s, e in matched_ranges)
            if overlap:
                continue
            # Whitelist-check: onderdruk als de match deel is van een bekende vakterm
            context_window = text_lower[max(0, match.start() - 30):match.end() + 30]
            if any(w in context_window for w in WHITELIST_NIVEAU1):
                continue
            # Citatie-check: onderdruk als de match waarschijnlijk in geciteerde tekst staat
            if _is_likely_citation(text, match.start(), match.end()):
                continue
            matched_ranges.append((match.start(), match.end()))
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 40)
            context = "..." + text[start:end].replace('\n', ' ') + "..."
            findings.append((term, context))

    # Morfologische werkwoordvarianten (NIVEAU_1_STEMS)
    for label, pattern in NIVEAU_1_STEMS.items():
        compiled = re.compile(pattern, re.IGNORECASE)
        for match in compiled.finditer(text_lower):
            overlap = any(s <= match.start() < e for s, e in matched_ranges)
            if overlap:
                continue
            context_window = text_lower[max(0, match.start() - 30):match.end() + 30]
            if any(w in context_window for w in WHITELIST_NIVEAU1):
                continue
            if _is_likely_citation(text, match.start(), match.end()):
                continue
            matched_ranges.append((match.start(), match.end()))
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 40)
            context = "..." + text[start:end].replace('\n', ' ') + "..."
            findings.append((label, context))

    return findings


def find_niveau2_density(text: str) -> List[Tuple[str, float, int]]:
    """
    Controleer Niveau 2-dichtheid.
    Geeft lijst van (woord, voorkomens_per_500w, totaal) voor woorden boven drempel.
    """
    word_count = count_words(text)
    findings = []

    for term in NIVEAU_2:
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        count = len(pattern.findall(text))
        if word_count > 0 and count > 0:
            per_500 = (count / word_count) * 500
            if per_500 > 1.0:
                findings.append((term, round(per_500, 1), count))

    return findings


def find_niveau3_density(text: str) -> List[Tuple[str, float, int]]:
    """
    Controleer Niveau 3-dichtheid.
    Geeft lijst van (woord, percentage_van_tekst, totaal) voor woorden boven 3% drempel.
    Niveau 3-woorden zijn acceptabel in kleine hoeveelheden maar verdacht bij hoge dichtheid.
    """
    words = text.lower().split()
    word_count = len(words)
    if word_count < 50:
        return []
    findings = []
    for term in NIVEAU_3:
        pattern = re.compile(r'\b' + re.escape(term) + r'\b', re.IGNORECASE)
        count = len(pattern.findall(text))
        if count > 0:
            percentage = (count / word_count) * 100
            if percentage > 3.0:
                findings.append((term, round(percentage, 1), count))
    return findings


def find_formulaic_openers(text: str) -> List[Tuple[str, str, str]]:
    """Zoek formulaïsche openers. Geeft lijst van (type, patroon, context)."""
    findings = []
    checks = [
        ("Type 1 (brede aanloop)", TYPE_1_OPENERS),
        ("Type 2 (aankondiging)", TYPE_2_OPENERS),
        ("Type 2b (contextueel frame)", TYPE_2B_OPENERS),
        ("Type 3 (herhaling/samenvatting)", TYPE_3_OPENERS),
    ]
    for opener_type, patterns in checks:
        for pat in patterns:
            compiled = re.compile(pat, re.IGNORECASE)
            for match in compiled.finditer(text):
                start = max(0, match.start() - 5)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')
                findings.append((opener_type, pat, context))

    return findings


def find_fillers(text: str) -> List[Tuple[str, str]]:
    """Zoek vullingszinnen. Geeft lijst van (patroon, context)."""
    findings = []
    for pat in FILLER_PATTERNS:
        compiled = re.compile(pat, re.IGNORECASE)
        for match in compiled.finditer(text):
            start = max(0, match.start() - 5)
            end = min(len(text), match.end() + 50)
            context = text[start:end].replace('\n', ' ')
            findings.append((pat, context))

    return findings


def check_sentence_rhythm(text: str) -> List[str]:
    """
    Controleer op uniform zinsritme.
    Vijf of meer opeenvolgende zinnen binnen 30% van elkaar in woordlengte.
    """
    sentences = split_sentences(text)
    findings = []

    if len(sentences) < 5:
        return findings

    window = 5
    reported = set()

    for i in range(len(sentences) - window + 1):
        chunk = sentences[i:i + window]
        lengths = [len(s.split()) for s in chunk]

        if all(l >= 5 for l in lengths):  # Alleen substantiële zinnen
            avg = sum(lengths) / len(lengths)
            if avg > 0 and all(abs(l - avg) / avg <= 0.30 for l in lengths):
                key = i
                if key not in reported:
                    reported.add(key)
                    snippet = chunk[0][:60] + ("..." if len(chunk[0]) > 60 else "")
                    findings.append(
                        f"{window} opeenvolgende zinnen vergelijkbare lengte "
                        f"(~{int(avg)} woorden): \"{snippet}\""
                    )

    # Globale CV-check: lage variatie over hele tekst (Fase 3)
    if len(sentences) >= 10:
        all_lengths = [len(s.split()) for s in sentences if len(s.split()) >= 4]
        if len(all_lengths) >= 10:
            mean = statistics.mean(all_lengths)
            stdev = statistics.stdev(all_lengths)
            cv = stdev / mean if mean > 0 else 1.0
            if cv < 0.30:
                findings.append(
                    f"Lage zinslengtevariatie over hele tekst "
                    f"(CV={cv:.2f}, norm >0.40) — uniform AI-ritme"
                )

    return findings[:2]  # Max 2 meldingen om output beheersbaar te houden


def check_paragraph_starters(text: str) -> List[str]:
    """Controleer of alinea's telkens met hetzelfde woord beginnen."""
    paragraphs = split_paragraphs(text)
    findings = []

    if len(paragraphs) < 3:
        return findings

    starters = []
    for p in paragraphs:
        words = p.split()
        if words:
            starters.append(words[0].lower().rstrip('.,;:'))

    # Woorden die 3+ keer voorkomen als starter
    starter_counts = Counter(starters)
    for word, count in starter_counts.items():
        if count >= 3 and len(word) > 3:
            findings.append(f"Alinea begint {count}x met \"{word}\"")

    # Drie opeenvolgende alinea's met hetzelfde starterwoord
    for i in range(len(starters) - 2):
        if starters[i] == starters[i + 1] == starters[i + 2] and len(starters[i]) > 3:
            msg = f"Drie opeenvolgende alinea's beginnen met \"{starters[i]}\""
            if msg not in findings:
                findings.append(msg)
            break

    return list(dict.fromkeys(findings))


def check_sentence_starters(text: str) -> List[str]:
    """
    Controleer of zinnen binnen alinea's te vaak met hetzelfde woord beginnen.
    Signaleert als 3+ opeenvolgende zinnen met hetzelfde woord starten.
    """
    paragraphs = split_paragraphs(text)
    findings = []

    for p_idx, para in enumerate(paragraphs):
        sentences = split_sentences(para)
        if len(sentences) < 3:
            continue
        starters = []
        for s in sentences:
            words = s.split()
            if words:
                starters.append(words[0].lower().rstrip('.,;:'))

        # 3+ opeenvolgende zinnen met hetzelfde starterwoord
        for i in range(len(starters) - 2):
            if (starters[i] == starters[i + 1] == starters[i + 2]
                    and len(starters[i]) > 2):
                findings.append(
                    f"Alinea {p_idx + 1}: 3 opeenvolgende zinnen beginnen "
                    f"met \"{starters[i]}\""
                )
                break  # Eén melding per alinea

        # "Daarnaast" specifiek: 4+ keer als zinsopener in hele tekst
        if p_idx == 0:  # Alleen bij eerste alinea de hele tekst checken
            all_sentences = split_sentences(text)
            daarnaast_count = sum(
                1 for s in all_sentences
                if s.strip().lower().startswith('daarnaast')
            )
            if daarnaast_count >= 4:
                findings.append(
                    f"\"Daarnaast\" wordt {daarnaast_count}x als zinsopener "
                    f"gebruikt (typisch AI-patroon)"
                )

    return findings[:3]  # Max 3 meldingen


def find_em_dashes(text: str) -> List[Tuple[str, str]]:
    """
    Detecteer em dashes (—) in de tekst.
    Em dashes zijn een Engels leesteken en een directe AI-indicator in Nederlandse tekst.
    """
    findings = []
    for match in re.finditer(r'—', text):
        start = max(0, match.start() - 30)
        end = min(len(text), match.end() + 30)
        context = "..." + text[start:end].replace('\n', ' ') + "..."
        findings.append(("—", context))
    return findings


def find_vague_attribution(text: str) -> List[Tuple[str, str]]:
    """
    Detecteer vage bronvermelding zonder citatie.
    Is zowel een AI-patroon als een APA-overtreding.
    """
    findings = []
    for pat in VAGUE_ATTRIBUTION_PATTERNS:
        compiled = re.compile(pat, re.IGNORECASE)
        for match in compiled.finditer(text):
            start = max(0, match.start() - 5)
            end = min(len(text), match.end() + 60)
            context = text[start:end].replace('\n', ' ')
            findings.append((pat, context))
    return findings


def find_oxford_comma(text: str) -> List[str]:
    """
    Detecteer Oxford comma patroon: "X, Y, en Z" (komma direct vóór 'en').
    In het Nederlands is de komma vóór 'en' in driedelige opsommingen on-gebruikelijk
    en een directe AI-indicator door Engelse training.
    Categorie 17 — bron: humanize_nl_gids.md Categorie 8.
    """
    # Match: woord, woord, en woord (komma voor 'en')
    pattern = re.compile(
        r'\b(\w{2,})\s*,\s*(\w{2,})\s*,\s+en\s+(\w{2,})\b',
        re.IGNORECASE
    )
    findings = []
    for match in pattern.finditer(text):
        # Onderdruk als dit waarschijnlijk een citatie is
        if _is_likely_citation(text, match.start(), match.end()):
            continue
        snippet = match.group(0)
        findings.append(f"Oxford comma: \"{snippet}\" → schrijf zonder komma vóór 'en'")
    return findings


def find_anglicisms(text: str) -> List[Tuple[str, str]]:
    """
    Detecteer directe Engelse vertalingen die on-Nederlands klinken.
    Categorie 18 — bron: humanize_nl_gids.md Categorie 7.
    """
    text_lower = text.lower()
    findings = []
    # Sorteer op lengte zodat langere phrases eerst matchen
    sorted_anglicisms = sorted(ANGLICISMS, key=len, reverse=True)
    matched_ranges = []

    for term in sorted_anglicisms:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        for match in pattern.finditer(text_lower):
            overlap = any(s <= match.start() < e for s, e in matched_ranges)
            if overlap:
                continue
            if _is_likely_citation(text, match.start(), match.end()):
                continue
            matched_ranges.append((match.start(), match.end()))
            start = max(0, match.start() - 40)
            end = min(len(text), match.end() + 40)
            context = "..." + text[start:end].replace('\n', ' ') + "..."
            findings.append((term, context))

    return findings


def find_communicatievormen(text: str) -> List[str]:
    """
    Detecteer chatbot/helper-taalpatronen (Categorie 19).
    Patronen die AI's gebruiken om als assistent te communiceren.
    """
    findings = []
    for pattern in COMMUNICATIEVORMEN_PATTERNS:
        compiled = re.compile(pattern, re.IGNORECASE)
        for match in compiled.finditer(text):
            if _is_likely_citation(text, match.start(), match.end()):
                continue
            start = max(0, match.start() - 20)
            end = min(len(text), match.end() + 60)
            context = "..." + text[start:end].replace('\n', ' ') + "..."
            findings.append(context)
    return findings


def check_passive_density(text: str) -> Tuple[float, bool, int]:
    """
    Bereken percentage zinnen met passieve constructies.
    AI genereert overmatig passief in het Nederlands.
    Geeft (percentage, is_hoog, aantal_passief).
    Waarschuwt bij > 40% passieve zinnen.
    """
    sentences = split_sentences(text)
    if len(sentences) < 5:
        return 0.0, False, 0
    passive_count = 0
    for s in sentences:
        for pat in PASSIVE_PATTERNS:
            if re.search(pat, s, re.IGNORECASE):
                passive_count += 1
                break  # Tel elke zin maximaal één keer
    pct = (passive_count / len(sentences)) * 100
    return round(pct, 1), pct > 40, passive_count


def check_connector_density(text: str) -> Tuple[float, bool]:
    """
    Bereken welk percentage zinnen met een connector begint.
    AI overgebruikt connectors als zinsopener.
    Waarschuwt bij > 30%.
    """
    sentences = split_sentences(text)
    if len(sentences) < 5:
        return 0.0, False
    connector_starts = 0
    for s in sentences:
        words = s.split()
        if words:
            first_word = words[0].lower().rstrip('.,;:')
            if first_word in CONNECTORS:
                connector_starts += 1
    pct = (connector_starts / len(sentences)) * 100
    return round(pct, 1), pct > 30


def find_adjective_stacking(text: str) -> List[str]:
    """
    Detecteer 3+ bijvoeglijke naamwoorden voor een zelfstandig naamwoord.
    AI stapelt vaak meerdere bijvoeglijke naamwoorden: "een innovatief, baanbrekend en
    transformatief project".
    """
    # Match: "een/de/het WOORD, WOORD en WOORD WOORD" of "WOORD, WOORD, WOORD en WOORD WOORD"
    pattern = re.compile(
        r'\b(?:een|de|het)\s+'
        r'(\w+\w*\s*,\s*\w+\w*\s+en\s+\w+\w*\s+\w+)',
        re.IGNORECASE
    )
    findings = []
    for match in pattern.finditer(text):
        start = max(0, match.start() - 5)
        end = min(len(text), match.end() + 10)
        context = text[start:end].replace('\n', ' ').strip()
        findings.append(f"Bijvoeglijk-naamwoordstapeling: \"{context}\"")
    return findings[:3]


def check_tricolons(text: str) -> Tuple[int, bool]:
    """
    Tel driedelige opsommingen (X, Y en Z).
    AI gebruikt overmatig driedelige lijsten over meerdere alinea's.
    Alarmerend als 5+ tricolons in de tekst voorkomen (algemeen),
    of als een tricolon bestaat uit 3 Niveau 1/2-woorden (altijd AI-indicator).
    """
    # Match: "woord, woord en woord" (minimaal 3 tekens per onderdeel)
    pattern = re.compile(r'\b(\w{3,})\s*,\s*(\w{3,})\s+en\s+(\w{3,})\b', re.IGNORECASE)
    matches = pattern.findall(text)
    count = len(matches)

    # Controleer ook op tricolons van AI-buzzwords (altijd flaggen, ook bij 1 occurrence)
    niveau1_set = set(NIVEAU_1)
    niveau2_set = set(NIVEAU_2)
    buzz_tricolon_found = False
    for m in matches:
        items = [w.lower() for w in m]
        if sum(1 for w in items if w in niveau1_set or w in niveau2_set) >= 2:
            buzz_tricolon_found = True
            break

    is_hoog = count >= 5 or buzz_tricolon_found
    return count, is_hoog


def check_ttr(text: str) -> Tuple[float, bool]:
    """
    Bereken MATTR (Moving Average Type-Token Ratio) met een venster van 50 woorden.
    Betrouwbaarder dan standaard TTR voor teksten van wisselende lengte.
    Menselijk schrijven: 0.65–0.80  |  AI-schrijven: 0.50–0.65
    Geeft (mattr_score, is_laag). Waarschuwt bij MATTR < 0.60.
    """
    words = re.findall(r'\b[a-zA-ZàáâãäåæçèéêëìíîïòóôõöùúûüÀ-ÿ]+\b', text.lower())
    if len(words) < 50:
        # Fallback naar standaard TTR bij korte teksten
        if len(words) < 20:
            return 0.0, False
        ttr = len(set(words)) / len(words)
        return round(ttr, 3), ttr < 0.45

    window = 50
    ttrs = []
    for i in range(len(words) - window + 1):
        window_words = words[i:i + window]
        ttr = len(set(window_words)) / window
        ttrs.append(ttr)

    mattr = sum(ttrs) / len(ttrs)
    return round(mattr, 3), mattr < 0.60


# Nederlandse klinkergroepen (hergebruikt van readability_nl.py) voor lettergreeptelling
_NL_VOWEL_PATTERN = re.compile(
    r'ui|eu|au|ou|ei|ij|oe|aa|ee|oo|uu|ie'
    r'|[aeiouáéíóúàèìòùäëïöü]',
    re.IGNORECASE
)
_ABBREV_PATTERN = re.compile(
    r'\b(?:dr|drs|mr|ir|prof|ing|dhr|mw|jr|sr|ca|bijv|resp|etc|vs|nr|'
    r'art|par|p|pp|red|reds|ed|eds|vol|fig|tab)\.',
    re.IGNORECASE
)


def _flesch_douma_score(text: str) -> Tuple[float, bool]:
    """
    Berekent Flesch-Douma score intern (hergebruik van readability_nl.py logica).
    Retourneert (score, flesch_laag) waarbij flesch_laag = score < 30.
    Score < 30 bij HBO-tekst is een sterk AI-signaal (ChatGPT schrijft te formeel).
    """
    text_clean = re.sub(r'https?://\S+', 'URL', text)
    text_clean = _ABBREV_PATTERN.sub(lambda m: m.group(0).replace('.', '\x00'), text_clean)
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z\u201c\u201e"\d])', text_clean)
    sentences = [s.replace('\x00', '.').strip() for s in raw_sentences
                 if s.strip() and len(s.split()) >= 2]

    words = [w for w in re.findall(r'\b[a-zA-Záéíóúàèìòùäëïöü]+\b', text) if len(w) >= 2]

    n_sentences = max(len(sentences), 1)
    n_words = max(len(words), 1)
    n_syllables = sum(
        max(1, len(_NL_VOWEL_PATTERN.findall(re.sub(r'[^a-zA-Záéíóúàèìòùäëïöü]', '', w))))
        for w in words
    )

    asl = n_words / n_sentences
    asw = n_syllables / n_words
    raw = 206.835 - (0.93 * asl) - (77 * asw)
    score = round(max(0.0, min(100.0, raw)), 1)
    return score, score < 30


def check_alinea_variatie(text: str) -> List[str]:
    """
    Categorie 20 — Alinea-lengtevariatie.
    ChatGPT genereert alinea's van opvallend gelijke lengte (uniforme structuur).
    Menselijk schrijven heeft meer variatie in alinealengte.
    Waarschuwt als de variatiecoëfficiënt (CV) van alinealengte < 0.25 over ≥ 4 alinea's.
    Bron: b2bmarketeers.nl, aikundig.nl (structurele AI-uniformiteit).
    """
    paragraphs = split_paragraphs(text)
    # Filter: alleen alinea's van meer dan 20 tekens (geen koppen/labels)
    substantive = [p for p in paragraphs if len(p.strip()) > 30]
    if len(substantive) < 4:
        return []
    lengths = [len(p.split()) for p in substantive]
    mean = sum(lengths) / len(lengths)
    if mean < 5:
        return []
    stdev = statistics.stdev(lengths)
    cv = stdev / mean
    if cv < 0.25:
        return [
            f"Alinea-lengtevariatie laag (CV={cv:.2f}, norm >0.25) — "
            f"{len(substantive)} alinea's van gemiddeld {int(mean)} woorden met weinig onderlinge variatie"
        ]
    return []


def calculate_score(
    niveau1: list, niveau2: list, niveau3: list, openers: list,
    fillers: list, rhythm: list, para_starters: list,
    sent_starters: list = None,
    em_dashes: list = None, vague_attr: list = None,
    passive_hoog: bool = False, connector_hoog: bool = False,
    adj_stacking: list = None, tricolon_hoog: bool = False,
    ttr_laag: bool = False, word_count: int = 500,
    oxford_comma: list = None, anglicisms: list = None,
    flesch_laag: bool = False,
    passive_pct: float = 0.0, connector_pct: float = 0.0,
    communicatievormen: list = None,
    alinea_variatie: list = None,
) -> Tuple[int, str]:
    """Berekent risicoscore. Geeft (score, label).
    Niveau 1-scoring schaalt proportioneel met documentlengte."""
    patterns = 0

    # Niveau 1: proportionele cap op basis van documentlengte
    if niveau1:
        cap = 3 + max(0, (word_count - 1000) // 500)
        patterns += min(len(niveau1), cap)
    # Niveau 2: volledige telling
    if niveau2:
        patterns += len(niveau2)
    # Niveau 3: 1 punt als er bevindingen zijn
    if niveau3:
        patterns += 1
    if openers:
        patterns += len(openers)
    if fillers:
        patterns += min(len(fillers), 2)
    # Fase 3: rhythm-scoring: lokale runs = 1 pt, globale CV = extra 1 pt
    local_rhythm = [f for f in (rhythm or []) if "Lage zinslengtevariatie" not in f]
    global_cv = [f for f in (rhythm or []) if "Lage zinslengtevariatie" in f]
    if local_rhythm:
        patterns += 1
    if global_cv:
        patterns += 1
    if para_starters:
        patterns += 1
    if sent_starters:
        patterns += 1
    if em_dashes:
        patterns += min(len(em_dashes), 2)
    if vague_attr:
        patterns += min(len(vague_attr), 2)
    # Fase 5: gradient scoring passief
    if passive_pct >= 60:
        patterns += 2
    elif passive_pct >= 40 or passive_hoog:
        patterns += 1
    # Fase 5: gradient scoring connector
    if connector_pct >= 50:
        patterns += 2
    elif connector_pct >= 30 or connector_hoog:
        patterns += 1
    if adj_stacking:
        patterns += 1
    if tricolon_hoog:
        patterns += 1
    if ttr_laag:
        patterns += 1
    # Fase 1b: Oxford comma drempel verlaagd naar 2+
    if oxford_comma and len(oxford_comma) >= 2:
        patterns += 1
    elif oxford_comma and len(oxford_comma) == 1:
        patterns += 0  # Meld maar telt niet mee (kan citaat zijn)
    # Anglicisms: elk uniek anglicisme telt als Niveau 1 (proportioneel afgetopt)
    if anglicisms:
        unique_anglicisms = len(set(t for t, _ in anglicisms)) if isinstance(anglicisms[0], tuple) else len(anglicisms)
        patterns += min(unique_anglicisms, 2)
    # Fase 2: Flesch-Douma < 30 = sterk AI-signaal (+2 pts)
    if flesch_laag:
        patterns += 2
    # Fase 6: communicatievormen
    if communicatievormen:
        patterns += min(len(communicatievormen), 2)
    # Categorie 20: alinea-lengtevariatie
    if alinea_variatie:
        patterns += 1

    # Drempels: Laag ≤ 2, Gemiddeld ≤ 6, Hoog 7+
    # (verhoogd van 5→6/6→7 na uitbreiding detectiecategorieën 2026-03-20)
    if patterns <= 2:
        return patterns, "Laag"
    elif patterns <= 6:
        return patterns, "Gemiddeld"
    else:
        return patterns, "Hoog"


def analyze(text: str) -> Dict:
    """Voer volledige analyse uit op tekst."""
    word_count = count_words(text)
    niveau1 = find_niveau1(text)
    niveau2 = find_niveau2_density(text)
    niveau3 = find_niveau3_density(text)
    openers = find_formulaic_openers(text)
    fillers = find_fillers(text)
    rhythm = check_sentence_rhythm(text)
    para_starters = check_paragraph_starters(text)
    sent_starters = check_sentence_starters(text)
    em_dashes = find_em_dashes(text)
    vague_attr = find_vague_attribution(text)
    passive_pct, passive_hoog, passive_count = check_passive_density(text)
    connector_pct, connector_hoog = check_connector_density(text)
    adj_stacking = find_adjective_stacking(text)
    tricolon_count, tricolon_hoog = check_tricolons(text)
    ttr, ttr_laag = check_ttr(text)
    oxford_comma = find_oxford_comma(text)
    anglicisms_found = find_anglicisms(text)
    flesch, flesch_laag = _flesch_douma_score(text)
    communicatievormen = find_communicatievormen(text)
    alinea_variatie = check_alinea_variatie(text)

    score, label = calculate_score(
        niveau1, niveau2, niveau3, openers, fillers, rhythm, para_starters,
        sent_starters, em_dashes, vague_attr,
        passive_hoog, connector_hoog, adj_stacking, tricolon_hoog,
        ttr_laag, word_count,
        oxford_comma=oxford_comma,
        anglicisms=anglicisms_found,
        flesch_laag=flesch_laag,
        passive_pct=passive_pct,
        connector_pct=connector_pct,
        communicatievormen=communicatievormen,
        alinea_variatie=alinea_variatie,
    )

    # Suggesties koppelen aan gevonden Niveau 1-termen (voor --suggest flag en JSON)
    niveau1_with_suggestions = []
    for term, context in niveau1:
        suggestions = SUGGESTIONS.get(term.lower(), [])
        niveau1_with_suggestions.append({
            "term": term,
            "context": context,
            "suggestions": suggestions,
        })

    return {
        "woorden": word_count,
        "zinnen": len(split_sentences(text)),
        "niveau1": niveau1_with_suggestions,
        "niveau2": [{"term": t, "per_500w": p, "totaal": n} for t, p, n in niveau2],
        "niveau3": [{"term": t, "percentage": p, "totaal": n} for t, p, n in niveau3],
        "openers": [{"type": ot, "context": c} for ot, _, c in openers],
        "fillers": [{"context": c} for _, c in fillers],
        "rhythm": rhythm,
        "para_starters": para_starters,
        "sent_starters": sent_starters,
        "em_dashes": [{"context": c} for _, c in em_dashes],
        "vague_attr": [{"context": c} for _, c in vague_attr],
        "passive_pct": passive_pct,
        "passive_hoog": passive_hoog,
        "passive_count": passive_count,
        "connector_pct": connector_pct,
        "connector_hoog": connector_hoog,
        "adj_stacking": adj_stacking,
        "tricolon_count": tricolon_count,
        "tricolon_hoog": tricolon_hoog,
        "ttr": ttr,
        "ttr_laag": ttr_laag,
        "oxford_comma": oxford_comma,
        "anglicisms": [{"term": t, "context": c} for t, c in anglicisms_found],
        "flesch": flesch,
        "flesch_laag": flesch_laag,
        "communicatievormen": communicatievormen,
        "alinea_variatie": alinea_variatie,
        "score": score,
        "risico": label,
    }


# ─────────────────────────────────────────────
# OUTPUT
# ─────────────────────────────────────────────

def print_report(result: Dict, label: str = "Analyse", suggest: bool = False) -> None:
    """Print een leesbaar rapport naar stdout.
    suggest=True: toon alternatieven voor Niveau 1-woorden."""
    r = result
    lijn = "═" * 60
    lijn2 = "─" * 60

    print(f"\n{lijn}")
    print(f"  HUMANISERINGSRAPPORT — {label}")
    print(f"{lijn}")
    print(f"  Woorden: {r['woorden']}  |  Zinnen: {r['zinnen']}")
    print(f"  Risicoscore: {r['score']} patroon/patronen → {r['risico'].upper()}")
    print(lijn2)

    if r["niveau1"]:
        print(f"\n⚠  NIVEAU 1-WOORDEN (altijd vervangen) — {len(r['niveau1'])} gevonden")
        for item in r["niveau1"]:
            print(f"   • \"{item['term']}\"")
            print(f"     → {item['context']}")
            if suggest and item.get("suggestions"):
                alts = ", ".join(item["suggestions"])
                print(f"     → Alternatieven: {alts}")
    else:
        print("\n✓  Geen Niveau 1-woorden gevonden")

    if r["niveau2"]:
        print(f"\n⚠  NIVEAU 2-DICHTHEID (te hoog) — {len(r['niveau2'])} woorden")
        for item in r["niveau2"]:
            print(f"   • \"{item['term']}\" — {item['totaal']}x "
                  f"({item['per_500w']}x per 500 woorden, max: 1x)")
    else:
        print("✓  Niveau 2-dichtheid binnen norm")

    if r["niveau3"]:
        print(f"\n⚠  NIVEAU 3-DICHTHEID (>3%) — {len(r['niveau3'])} woorden")
        for item in r["niveau3"]:
            print(f"   • \"{item['term']}\" — {item['totaal']}x "
                  f"({item['percentage']}% van tekst, max: 3%)")
    else:
        print("✓  Niveau 3-dichtheid binnen norm")

    if r["openers"]:
        print(f"\n⚠  FORMULAÏSCHE OPENERS — {len(r['openers'])} gevonden")
        for item in r["openers"]:
            print(f"   • {item['type']}")
            print(f"     → \"{item['context']}\"")
    else:
        print("✓  Geen formulaïsche openers gevonden")

    if r["fillers"]:
        print(f"\n⚠  VULLINGSZINNEN — {len(r['fillers'])} gevonden")
        for item in r["fillers"]:
            print(f"   • \"{item['context']}\"")
    else:
        print("✓  Geen vullingszinnen gevonden")

    if r["rhythm"]:
        print(f"\n⚠  UNIFORM ZINSRITME")
        for item in r["rhythm"]:
            print(f"   • {item}")
    else:
        print("✓  Zinslengte voldoende gevarieerd")

    if r["para_starters"]:
        print(f"\n⚠  HERHALENDE ALINEASTARTERS")
        for item in r["para_starters"]:
            print(f"   • {item}")
    else:
        print("✓  Alineastarters voldoende gevarieerd")

    if r.get("sent_starters"):
        print(f"\n⚠  HERHALENDE ZINSSTARTERS (binnen alinea)")
        for item in r["sent_starters"]:
            print(f"   • {item}")
    else:
        print("✓  Zinsstarters voldoende gevarieerd")

    if r.get("em_dashes"):
        print(f"\n⚠  EM DASHES (—) — {len(r['em_dashes'])} gevonden")
        for item in r["em_dashes"]:
            print(f"   • {item['context']}")
        print("     → Vervang — door komma, punt of gedachtestreepje ( - )")
    else:
        print("✓  Geen em dashes gevonden")

    if r.get("vague_attr"):
        print(f"\n⚠  VAGE BRONVERMELDING — {len(r['vague_attr'])} gevonden")
        for item in r["vague_attr"]:
            print(f"   • \"{item['context']}\"")
        print("     → Voeg een APA-citatie toe of verwijder de claim")
    else:
        print("✓  Geen vage bronvermelding gevonden")

    if r.get("passive_hoog"):
        print(f"\n⚠  HOGE PASSIEF-DICHTHEID ({r['passive_pct']}%)")
        print(f"     → {r['passive_count']} van {r['zinnen']} zinnen bevatten passief")
        print(f"     → Norm: max 40% | Herschrijf passieve zinnen naar actief")
    else:
        pct = r.get('passive_pct', 0)
        if pct > 0:
            print(f"✓  Passief-dichtheid binnen norm ({pct}%)")

    if r.get("connector_hoog"):
        print(f"\n⚠  HOGE CONNECTOR-DICHTHEID ({r['connector_pct']}%)")
        print(f"     → Norm: max 30% zinnen beginnen met een connector")
        print(f"     → Varieer zinsopeningen: begin met onderwerp of bijzin")
    else:
        pct = r.get('connector_pct', 0)
        if pct > 0:
            print(f"✓  Connector-dichtheid binnen norm ({pct}%)")

    if r.get("adj_stacking"):
        print(f"\n⚠  BIJVOEGLIJK-NAAMWOORDSTAPELING — {len(r['adj_stacking'])} gevonden")
        for item in r["adj_stacking"]:
            print(f"   • {item}")
        print("     → Beschrijf eigenschappen in aparte zinnen of kies de belangrijkste")
    else:
        print("✓  Geen bijvoeglijk-naamwoordstapeling gevonden")

    if r.get("tricolon_hoog"):
        print(f"\n⚠  OVERMATIG TRICOLONS ({r['tricolon_count']}x)")
        print(f"     → Driedelige opsommingen ('A, B en C') zijn AI-typisch bij herhaling")
        print(f"     → Wissel af met twee- of vierdelige opsommingen")
    else:
        tc = r.get('tricolon_count', 0)
        if tc > 0:
            print(f"✓  Tricolons aanwezig maar niet overmatig ({tc}x)")

    if r.get("ttr_laag") and r.get("ttr", 0) > 0:
        print(f"\n⚠  LAGE WOORDENSCHATVARIATIE (MATTR: {r['ttr']})")
        print(f"     → Menselijk schrijven: 0.65–0.80 | AI-schrijven: 0.50–0.65")
        print(f"     → Gebruik meer synoniemen en gevarieerde formuleringen")
    elif r.get("ttr", 0) > 0:
        print(f"✓  Woordenschatvariatie voldoende (MATTR: {r['ttr']})")

    if r.get("oxford_comma"):
        print(f"\n⚠  OXFORD COMMA — {len(r['oxford_comma'])} gevonden (Categorie 8)")
        for item in r["oxford_comma"]:
            print(f"   • {item}")
        print("     → Verwijder de komma vóór 'en' in driedelige opsommingen")
    else:
        print("✓  Geen Oxford comma gevonden")

    if r.get("anglicisms"):
        print(f"\n⚠  ANGLICISMEN — {len(r['anglicisms'])} gevonden (Categorie 7)")
        for item in r["anglicisms"]:
            term = item["term"] if isinstance(item, dict) else item[0]
            context = item["context"] if isinstance(item, dict) else item[1]
            print(f"   • \"{term}\"")
            print(f"     → {context}")
            if suggest:
                alts = SUGGESTIONS.get(term.lower(), [])
                if alts:
                    print(f"     → Alternatieven: {', '.join(alts)}")
    else:
        print("✓  Geen anglicismen gevonden")

    if r.get("flesch_laag") and r.get("flesch", 100) < 100:
        print(f"\n⚠  FLESCH-DOUMA SCORE ({r['flesch']}) — te laag voor HBO-tekst")
        print(f"     → HBO-norm: 30–50 | Score < 30 = AI schrijft te formeel/complex")
        print(f"     → Breek lange zinnen op of gebruik eenvoudiger zinsconstructies")
    elif r.get("flesch", 0) > 0:
        print(f"✓  Flesch-Douma leesbaarheid: {r['flesch']} (HBO-norm: 30–50)")

    if r.get("communicatievormen"):
        print(f"\n⚠  COMMUNICATIEVORMEN (chatbot-taal) — {len(r['communicatievormen'])} gevonden")
        for item in r["communicatievormen"]:
            print(f"   • {item}")
        print("     → Schrijf als auteur, niet als assistent")
    else:
        print("✓  Geen chatbot-communicatievormen gevonden")

    if r.get("alinea_variatie"):
        print(f"\n⚠  ALINEA-LENGTEVARIATIE (Categorie 20)")
        for item in r["alinea_variatie"]:
            print(f"   • {item}")
        print("     → Varieer alinealengte bewust: kort (1-2 zinnen) en lang (5+ zinnen) afwisselen")
    else:
        print("✓  Alinea-lengtevariatie voldoende")

    print(f"\n{lijn2}")
    if r["risico"] == "Laag":
        print("  CONCLUSIE: Laag risico — kleine bijstellingen volstaan")
    elif r["risico"] == "Gemiddeld":
        print("  CONCLUSIE: Gemiddeld risico — herschrijf betreffende alinea's")
    else:
        print("  CONCLUSIE: Hoog risico — dringend herschrijven aanbevolen")
    print(f"{lijn}\n")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Detecteer AI-schrijfpatronen in Nederlandse tekst (DutchQuill AI)"
    )
    parser.add_argument("--input", "-i", help="Invoerbestand (tekst). Standaard: stdin.")
    parser.add_argument(
        "--compare", nargs=2, metavar=("ORIGINEEL", "HERSCHREVEN"),
        help="Vergelijk twee bestanden (voor/na vergelijking)"
    )
    parser.add_argument("--json", action="store_true", help="Uitvoer als JSON")
    parser.add_argument(
        "--suggest", action="store_true",
        help="Toon alternatieven voor gevonden Niveau 1-woorden en anglicismen"
    )
    args = parser.parse_args()

    if args.compare:
        try:
            with open(args.compare[0], encoding="utf-8") as f:
                text_a = f.read()
            with open(args.compare[1], encoding="utf-8") as f:
                text_b = f.read()
        except FileNotFoundError as e:
            print(f"Fout: Bestand niet gevonden — {e}", file=sys.stderr)
            sys.exit(1)

        result_a = analyze(text_a)
        result_b = analyze(text_b)

        if args.json:
            print(json.dumps({"origineel": result_a, "herschreven": result_b},
                             ensure_ascii=False, indent=2))
        else:
            print_report(result_a, "ORIGINEEL", suggest=args.suggest)
            print_report(result_b, "HERSCHREVEN", suggest=args.suggest)
            delta = result_b["score"] - result_a["score"]
            sign = "+" if delta > 0 else ""
            print(f"  DELTA: {sign}{delta} patronen  "
                  f"({result_a['risico']} → {result_b['risico']})\n")

    else:
        if args.input:
            try:
                with open(args.input, encoding="utf-8") as f:
                    text = f.read()
            except FileNotFoundError:
                print(f"Fout: Bestand niet gevonden — {args.input}", file=sys.stderr)
                sys.exit(1)
        else:
            text = sys.stdin.read()

        if not text.strip():
            print("Fout: Lege invoer.", file=sys.stderr)
            sys.exit(1)

        result = analyze(text)

        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_report(result, suggest=args.suggest)


if __name__ == "__main__":
    main()
