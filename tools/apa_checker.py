#!/usr/bin/env python3
"""
tools/apa_checker.py — DutchQuill AI

Controleert een tekst op veelvoorkomende APA 7e editie overtredingen.
Gebaseerd op apa_nl_gids.md (bron: Scribbr NL).

Gecontroleerde regels:
  1. "&" in lopende tekst buiten haakjes (moet "en" zijn)
  2. In-text citaties: voornamen aanwezig, komma ontbreekt
  3. Directe citaten (<40 woorden): paginanummer aanwezig?
  4. Meerdere bronnen: puntkomma als scheidingsteken?
  5. Citatiepositie: staat citatie vóór de punt?
  6. Literatuurlijst aanwezig en juist benoemd?
  7. z.d.-differentiatie: meerdere bronnen van dezelfde auteur zonder letter-suffix
  8. Citatie-dekking: in-text citaties zonder overeenkomstige literatuurlijst-entry

Let op: regex-gebaseerde checker — controleer bevindingen altijd zelf.

Gebruik:
    python3 tools/apa_checker.py --input rapport.txt
    cat rapport.txt | python3 tools/apa_checker.py
    python3 tools/apa_checker.py --input rapport.txt --json
"""

import sys
import re
import json
import argparse
from typing import List, Dict

Finding = Dict  # {"regel": int, "categorie": str, "tekst": str, "melding": str, "suggestie": str}


def get_lines(text: str) -> List[str]:
    return text.splitlines()


# ─────────────────────────────────────────────
# CHECK 1: "&" buiten haakjes in lopende tekst
# ─────────────────────────────────────────────

def check_ampersand_in_text(lines: List[str]) -> List[Finding]:
    """
    Detecteer '&' in lopende tekst buiten haakjes.
    Uitzondering: '&' binnen (…) is correct APA.
    """
    findings = []
    for i, line in enumerate(lines, 1):
        # Verwijder alles tussen haakjes voor de check
        stripped = re.sub(r'\([^)]*\)', '', line)
        # Zoek naar & dat niet deel is van HTML-entities of URLs
        matches = list(re.finditer(r'(?<!\w)&(?!\w|amp;|lt;|gt;)', stripped))
        for m in matches:
            findings.append({
                "regel": i,
                "categorie": "In-text citatie",
                "tekst": line.strip()[:100],
                "melding": "\"&\" gebruikt in lopende tekst buiten haakjes",
                "suggestie": (
                    "Vervang \"&\" door \"en\" in lopende tekst. "
                    "Gebruik \"&\" alleen binnen haakjes: (Auteur & Auteur, jaar)."
                ),
            })
    return findings


# ─────────────────────────────────────────────
# CHECK 2: In-text citaties op correct format
# ─────────────────────────────────────────────

def check_intext_citation_format(lines: List[str]) -> List[Finding]:
    """
    Controleer parenthetische citaties op voornamen en ontbrekende komma's.
    """
    findings = []
    citation_pattern = re.compile(r'\(([^)]{5,120})\)')

    for i, line in enumerate(lines, 1):
        for m in citation_pattern.finditer(line):
            content = m.group(1)

            # Sla over als het geen jaar bevat (geen citatie)
            if not re.search(r'\b(19|20)\d{2}\b|z\.d\.', content):
                continue

            # Check: voornaam aanwezig — alleen in het auteursdeel (voor eerste komma)
            # Patroon: "Jan de Vries" of "Marie Bakker" — niet org-namen of technische termen
            comma_pos = content.find(',')
            if comma_pos >= 0:
                author_part = content[:comma_pos].strip()
                # Sla technische content over (digits, dubbele punt, puntkomma, koppelteken)
                if not re.search(r'[\d:;\-]', author_part):
                    words = author_part.split()
                    # 2-woord naam: Voornaam Achternaam (bv. "Marie Bakker")
                    if (len(words) == 2
                            and re.match(r'^[A-Z][a-z]{2,}$', words[0])
                            and re.match(r'^[A-Z][a-z]{2,}$', words[1])):
                        findings.append({
                            "regel": i,
                            "categorie": "In-text citatie",
                            "tekst": f"({content})",
                            "melding": "Mogelijk voornaam in citatie",
                            "suggestie": (
                                "Gebruik alleen achternaam: (Achternaam, jaar). "
                                "Geen voornamen of titels in APA-citaties."
                            ),
                        })
                    # 3-woord naam met tussenvoegsel: "Jan de Vries", "Marie van Berg"
                    elif (len(words) == 3
                            and re.match(r'^[A-Z][a-z]{1,}$', words[0])
                            and re.match(
                                r'^(de|van|den|der|te|ter|ten|op|in|bij|voor|af|uit|aan|over)$',
                                words[1], re.IGNORECASE)
                            and re.match(r'^[A-Z][a-z]{1,}$', words[2])):
                        findings.append({
                            "regel": i,
                            "categorie": "In-text citatie",
                            "tekst": f"({content})",
                            "melding": "Mogelijk voornaam in citatie (inclusief tussenvoegsel)",
                            "suggestie": (
                                "Gebruik alleen achternaam met tussenvoegsel: (De Vries, jaar). "
                                "Geen voornamen in APA-citaties."
                            ),
                        })

            # Check: ontbrekende komma tussen auteur en jaar
            # "Achternaam 2021" zonder komma
            if re.search(r'[a-zéèëàä]\s+(19|20)\d{2}', content):
                findings.append({
                    "regel": i,
                    "categorie": "In-text citatie",
                    "tekst": f"({content})",
                    "melding": "Mogelijk ontbrekende komma tussen auteur en jaar",
                    "suggestie": "Correct format: (Achternaam, jaar) — let op de komma na de achternaam.",
                })

            # Check: meerdere bronnen zonder puntkomma (jaar gevolgd door hoofdletter)
            if re.search(r'\d{4}\s+[A-Z]', content):
                findings.append({
                    "regel": i,
                    "categorie": "In-text citatie",
                    "tekst": f"({content})",
                    "melding": "Mogelijk ontbrekende puntkomma tussen meerdere bronnen",
                    "suggestie": (
                        "Meerdere bronnen scheiden met puntkomma, alfabetisch: "
                        "(Auteur, jaar; Auteur, jaar)."
                    ),
                })

    return findings


# ─────────────────────────────────────────────
# CHECK 3: Directe citaten — paginanummer
# ─────────────────────────────────────────────

def check_direct_quotes(text: str) -> List[Finding]:
    """
    Zoek korte directe citaten (aanhalingstekens) en controleer of er
    een paginanummer aanwezig is in de bijbehorende citatie.
    """
    findings = []

    # Zoek aanhalingstekens: dubbel recht, of typografisch
    quote_pattern = re.compile(
        r'(?:"([^"]{15,250})"|'         # "..."
        r'\u201e([^\u201d]{15,250})\u201d|'  # „..."
        r'\u201c([^\u201d]{15,250})\u201d)'  # "..."
    )

    for m in quote_pattern.finditer(text):
        quote_text = m.group(1) or m.group(2) or m.group(3)
        word_count = len(quote_text.split())

        if word_count >= 40:
            continue  # Blokcitaten apart

        line_num = text[:m.start()].count('\n') + 1
        context_after = text[m.end():m.end() + 100]

        has_page = bool(re.search(r'p\.\s*\d+|pp\.\s*\d+|par\.\s*\d+', context_after))
        has_citation = bool(re.search(r'\([A-Z][^)]{2,60}\d{4}[^)]*\)', context_after[:80]))

        if has_citation and not has_page:
            findings.append({
                "regel": line_num,
                "categorie": "Directe citaten",
                "tekst": (f'"{quote_text[:60]}..."' if len(quote_text) > 60
                          else f'"{quote_text}"'),
                "melding": "Direct citaat zonder paginanummer",
                "suggestie": (
                    "Voeg paginanummer toe: (Auteur, jaar, p. X). "
                    "Gebruik par. X als er geen paginanummering is."
                ),
            })

    return findings


# ─────────────────────────────────────────────
# CHECK 4: Citatiepositie (vóór de punt)
# ─────────────────────────────────────────────

def check_citation_position(lines: List[str]) -> List[Finding]:
    """
    In-text citaties staan vóór de punt van de zin.
    Detecteer citaties die ná de punt staan.
    """
    findings = []
    # Punt gevolgd door spatie en dan een citatie op dezelfde regel
    for i, line in enumerate(lines, 1):
        matches = re.finditer(r'\.\s+(\([A-Z][^)]{3,80}\d{4}[^)]*\))', line)
        for m in matches:
            findings.append({
                "regel": i,
                "categorie": "Citatiepositie",
                "tekst": line.strip()[:100],
                "melding": "Citatie staat mogelijk na de punt (moet ervoor staan)",
                "suggestie": (
                    "Plaats de citatie vóór de punt: \"...dit klopt (De Vries, 2020).\" "
                    "Uitzondering: blokcitaten (≥40 woorden) krijgen de citatie ná de punt."
                ),
            })
    return findings


# ─────────────────────────────────────────────
# CHECK 5: Literatuurlijst aanwezig?
# ─────────────────────────────────────────────

def check_reference_list(text: str) -> List[Finding]:
    """Controleer of er een literatuurlijst aanwezig is en correct benoemd is."""
    findings = []

    has_ref = bool(re.search(
        r'\b(literatuurlijst|referentielijst|referenties)\b', text, re.IGNORECASE
    ))

    if not has_ref:
        findings.append({
            "regel": 0,
            "categorie": "Literatuurlijst",
            "tekst": "",
            "melding": "Geen literatuurlijst of referentielijst gevonden",
            "suggestie": (
                "Voeg een sectie \"Literatuurlijst\" toe aan het einde van het rapport "
                "(vóór bijlagen)."
            ),
        })
    else:
        if re.search(r'\bbibliografie\b', text, re.IGNORECASE):
            findings.append({
                "regel": 0,
                "categorie": "Literatuurlijst",
                "tekst": "Bibliografie",
                "melding": "Sectie heet \"Bibliografie\" — APA 7 gebruikt \"Literatuurlijst\"",
                "suggestie": "Hernoem de sectie naar \"Literatuurlijst\" of \"Referentielijst\".",
            })

    return findings


# ─────────────────────────────────────────────
# CHECK 6: Voornamen in lopende tekst citaties
# ─────────────────────────────────────────────

def check_narrative_voornamen(lines: List[str]) -> List[Finding]:
    """
    Detecteer narratieve citaties met voornamen in lopende tekst.
    Bijv. "Jan de Vries (2021)" — voornaam moet niet aanwezig zijn.
    """
    findings = []
    # Patroon: voornaam + achternaam + (jaar)
    pattern = re.compile(r'\b[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}\s+\((19|20)\d{2}\)')

    for i, line in enumerate(lines, 1):
        for m in pattern.finditer(line):
            findings.append({
                "regel": i,
                "categorie": "In-text citatie (narratief)",
                "tekst": m.group(0),
                "melding": "Mogelijk voornaam in narratieve citatie",
                "suggestie": (
                    "Gebruik alleen achternaam: \"Achternaam (jaar)\". "
                    "Geen voornamen in APA-citaties."
                ),
            })

    return findings


# ─────────────────────────────────────────────
# CHECK 7: z.d.-differentiatie
# ─────────────────────────────────────────────

def check_zd_differentiation(text: str) -> List[Finding]:
    """
    Detecteer meerdere bronnen van dezelfde auteur met z.d. zonder letter-suffix.
    APA 7 vereist z.d.-a, z.d.-b, etc. als dezelfde auteur meerdere undated bronnen heeft.

    Controleert:
      - Referentielijst: zelfde auteur met 2+ (z.d.) zonder suffix
      - In-text: zelfde auteur met (Auteur, z.d.) 2+ keer zonder suffix
    """
    findings = []

    # ── Referentielijst: Auteur. (z.d.). zonder letter-suffix ──
    # Patroon: begin van een regel, auteursnaam, punt, (z.d.) zonder -letter
    reflist_pattern = re.compile(
        r'^([A-Z][^\n.(]{1,80})\.\s*\(z\.d\.\)(?!-[a-z])',
        re.MULTILINE
    )

    authors_reflist: Dict[str, list] = {}
    for m in reflist_pattern.finditer(text):
        author_key = re.sub(r'\s+', ' ', m.group(1)).strip()
        line_num = text[:m.start()].count('\n') + 1
        authors_reflist.setdefault(author_key, []).append(line_num)

    for author, line_nums in authors_reflist.items():
        if len(line_nums) >= 2:
            for ln in line_nums:
                findings.append({
                    "regel": ln,
                    "categorie": "z.d.-differentiatie",
                    "tekst": f"{author}. (z.d.)",
                    "melding": (
                        f"Auteur \"{author}\" heeft {len(line_nums)} bronnen met "
                        f"(z.d.) zonder letter-suffix in de literatuurlijst"
                    ),
                    "suggestie": (
                        "Differentieer met letters: (z.d.-a), (z.d.-b), (z.d.-c) etc. "
                        "Gebruik dezelfde letters in de in-text citaties: (Auteur, z.d.-a)."
                    ),
                })

    # ── In-text: (Auteur, z.d.) zonder suffix, zelfde auteur 2+ keer ──
    intext_pattern = re.compile(
        r'\(([^,\)]{2,80}),\s*z\.d\.(?!-[a-z])\)',
        re.IGNORECASE
    )

    authors_intext: Dict[str, list] = {}
    for m in intext_pattern.finditer(text):
        author_key = re.sub(r'\s+', ' ', m.group(1)).strip()
        # Sla technische content over (digits, dubbele punt, puntkomma)
        if re.search(r'[\d:;]', author_key):
            continue
        line_num = text[:m.start()].count('\n') + 1
        authors_intext.setdefault(author_key, []).append(line_num)

    for author, line_nums in authors_intext.items():
        if len(line_nums) >= 2:
            for ln in line_nums:
                findings.append({
                    "regel": ln,
                    "categorie": "z.d.-differentiatie",
                    "tekst": f"({author}, z.d.)",
                    "melding": (
                        f"In-text citatie \"({author}, z.d.)\" verschijnt {len(line_nums)}× "
                        f"zonder letter-suffix"
                    ),
                    "suggestie": (
                        "Voeg letter-suffixen toe om bronnen te onderscheiden: "
                        "(Auteur, z.d.-a), (Auteur, z.d.-b)."
                    ),
                })

    return findings


# ─────────────────────────────────────────────
# CHECK 8: Citatie-dekking (in-text vs literatuurlijst)
# ─────────────────────────────────────────────

def check_citation_coverage(text: str) -> List[Finding]:
    """
    Controleer of alle in-text citaties een overeenkomstige entry hebben in de
    literatuurlijst. Splitst tekst bij de literatuurlijst-heading en vergelijkt
    geciteerde auteursleutels met auteurs die in de referentie-entries voorkomen.
    """
    findings = []

    # Splits tekst bij literatuurlijst-heading
    lit_split = re.split(
        r'\n#+\s*(?:literatuurlijst|referentielijst|referenties)\s*\n',
        text, maxsplit=1, flags=re.IGNORECASE
    )
    if len(lit_split) < 2:
        return findings  # check_reference_list rapporteert ontbrekende heading

    body_text, ref_text = lit_split

    # Extraheer eerste auteur uit elke parenthetische in-text citatie
    citation_pattern = re.compile(
        r'\(([A-Z][a-zA-ZÀ-ÿ\-]+(?:\s+et\s+al\.)?'
        r'(?:\s+&\s+[A-Z][a-zA-ZÀ-ÿ\-]+)*),\s*(?:19|20)\d{2}[a-z]?\)',
        re.UNICODE
    )
    cited_authors: set = set()
    for m in citation_pattern.finditer(body_text):
        raw = m.group(1)
        # Neem alleen het eerste achternaam-token (vóór '&' of 'et al')
        first = re.split(r'\s+et\s+al|\s*&', raw)[0].strip()
        if first:
            cited_authors.add(first.lower())

    if not cited_authors:
        return findings

    # Extraheer auteur-sleutels uit de literatuurlijst (eerste hoofdletter-woord per regel)
    ref_author_re = re.compile(r'^([A-Z][a-zA-ZÀ-ÿ\-]+)', re.UNICODE)
    ref_author_keys: set = set()
    for line in ref_text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = ref_author_re.match(line)
        if m:
            ref_author_keys.add(m.group(1).lower())

    # Rapporteer geciteerde auteurs die niet in de literatuurlijst staan
    for author in sorted(cited_authors):
        if author not in ref_author_keys:
            findings.append({
                "regel": 0,
                "categorie": "Literatuurlijst (dekking)",
                "tekst": author.capitalize(),
                "melding": (
                    f"In-text citatie \"{author.capitalize()}\" heeft geen "
                    "overeenkomstige entry in de literatuurlijst"
                ),
                "suggestie": (
                    f"Voeg een referentie-entry toe voor \"{author.capitalize()}\" "
                    "in de literatuurlijst, of verwijder de in-text citatie."
                ),
            })

    return findings


# ─────────────────────────────────────────────
# HOOFDFUNCTIE
# ─────────────────────────────────────────────

def run_checks(text: str) -> List[Finding]:
    lines = get_lines(text)
    findings = []
    findings += check_ampersand_in_text(lines)
    findings += check_intext_citation_format(lines)
    findings += check_direct_quotes(text)
    findings += check_citation_position(lines)
    findings += check_reference_list(text)
    findings += check_narrative_voornamen(lines)
    findings += check_zd_differentiation(text)
    findings += check_citation_coverage(text)
    return findings


def print_report(findings: List[Finding]) -> None:
    total = len(findings)
    lijn = "═" * 60
    lijn2 = "─" * 60

    print(f"\n{lijn}")
    print(f"  APA-CHECKER RAPPORT — DutchQuill AI")
    print(f"{lijn}")
    print(f"  Gevonden: {total} mogelijke overtreding(en)")
    print(lijn2)

    if not findings:
        print("\n  ✓ Geen APA-overtredingen gedetecteerd.\n")
    else:
        categories: Dict[str, List] = {}
        for f in findings:
            categories.setdefault(f["categorie"], []).append(f)

        for cat, items in categories.items():
            print(f"\n  [{cat}] — {len(items)} bevinding(en)")
            for item in items:
                regel_str = f"Regel {item['regel']}: " if item["regel"] > 0 else ""
                print(f"\n  ✗ {regel_str}{item['melding']}")
                if item["tekst"]:
                    preview = item["tekst"][:80] + ("..." if len(item["tekst"]) > 80 else "")
                    print(f"    Tekst:   \"{preview}\"")
                print(f"    Advies:  {item['suggestie']}")

    print(f"\n{lijn}")
    print("  Let op: APA-checker detecteert patronen via regex.")
    print("  Controleer bevindingen altijd zelf voor je aanpassingen maakt.")
    print(f"{lijn}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Controleer tekst op APA 7e editie overtredingen (DutchQuill AI)"
    )
    parser.add_argument("--input", "-i", help="Invoerbestand. Standaard: stdin.")
    parser.add_argument("--json", action="store_true", help="Uitvoer als JSON")
    args = parser.parse_args()

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

    findings = run_checks(text)

    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    else:
        print_report(findings)


if __name__ == "__main__":
    main()
