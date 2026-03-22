#!/usr/bin/env python3
"""
md_to_docx.py — Markdown/plain-text naar APA .docx via word_export.py

Gebruik:
    python3 tools/md_to_docx.py --input .tmp/herschreven.txt
    python3 tools/md_to_docx.py --input .tmp/herschreven.txt --output .tmp/herschreven.docx
    python3 tools/md_to_docx.py --input .tmp/tekst.txt \\
        --metadata '{"naam":"Jan Jansen","studentnummer":"123456","opleiding":"Software Engineering","instelling":"Hogeschool Amsterdam"}' \\
        --output .tmp/tekst.docx

Front matter: platte tekst vóór de eerste heading wordt automatisch herkend als
titelpaginadata (titel, auteur, studentnummer, instelling, opleiding, datum).
CLI --metadata overschrijft front matter waar beide bestaan.

Heading mapping (markdown → APA):
    #    → heading level 1 (gecentreerd, vet — APA Level 1)
    ##   → heading level 2 (links, vet — APA Level 2)
    ###  → heading level 3 (links, vet cursief — APA Level 3)
    #### → heading level 4 (ingesprongen, vet — APA Level 4)

Sectie-extractie (APA):
    - Inleiding wordt apart geëxtraheerd; kop = documenttitel (APA 7 regel)
    - Conclusie wordt apart geëxtraheerd; kop = "Conclusie"

Ondersteunde markdown-elementen:
    - Koppen (#, ##, ###, ####)
    - Alinea's (met inline *cursief* en **vet**)
    - Lijstitems (- item, * item, 1. item)
    - Tabellen (| kop | kop | formaat)
    - Blokcitaten (> tekst)
    - Figuren (![caption](pad/naar/afbeelding.png))
    - Paginascheidingen (---)
    - Referentieblok (# Literatuurlijst)

Stdout bij succes: absoluut pad naar het gegenereerde .docx-bestand
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from typing import Optional, List, Dict, Tuple


def strip_inline(text: str) -> str:
    """Verwijder markdown inline-opmaak (**bold**, *italic*, `code`)."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    return text.strip()


REFERENCES_HEADERS = re.compile(
    r'^#{1,3}\s*(?:\d+\.?\d*\.?\s*)?(literatuurlijst|bronnenlijst|referentielijst|bronnen|literatuur)\s*$',
    re.IGNORECASE
)

# Bijlagen-sectie (overkoepelend) — wordt genegeerd als kop; wisselt naar bijlagen-modus
_BIJLAGEN_SECTION = re.compile(r'^#{1,3}\s+Bijlagen?\s*$', re.IGNORECASE)

# Individuele bijlage-kop: ## Bijlage A: Titel  of  ## Bijlage A — Titel
_BIJLAGE_ITEM = re.compile(
    r'^#{1,3}\s+(Bijlage\s+[A-Z])\s*(?:[:\-]\s*(.+))?$',
    re.IGNORECASE
)

# Optioneel numeriek prefix in kopnamen (bijv. "1.", "3.1") — altijd verwijderen uit .docx
_HEADING_NUMBER_PREFIX = re.compile(r'^\d+\.?\d*\.?\s*')

# Samenvatting/abstract sectie
_ABSTRACT_HEADING = re.compile(r'^(samenvatting|abstract)\s*$', re.IGNORECASE)

# Labels die in front matter herkend worden
_FM_TITEL = re.compile(r'^(?:Titel|Title):\s*(.+)', re.IGNORECASE)
_FM_AUTEUR = re.compile(r'^(?:Auteur|Author|Naam):\s*(.+)', re.IGNORECASE)
_FM_INSTELLING = re.compile(r'^(?:Instelling|Institution|School|Universiteit|Hogeschool):\s*(.+)', re.IGNORECASE)
_FM_STUDENTNUMMER = re.compile(r'^Studentnummer:\s*(.+)', re.IGNORECASE)
_FM_OPLEIDING = re.compile(r'^Opleiding:\s*(.+)', re.IGNORECASE)
_FM_VAK = re.compile(r'^Vak(?:naam)?(?:\s*[-/]\s*\S+)?:\s*(.+)', re.IGNORECASE)
_FM_BEGELEIDER = re.compile(r'^(?:Begeleider|Docent|Examinator|Supervisor)s?:\s*(.+)', re.IGNORECASE)
_FM_DATUM = re.compile(r'^(?:Datum|Date):\s*(.+)', re.IGNORECASE)
_FM_TOC = re.compile(r'^(inhoudsopgave|table of contents)$', re.IGNORECASE)

# Nederlandse datum zonder label-prefix: "12 maart 2026", "1 januari 2025"
_NL_MONTHS = (
    'januari', 'februari', 'maart', 'april', 'mei', 'juni',
    'juli', 'augustus', 'september', 'oktober', 'november', 'december',
)
_FM_NL_DATE = re.compile(
    r'^\d{1,2}\s+(' + '|'.join(_NL_MONTHS) + r')\s+\d{4}$',
    re.IGNORECASE
)

# Trefwoorden om instellingen te herkennen
_INSTITUTION_KEYWORDS = [
    'hogeschool', 'universiteit', 'university', 'college',
    'novi', 'fontys', 'saxion', 'avans',
]

# Sectie-extractie patronen
_INTRO_HEADING = re.compile(r'^(\d+\.?\s*)?(inleiding)\s*$', re.IGNORECASE)
_CONCLUSION_HEADING = re.compile(
    r'^(\d+\.?\s*)?(conclusie|discussie|conclusie en discussie|conclusie en aanbevelingen)\s*$',
    re.IGNORECASE
)

# Plain-text sectie-headers (zonder # prefix — van .docx met normale alineastijl)
_REFERENCES_PLAIN = re.compile(
    r'^(literatuurlijst|bronnenlijst|referentielijst|bronnen|literatuur)\s*$',
    re.IGNORECASE
)
_BIJLAGEN_PLAIN = re.compile(r'^Bijlagen?\s*$', re.IGNORECASE)
_BIJLAGE_PLAIN = re.compile(
    r'^(Bijlage\s+[A-Z])\s*(?:[:\-]\s*(.+))?$',
    re.IGNORECASE
)
# Tabel-/figuurlabel op eigen regel: **Tabel N** of **Tabel N: ...**
_TABLE_LABEL_LINE = re.compile(r'^\*\*(Tabel|Figuur)\s+\d+', re.IGNORECASE)
# nmap-stijl commentaarregels die ten onrechte als # Heading worden herkend in bijlagen
_NMAP_COMMENT_RE = re.compile(
    r'^(Nmap\s+\d|Starting\s+Nmap|Nmap\s+done|Host\s+is\s+up|'
    r'Not\s+shown|Scanned\s+at|Scan\s+report\s+for)',
    re.IGNORECASE
)


def extract_front_matter(lines: List[str]) -> Tuple[Dict[str, str], int]:
    """
    Herkent titelpagina-metadata op twee manieren:

    1. YAML-stijl front matter (--- ... ---):
       Als het document begint met een `---` blok, worden de Key: Value
       regels daarin geparseerd. De sluitende `---` en alles daarvoor wordt
       overgeslagen als body-content.

    2. Plain-text front matter (originele stijl):
       Regels vóór de eerste # heading worden heuristisch geparseerd.

    Returns:
        (front_matter_meta, first_content_index)
        first_content_index = index van de eerste regel na de front matter.
    """

    # ── Detecteer YAML-stijl front matter (--- blok) ──
    if lines and lines[0].strip() == '---':
        closing_idx = None
        for i in range(1, len(lines)):
            if lines[i].strip() == '---':
                closing_idx = i
                break
        if closing_idx is not None:
            meta: Dict[str, str] = {}
            yaml_lines = [l.strip() for l in lines[1:closing_idx] if l.strip()]
            for line in yaml_lines:
                m = _FM_TITEL.match(line)
                if m:
                    meta['titel'] = strip_inline(m.group(1).strip())
                    continue
                m = _FM_AUTEUR.match(line)
                if m:
                    meta['naam'] = m.group(1).strip()
                    continue
                m = _FM_INSTELLING.match(line)
                if m:
                    meta['instelling'] = m.group(1).strip()
                    continue
                m = _FM_STUDENTNUMMER.match(line)
                if m:
                    meta['studentnummer'] = m.group(1).strip()
                    continue
                m = _FM_OPLEIDING.match(line)
                if m:
                    meta['opleiding'] = m.group(1).strip()
                    continue
                m = _FM_VAK.match(line)
                if m:
                    meta['vak'] = m.group(1).strip()
                    continue
                m = _FM_BEGELEIDER.match(line)
                if m:
                    meta['begeleider'] = m.group(1).strip()
                    continue
                m = _FM_DATUM.match(line)
                if m:
                    meta['datum'] = m.group(1).strip()
                    continue
                # Ongelabeld: instelling-keyword detectie
                line_lower = line.lower()
                if any(kw in line_lower for kw in _INSTITUTION_KEYWORDS):
                    if 'instelling' not in meta:
                        meta['instelling'] = line
                    continue
            return meta, closing_idx + 1

    # ── Plain-text front matter (originele heuristiek) ──
    # Zoek de eerste heading-regel
    first_heading_idx = len(lines)
    for i, line in enumerate(lines):
        if re.match(r'^#{1,6}\s+', line.rstrip()):
            first_heading_idx = i
            break

    if first_heading_idx == 0:
        return {}, 0

    # Verzamel niet-lege regels vóór de eerste heading
    fm_lines: List[str] = []
    for i in range(first_heading_idx):
        stripped = lines[i].strip()
        if stripped:
            fm_lines.append(stripped)

    if not fm_lines:
        return {}, first_heading_idx

    meta = {}
    consumed: set = set()  # indices van verwerkte regels

    # Pass 1: herken gelabelde velden
    for i, line in enumerate(fm_lines):
        m = _FM_TITEL.match(line)
        if m:
            meta['titel'] = strip_inline(m.group(1).strip())
            consumed.add(i)
            continue

        m = _FM_AUTEUR.match(line)
        if m:
            meta['naam'] = m.group(1).strip()
            consumed.add(i)
            continue

        m = _FM_INSTELLING.match(line)
        if m:
            meta['instelling'] = m.group(1).strip()
            consumed.add(i)
            continue

        m = _FM_STUDENTNUMMER.match(line)
        if m:
            meta['studentnummer'] = m.group(1).strip()
            consumed.add(i)
            # Auteur = vorige niet-verwerkte regel (als er geen Auteur: label was)
            if 'naam' not in meta and i > 0 and (i - 1) not in consumed:
                meta['naam'] = fm_lines[i - 1]
                consumed.add(i - 1)
            continue

        m = _FM_OPLEIDING.match(line)
        if m:
            meta['opleiding'] = m.group(1).strip()
            consumed.add(i)
            continue

        m = _FM_VAK.match(line)
        if m:
            meta['vak'] = m.group(1).strip()
            consumed.add(i)
            continue

        m = _FM_BEGELEIDER.match(line)
        if m:
            meta['begeleider'] = m.group(1).strip()
            consumed.add(i)
            continue

        m = _FM_DATUM.match(line)
        if m:
            meta['datum'] = m.group(1).strip()
            consumed.add(i)
            continue

        # Inhoudsopgave-label overslaan
        if _FM_TOC.match(line):
            consumed.add(i)
            continue

        # Instelling herkennen via keywords (ongelabelde regels)
        line_lower = line.lower()
        if any(kw in line_lower for kw in _INSTITUTION_KEYWORDS):
            if 'instelling' not in meta:
                meta['instelling'] = line
                consumed.add(i)
            continue

    # Alleen als front matter als we minstens één gestructureerd label vonden
    has_structured = any(k in meta for k in ('studentnummer', 'opleiding', 'datum', 'instelling'))
    if not has_structured:
        return {}, first_heading_idx

    # Pass 2: resterende regels → titelkandidaten + ongelabelde datums
    remaining_indices = [i for i in range(len(fm_lines)) if i not in consumed]
    remaining = [fm_lines[i] for i in remaining_indices]

    # Detecteer ongelabelde Nederlandse datum (bijv. "12 maart 2026") in resterende regels
    if 'datum' not in meta:
        for i, (idx, line) in enumerate(zip(remaining_indices, remaining)):
            if _FM_NL_DATE.match(line):
                meta['datum'] = line
                consumed.add(idx)
                remaining_indices.pop(i)
                remaining.pop(i)
                break

    # Eerste niet-verwerkte regel = titel (inline markdown strippen)
    if 'titel' not in meta:
        remaining = [fm_lines[i] for i in range(len(fm_lines)) if i not in consumed]
        if remaining:
            meta['titel'] = strip_inline(remaining[0])
            if len(remaining) > 1:
                meta['ondertitel'] = strip_inline(remaining[1])

    return meta, first_heading_idx


def extract_sections(blocks: List[Dict]) -> Tuple[Optional[Dict], List[Dict], List[Dict], List[Dict]]:
    """
    Extraheer samenvatting, inleiding en conclusie uit body-blocks (APA-structuur).

    De samenvatting-heading wordt verwijderd; tekst wordt als abstract-dict teruggegeven.
    De inleiding-heading wordt verwijderd (build_introduction plaatst de documenttitel).
    De conclusie-heading wordt verwijderd (build_conclusion plaatst "Conclusie").

    Returns:
        (abstract_data, intro_blocks, body_blocks, conclusion_blocks)
        abstract_data: {"text": str, "keywords": list[str]} of None
    """
    abstract_blocks: List[Dict] = []
    intro_blocks: List[Dict] = []
    conclusion_blocks: List[Dict] = []
    body_blocks: List[Dict] = []

    state = 'body'
    section_level: Optional[int] = None

    for block in blocks:
        is_heading = block.get('type') == 'heading'

        if is_heading:
            level = block.get('level', 1)
            text = block.get('text', '').strip()

            # Exit huidige sectie bij heading van gelijk of hoger niveau
            if state in ('abstract', 'intro', 'conclusion') and level <= section_level:
                state = 'body'

            # Detecteer secties (alleen vanuit body-state)
            if state == 'body':
                if _ABSTRACT_HEADING.match(text):
                    state = 'abstract'
                    section_level = level
                    continue  # Heading overslaan
                elif _INTRO_HEADING.match(text):
                    state = 'intro'
                    section_level = level
                    continue  # Heading overslaan
                elif _CONCLUSION_HEADING.match(text):
                    state = 'conclusion'
                    section_level = level
                    continue  # Heading overslaan

        # Ook paragrafen checken op sectie-koppen (docx soms zonder heading-stijl)
        elif block.get('type') == 'paragraph':
            text = block.get('text', '').strip()
            if _ABSTRACT_HEADING.match(text):
                state = 'abstract'
                section_level = 1
                continue
            elif _INTRO_HEADING.match(text):
                state = 'intro'
                section_level = 1
                continue
            elif _CONCLUSION_HEADING.match(text):
                state = 'conclusion'
                section_level = 1
                continue

        # Append naar juiste lijst
        if state == 'abstract':
            abstract_blocks.append(block)
        elif state == 'intro':
            intro_blocks.append(block)
        elif state == 'conclusion':
            conclusion_blocks.append(block)
        else:
            body_blocks.append(block)

    # Bouw abstract_data uit abstract_blocks
    abstract_data: Optional[Dict] = None
    if abstract_blocks:
        keywords: List[str] = []
        text_parts: List[str] = []
        for b in abstract_blocks:
            if b.get('type') == 'paragraph':
                t = b['text'].strip()
                kw_match = re.match(
                    r'^[\*_]{0,3}sleutelwoorden[\*_]{0,3}:\s*(.+?)[\*_]{0,3}\s*$',
                    t, re.IGNORECASE
                )
                if kw_match:
                    keywords = [k.strip().rstrip('*_') for k in kw_match.group(1).split(',')]
                else:
                    text_parts.append(strip_inline(t))
        abstract_text = ' '.join(text_parts).strip()
        if abstract_text:
            abstract_data = {"text": abstract_text}
            if keywords:
                abstract_data["keywords"] = keywords

    return abstract_data, intro_blocks, body_blocks, conclusion_blocks


def parse_table_lines(table_lines: List[str]) -> Dict:
    """
    Parse markdown-tabelregels naar een word_export.py tabelblok.

    Verwacht:
        | Kop 1 | Kop 2 |
        |-------|-------|
        | Cel 1 | Cel 2 |
    """
    if len(table_lines) < 2:
        return {"type": "paragraph", "text": ' '.join(table_lines)}

    def split_row(line: str) -> List[str]:
        # Strip leading/trailing pipe, splits op |, trim witruimte
        cells = line.split('|')
        # Verwijder lege eerste en laatste element (van leading/trailing |)
        if cells and not cells[0].strip():
            cells = cells[1:]
        if cells and not cells[-1].strip():
            cells = cells[:-1]
        return [cell.strip() for cell in cells]

    headers = split_row(table_lines[0])

    # Bepaal of rij 2 een separator is (|---|---|)
    start_row = 1
    if len(table_lines) > 1 and re.match(r'^[\s|:-]+$', table_lines[1]):
        start_row = 2

    rows = []
    for line in table_lines[start_row:]:
        cells = split_row(line)
        rows.append(cells)

    return {
        "type": "table",
        "headers": headers,
        "rows": rows,
    }


def preprocess_figure_blocks(lines: List[str]) -> List[str]:
    """
    Normaliseer figuurblokken: merge **Figuur N**, *caption* en ![...](path)
    tot één ![caption](path) regel, ongeacht de volgorde.

    Herkende patronen:
    1. ![](path) → **Figuur N** → *caption*
    2. **Figuur N** → *caption* → ![](path)
    3. ***Figuur N*** → *caption* → ![](path)

    Output altijd: ![caption](path)
    """
    _fig_line = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$')
    _bold_figuur = re.compile(r'^\*{2,3}Figuur\s+\d+\.?\*{2,3}\s*$')
    _italic_caption = re.compile(r'^\*([^*].+[^*])\*\s*$|^\*([^*]+)\*\s*$')

    result: List[str] = []
    i = 0
    while i < len(lines):
        m = _fig_line.match(lines[i])
        if m:
            # Patroon 1: ![](path) komt eerst
            existing_caption = m.group(1)
            path = m.group(2)
            caption = existing_caption
            j = i + 1

            # Sla lege regels over
            while j < len(lines) and not lines[j].strip():
                j += 1

            # Optionele **Figuur N** regel overslaan
            if j < len(lines) and _bold_figuur.match(lines[j].strip()):
                j += 1
                # Sla lege regels over
                while j < len(lines) and not lines[j].strip():
                    j += 1
                # Optionele *caption* regel opnemen als caption
                if j < len(lines):
                    cm = _italic_caption.match(lines[j].strip())
                    if cm:
                        caption = (cm.group(1) or cm.group(2) or '').strip()
                        j += 1

            result.append(f'![{caption}]({path})')
            i = j
        elif _bold_figuur.match(lines[i].strip()):
            # Patroon 2: **Figuur N** komt eerst — zoek *caption* en ![](path)
            j = i + 1
            caption = ''

            # Sla lege regels over
            while j < len(lines) and not lines[j].strip():
                j += 1

            # Optionele *caption* regel
            if j < len(lines):
                cm = _italic_caption.match(lines[j].strip())
                if cm:
                    caption = (cm.group(1) or cm.group(2) or '').strip()
                    j += 1
                    # Sla lege regels over
                    while j < len(lines) and not lines[j].strip():
                        j += 1

            # Zoek de ![](path) regel
            if j < len(lines):
                fm = _fig_line.match(lines[j])
                if fm:
                    path = fm.group(2)
                    if not caption:
                        caption = fm.group(1)
                    result.append(f'![{caption}]({path})')
                    i = j + 1
                    continue

            # Geen ![](path) gevonden — bewaar originele regels
            result.append(lines[i])
            i += 1
        else:
            result.append(lines[i])
            i += 1
    return result


# Patroon voor de inhoudsopgave-placeholder
_TOC_PLACEHOLDER = re.compile(r'^\[inhoudsopgave\b', re.IGNORECASE)
# Koppen die niet naar de body mogen (al aangemaakt door word_export.py)
_SKIP_HEADINGS = re.compile(r'^(inhoudsopgave|table of contents)$', re.IGNORECASE)


def _parse_appendix_lines(raw_lines: List[str], title: str = "") -> List[Dict]:
    """
    Converteer ruwe regels (van een bijlage-sectie) naar content-blokken.
    Ondersteunt fenced code blocks (```), koppen (#), tabellen (|) en alinea's.

    Uitzondering: bijlagen over AI-prompts (title bevat "ai" of "prompt", case-insensitive)
    behandelen code fences als gewone tekst — AI-prompttekst hoort niet in Code Snippet.
    """
    content: List[Dict] = []
    in_fence = False
    fence_lines: List[str] = []
    para_buffer: List[str] = []
    # Bijlage over AI-prompts: code fences worden genegeerd (inhoud als alinea's).
    # Controleer de heading-titel; als die leeg is, scan de eerste paar content-regels
    # (bijv. als titel op een aparte bold-paragraaf staat: "**Gebruikte AI-prompts**").
    _ai_search_text = title
    if not _ai_search_text:
        _ai_search_text = ' '.join(l.strip() for l in raw_lines[:5] if l.strip())
    is_ai_prompts = bool(re.search(r'\bai\b|prompt', _ai_search_text, re.IGNORECASE))

    def flush_para():
        if para_buffer:
            combined = ' '.join(para_buffer).strip()
            if combined:
                content.append({"type": "paragraph", "text": combined})
            para_buffer.clear()

    def close_fence():
        nonlocal in_fence, fence_lines
        content.append({"type": "code", "tekst": "\n".join(fence_lines)})
        fence_lines = []
        in_fence = False

    for raw in raw_lines:
        line = raw.rstrip()

        if line.strip().startswith("```"):
            if is_ai_prompts:
                continue  # negeer code fences in AI-prompt bijlage
            if not in_fence:
                flush_para()
                in_fence = True
                fence_lines = []
            else:
                close_fence()
            continue

        if in_fence:
            fence_lines.append(line)
            continue

        if not line.strip():
            flush_para()
            continue

        heading_match = re.match(r'^(#{1,4})\s+(.+)', line)
        if heading_match:
            heading_text = heading_match.group(2)
            # Bewaar nmap/tool commentaarregels (# Nmap...) als gewone tekst, niet als koptitel
            if _NMAP_COMMENT_RE.match(heading_text):
                para_buffer.append(line)
                continue
            flush_para()
            level = len(heading_match.group(1))
            text = strip_inline(heading_text)
            content.append({"type": "heading", "level": level, "text": text})
            continue

        para_buffer.append(line)

    flush_para()
    if in_fence and fence_lines:
        close_fence()

    return content


def parse_markdown(text: str) -> Tuple[Optional[str], List[Dict], List[str], Dict[str, str], List[Dict]]:
    """
    Parset markdown naar:
    - title (str|None): fallback-titel uit eerste H1 (alleen als geen front matter)
    - blocks (list[dict]): word_export.py blokken voor 'body'
    - references (list[str]): APA-bronnenregels (met inline markdown bewaard)
    - front_matter_meta (dict): metadata uit front matter
    - appendices (list[dict]): bijlagen-structuur voor word_export.py
    """
    lines = text.splitlines()
    # Pre-verwerk figuurblokken: merge **Figuur N** / *caption* regels
    lines = preprocess_figure_blocks(lines)

    # Stap 1: extraheer front matter
    front_matter_meta, start_idx = extract_front_matter(lines)
    has_front_matter = bool(front_matter_meta)

    title = None       # type: Optional[str]
    blocks = []        # type: List[Dict]
    references = []    # type: List[str]
    in_references = False
    paragraph_buffer = []  # type: List[str]
    table_buffer = []  # type: List[str]
    quote_buffer = []  # type: List[str]
    figure_counter = 0

    # Fenced code block state (main body)
    in_code_block = False
    code_block_lines: List[str] = []

    # Bijlagen state
    in_appendix_section = False
    appendices_raw: List[tuple] = []   # (label, title, [raw_lines])
    current_appendix_label: Optional[str] = None
    current_appendix_title: str = ""
    current_appendix_lines: List[str] = []

    def save_current_appendix():
        if current_appendix_label:
            appendices_raw.append((
                current_appendix_label,
                current_appendix_title,
                list(current_appendix_lines),
            ))

    def start_new_appendix(label: str, title: str):
        nonlocal current_appendix_label, current_appendix_title, current_appendix_lines
        save_current_appendix()
        current_appendix_label = label
        current_appendix_title = title
        current_appendix_lines = []

    def flush_paragraph():
        if paragraph_buffer:
            combined = ' '.join(paragraph_buffer).strip()
            # Sla inhoudsopgave-placeholders over (worden automatisch gegenereerd)
            if combined and not _TOC_PLACEHOLDER.match(combined):
                blocks.append({"type": "paragraph", "text": combined})
            paragraph_buffer.clear()

    def flush_table():
        if table_buffer:
            blocks.append(parse_table_lines(table_buffer[:]))
            table_buffer.clear()

    def flush_quote():
        if quote_buffer:
            combined = ' '.join(quote_buffer).strip()
            if combined:
                # Detecteer bronvermelding aan het einde: (Auteur, jaar) of (Auteur, jaar, p. X)
                citation = ""
                citation_match = re.search(r'\(([^)]+,\s*\d{4}[^)]*)\)\s*\.?\s*$', combined)
                if citation_match:
                    citation = f"({citation_match.group(1)})"
                    combined = combined[:citation_match.start()].strip()
                blocks.append({"type": "block_quote", "text": combined, "citation": citation})
            quote_buffer.clear()

    for line in lines[start_idx:]:
        raw = line.rstrip()

        # ── Fenced code block (``` ... ```) — verwerking vóór alle andere checks ──
        if raw.strip().startswith('```'):
            if in_appendix_section:
                # Bijlagen: sla ruwe regel op — _parse_appendix_lines handelt de ``` af
                current_appendix_lines.append(raw)
            elif not in_code_block:
                flush_paragraph()
                flush_table()
                flush_quote()
                in_code_block = True
                code_block_lines = []
            else:
                in_code_block = False
                blocks.append({"type": "code", "tekst": "\n".join(code_block_lines)})
                code_block_lines = []
            continue

        # Regels binnen een code block gaan rechtstreeks naar de buffer
        if in_code_block:
            code_block_lines.append(raw)
            continue

        # ── Bijlagen-sectie ──
        if in_appendix_section:
            # Nieuwe bijlage-kop: ## Bijlage A: Titel  OF  Bijlage A: Titel (plain)
            m = _BIJLAGE_ITEM.match(raw.strip()) or _BIJLAGE_PLAIN.match(raw.strip())
            if m:
                start_new_appendix(
                    label=m.group(1).strip(),
                    title=(m.group(2) or "").strip(),
                )
            else:
                # Overige content: bewaar als ruwe regel (incl. lege regels)
                current_appendix_lines.append(raw)
            continue

        # ── Lege regel → alinea-scheiding ──
        if not raw.strip():
            if in_references:
                pass  # lege regels in bronnenlijst overslaan
            elif table_buffer:
                flush_table()
            elif quote_buffer:
                flush_quote()
            else:
                flush_paragraph()
            continue

        # ── Detecteer referentieblok-header ──
        if REFERENCES_HEADERS.match(raw):
            flush_paragraph()
            flush_table()
            flush_quote()
            in_references = True
            continue

        # ── Verwerk regels in referentieblok ──
        if in_references:
            # Overkoepelende Bijlagen-kop → schakel naar bijlagen-modus (met of zonder # prefix)
            if _BIJLAGEN_SECTION.match(raw.strip()) or _BIJLAGEN_PLAIN.match(raw.strip()):
                in_references = False
                in_appendix_section = True
                continue
            # Individuele bijlage-kop zonder voorafgaande # Bijlagen (met of zonder # prefix)
            m = _BIJLAGE_ITEM.match(raw.strip()) or _BIJLAGE_PLAIN.match(raw.strip())
            if m:
                in_references = False
                in_appendix_section = True
                start_new_appendix(
                    label=m.group(1).strip(),
                    title=(m.group(2) or "").strip(),
                )
                continue
            ref = raw.strip()
            if ref:
                references.append(ref)
            continue

        # Detecteer tabelregels (beginnen met |)
        if raw.strip().startswith('|'):
            flush_paragraph()
            flush_quote()
            table_buffer.append(raw.strip())
            continue

        # Multi-line tabelcel: als we in een tabel zitten en de regel is niet leeg,
        # plak de tekst aan de laatste tabelregel (cel-inhoud loopt door op volgende regel)
        if table_buffer and raw.strip():
            table_buffer[-1] = table_buffer[-1] + ' ' + raw.strip()
            continue

        # Als we in een tabel zaten maar lege regel of einde tabel, flush
        if table_buffer:
            flush_table()

        # Detecteer blokcitaten (beginnen met >)
        if raw.strip().startswith('> ') or raw.strip() == '>':
            flush_paragraph()
            flush_table()
            quote_text = raw.strip()
            if quote_text.startswith('> '):
                quote_text = quote_text[2:]
            else:
                quote_text = ''
            quote_buffer.append(quote_text)
            continue

        # Als we in een blokcitaat zaten maar deze regel is geen citaat, flush
        if quote_buffer:
            flush_quote()

        # Detecteer paginascheiding
        if re.match(r'^-{3,}$', raw):
            flush_paragraph()
            blocks.append({"type": "page_break"})
            continue

        # Detecteer figuren: ![caption](pad/naar/afbeelding.png)
        figure_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', raw)
        if figure_match:
            flush_paragraph()
            figure_counter += 1
            blocks.append({
                "type": "figure_placeholder",
                "number": figure_counter,
                "caption": figure_match.group(1),
                "image_path": figure_match.group(2),
            })
            continue

        # Detecteer lijstitems → behandel als alinea (bewaar inline markdown)
        list_match = re.match(r'^[-*]\s+(.+)', raw)
        if list_match:
            flush_paragraph()
            blocks.append({"type": "paragraph", "text": list_match.group(1)})
            continue

        numbered_match = re.match(r'^\d+\.\s+(.+)', raw)
        if numbered_match:
            flush_paragraph()
            blocks.append({"type": "paragraph", "text": numbered_match.group(1)})
            continue

        # Detecteer koppen
        heading_match = re.match(r'^(#{1,4})\s+(.+)', raw)
        if heading_match:
            flush_paragraph()
            level_md = len(heading_match.group(1))
            heading_text = strip_inline(heading_match.group(2))
            # Strip optioneel numeriek prefix (bijv. "1.", "3.1") uit kopnaam
            heading_text = _HEADING_NUMBER_PREFIX.sub('', heading_text).strip()

            # Sla Inhoudsopgave-koppen over: word_export.py genereert de TOC automatisch
            if _SKIP_HEADINGS.match(heading_text):
                continue

            if not has_front_matter and level_md == 1 and title is None:
                # Fallback: geen front matter, eerste H1 = documenttitel
                title = heading_text
            else:
                # Directe mapping: # → 1, ## → 2, ### → 3, #### → 4
                blocks.append({"type": "heading", "level": level_md, "text": heading_text})
            continue

        # ── Plain-text referentielijst-header (zonder # prefix) ──
        if _REFERENCES_PLAIN.match(raw.strip()):
            flush_paragraph()
            flush_table()
            flush_quote()
            in_references = True
            continue

        # ── Plain-text bijlagen-sectie (zonder # prefix) ──
        if _BIJLAGEN_PLAIN.match(raw.strip()):
            flush_paragraph()
            flush_table()
            flush_quote()
            in_references = False
            in_appendix_section = True
            continue

        # ── Plain-text individuele bijlage-kop (zonder # prefix) ──
        _bm = _BIJLAGE_PLAIN.match(raw.strip())
        if _bm:
            flush_paragraph()
            flush_table()
            flush_quote()
            in_references = False
            in_appendix_section = True
            start_new_appendix(
                label=_bm.group(1).strip(),
                title=(_bm.group(2) or "").strip(),
            )
            continue

        # ── Tabel-/figuurlabels: elk hun eigen alinea-blok (APA: label en caption apart) ──
        if _TABLE_LABEL_LINE.match(raw.strip()):
            flush_paragraph()
            blocks.append({"type": "paragraph", "text": raw.strip()})
            continue

        # Detecteer alinea die volledig uit één inline code-expressie bestaat: `cmd`
        # Bijv. `nmap -sn 10.120.1.0/24` op een eigen regel → Code Snippet blok
        inline_code_match = re.match(r'^`([^`]+)`\s*$', raw.strip())
        if inline_code_match:
            flush_paragraph()
            blocks.append({"type": "code", "tekst": inline_code_match.group(1)})
            continue

        # Gewone tekstregel → verzamel in buffer voor huidige alinea
        paragraph_buffer.append(raw)

    # Flush resterende buffers
    flush_paragraph()
    flush_table()
    flush_quote()
    # Sluit open code block af
    if in_code_block and code_block_lines:
        blocks.append({"type": "code", "tekst": "\n".join(code_block_lines)})
    # Sla laatste bijlage op
    save_current_appendix()

    # Converteer ruwe bijlagen-regels naar blokken
    appendices: List[Dict] = []
    for label, app_title, raw_lines in appendices_raw:
        appendices.append({
            "label": label,
            "title": app_title,
            "content": _parse_appendix_lines(raw_lines, title=app_title),
        })

    return title, blocks, references, front_matter_meta, appendices


def build_payload(
    title: Optional[str],
    blocks: List[Dict],
    references: List[str],
    metadata_extra: dict,
    front_matter_meta: Optional[dict] = None,
    appendices: Optional[List[Dict]] = None,
):
    """Bouw het word_export.py JSON-payload. CLI --metadata overschrijft front matter."""
    fm = front_matter_meta or {}

    # Bepaal titel (prioriteit: CLI > front matter > eerste H1 > default)
    doc_title = (
        metadata_extra.get('titel')
        or fm.get('titel')
        or title
        or 'DutchQuill Export'
    )

    # Bouw metadata
    meta: dict = {"title": doc_title, "font": metadata_extra.get('font', 'times')}

    # Ondertitel
    subtitle = metadata_extra.get('ondertitel') or fm.get('ondertitel')
    if subtitle:
        meta["subtitle"] = subtitle

    # Auteur
    naam = (metadata_extra.get('naam') or fm.get('naam', '')).strip()
    if naam:
        meta["authors"] = [naam]

    # Studentnummer
    studentnummer = (metadata_extra.get('studentnummer') or fm.get('studentnummer', '')).strip()
    if studentnummer:
        meta["student_numbers"] = [studentnummer]

    # Instelling
    instelling = (metadata_extra.get('instelling') or fm.get('instelling', '')).strip()
    if instelling:
        meta["institution"] = instelling

    # Opleiding
    opleiding = (metadata_extra.get('opleiding') or fm.get('opleiding', '')).strip()
    if opleiding:
        meta["opleiding"] = opleiding

    # Vak (aparte regel onder opleiding, boven begeleider)
    vak = (metadata_extra.get('vak') or fm.get('vak', '')).strip()
    if vak:
        meta["course"] = vak

    # Begeleider / docent
    begeleider = (metadata_extra.get('begeleider') or fm.get('begeleider', '')).strip()
    if begeleider:
        meta["supervisor"] = begeleider

    # Datum
    datum = (metadata_extra.get('datum') or fm.get('datum', '')).strip()
    if datum:
        meta["submission_date"] = datum

    # Detecteer afkortingentabellen en verplaats naar abbreviations-payload
    abbreviations = []
    remaining_blocks = []
    _abbrev_headers = {'afkorting', 'afkortingen', 'abbreviation', 'abbreviations'}
    _def_headers = {'definitie', 'definities', 'definition', 'definitions', 'betekenis', 'omschrijving'}
    for block in blocks:
        if (block.get('type') == 'table'
                and len(block.get('headers', [])) == 2
                and block['headers'][0].strip().lower() in _abbrev_headers
                and block['headers'][1].strip().lower() in _def_headers):
            for row in block.get('rows', []):
                if len(row) >= 2:
                    abbreviations.append({
                        "afkorting": strip_inline(row[0]),
                        "definitie": strip_inline(row[1]),
                    })
            # Verwijder ook de heading die er direct boven staat
            if (remaining_blocks
                    and remaining_blocks[-1].get('type') == 'heading'
                    and 'afkorting' in remaining_blocks[-1].get('text', '').lower()):
                remaining_blocks.pop()
        else:
            remaining_blocks.append(block)

    # Detectie 2: bold+tab formaat onder afkortingen-heading
    # Herkent regels als: **ABBR**\tDefinitie (vet afkorting gevolgd door tab en definitie)
    # Ook plain-text: ABBR\tDefinitie (plain tekst met tabs, zoals geëxtraheerd uit .docx)
    if not abbreviations:
        # Gebruik finditer (niet match) zodat ook space-joined paragrafen met meerdere
        # afkortingen op één regel correct worden gesplitst.
        _bold_tab_re = re.compile(
            r'\*\*([A-Z][A-Za-z0-9/.\-]*)\*\*\s*\t+([^*]+?)(?=\s*\*\*[A-Z]|$)'
        )
        # Plain-text afkorting+tab patroon: ABBR (1-10 tekens, hoofdletters/cijfers)
        # gevolgd door één of meer tabs en een definitie.
        # Herkent ook de vorm waarbij de afkorting gevolgd door spaties+tab staat.
        _plain_tab_re = re.compile(
            r'^([A-Z][A-Za-z0-9/.\-]{0,9})\s*\t+(.+)$'
        )
        collecting = False
        abbrev_blocks_to_remove = set()
        abbrev_heading_idx = None
        for idx, block in enumerate(remaining_blocks):
            if block.get('type') == 'heading':
                txt = block.get('text', '').strip().lower()
                if any(k in txt for k in ('afkorting', 'abbreviat')):
                    collecting = True
                    abbrev_heading_idx = idx
                    continue
                elif collecting:
                    break
            if collecting and block.get('type') == 'paragraph':
                text_val = block.get('text', '')
                # Probeer eerst bold+tab formaat
                found = list(_bold_tab_re.finditer(text_val))
                if found:
                    for fm in found:
                        abbreviations.append({
                            "afkorting": fm.group(1),
                            "definitie": fm.group(2).strip(),
                        })
                    abbrev_blocks_to_remove.add(idx)
                else:
                    # Probeer plain-text tab formaat: elke alinea kan één afkorting zijn
                    # OF meerdere afkortingen samengevloten door paragraph_buffer (ruimte+tab)
                    # Splits op de scheiding tussen afkortingen door te zoeken op tabs
                    pm = _plain_tab_re.match(text_val.strip())
                    if pm:
                        abbreviations.append({
                            "afkorting": pm.group(1).strip(),
                            "definitie": pm.group(2).strip(),
                        })
                        abbrev_blocks_to_remove.add(idx)
        if abbreviations:
            if abbrev_heading_idx is not None:
                abbrev_blocks_to_remove.add(abbrev_heading_idx)
            remaining_blocks = [
                b for i, b in enumerate(remaining_blocks)
                if i not in abbrev_blocks_to_remove
            ]

    blocks = remaining_blocks

    # Extraheer samenvatting, inleiding en conclusie uit body-blocks
    abstract_data, intro_blocks, body_blocks, conclusion_blocks = extract_sections(blocks)

    payload = {
        "metadata": meta,
        "introduction_text": intro_blocks,
        "body": body_blocks,
        "conclusion_text": conclusion_blocks,
        "references": references,
    }

    if abstract_data:
        payload["abstract"] = abstract_data
    if abbreviations:
        payload["abbreviations"] = abbreviations
    if appendices:
        payload["appendices"] = appendices

    return payload


def main():
    parser = argparse.ArgumentParser(
        description='Converteer markdown/plain-text naar APA .docx via word_export.py'
    )
    parser.add_argument('--input', required=True, help='Pad naar het invoerbestand (.txt of .md)')
    parser.add_argument('--output', help='Pad voor het uitvoer-.docx-bestand (optioneel)')
    parser.add_argument(
        '--metadata',
        default='{}',
        help='JSON-string met auteursvelden: naam, studentnummer, opleiding, instelling, titel, datum'
    )
    args = parser.parse_args()

    # Lees invoerbestand
    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Fout: invoerbestand niet gevonden: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, encoding='utf-8') as f:
        text = f.read()

    # Parse metadata JSON
    try:
        metadata_extra = json.loads(args.metadata)
    except json.JSONDecodeError as e:
        print(f"Fout: ongeldige metadata JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse markdown
    title, blocks, references, front_matter_meta, appendices = parse_markdown(text)

    # Bouw payload
    payload = build_payload(title, blocks, references, metadata_extra, front_matter_meta, appendices)

    # Bepaal output-pad
    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        base = os.path.splitext(input_path)[0]
        output_path = base + '.docx'

    # Schrijf tijdelijke payload naar /tmp
    ts = int(time.time() * 1000)
    tmp_payload = f'/tmp/dutchquill_payload_{ts}.json'
    try:
        with open(tmp_payload, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        # Bepaal pad naar word_export.py
        script_dir = os.path.dirname(os.path.abspath(__file__))
        word_export = os.path.join(script_dir, 'word_export.py')

        result = subprocess.run(
            [sys.executable, word_export, '--input', tmp_payload, '--output', output_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            sys.exit(1)

        print(output_path)

    finally:
        # Opruimen
        if os.path.exists(tmp_payload):
            os.remove(tmp_payload)


if __name__ == '__main__':
    main()
