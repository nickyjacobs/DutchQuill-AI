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

# Optioneel numeriek prefix in kopnamen (bijv. "1.", "3.1") — altijd verwijderen uit .docx
_HEADING_NUMBER_PREFIX = re.compile(r'^\d+\.?\d*\.?\s*')

# Samenvatting/abstract sectie
_ABSTRACT_HEADING = re.compile(r'^(samenvatting|abstract)\s*$', re.IGNORECASE)

# Labels die in front matter herkend worden
_FM_STUDENTNUMMER = re.compile(r'^Studentnummer:\s*(.+)', re.IGNORECASE)
_FM_OPLEIDING = re.compile(r'^Opleiding:\s*(.+)', re.IGNORECASE)
_FM_VAK = re.compile(r'^Vak(?:naam)?(?:\s*[-/]\s*\S+)?:\s*(.+)', re.IGNORECASE)
_FM_BEGELEIDER = re.compile(r'^(?:Begeleider|Docent|Examinator|Supervisor)s?:\s*(.+)', re.IGNORECASE)
_FM_DATUM = re.compile(r'^Datum:\s*(.+)', re.IGNORECASE)
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


def extract_front_matter(lines: List[str]) -> Tuple[Dict[str, str], int]:
    """
    Herkent titelpagina-metadata uit platte tekst vóór de eerste markdown heading.

    Returns:
        (front_matter_meta, first_heading_index)
        Als er geen herkenbare front matter is, is first_heading_index 0
        en front_matter_meta leeg.
    """
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

    meta: Dict[str, str] = {}
    consumed: set = set()  # indices van verwerkte regels

    # Pass 1: herken gelabelde velden
    for i, line in enumerate(fm_lines):
        m = _FM_STUDENTNUMMER.match(line)
        if m:
            meta['studentnummer'] = m.group(1).strip()
            consumed.add(i)
            # Auteur = vorige niet-verwerkte regel
            if i > 0 and (i - 1) not in consumed:
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

        # Instelling herkennen
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
                    r'^[\*_]?sleutelwoorden[\*_]?:\s*(.+)',
                    t, re.IGNORECASE
                )
                if kw_match:
                    keywords = [k.strip() for k in kw_match.group(1).split(',')]
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


def parse_markdown(text: str) -> Tuple[Optional[str], List[Dict], List[str], Dict[str, str]]:
    """
    Parset markdown naar:
    - title (str|None): fallback-titel uit eerste H1 (alleen als geen front matter)
    - blocks (list[dict]): word_export.py blokken voor 'body'
    - references (list[str]): APA-bronnenregels (met inline markdown bewaard)
    - front_matter_meta (dict): metadata uit front matter
    """
    lines = text.splitlines()

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

    def flush_paragraph():
        if paragraph_buffer:
            combined = ' '.join(paragraph_buffer).strip()
            if combined:
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

        # Lege regel → alinea-scheiding
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

        # Detecteer referentieblok-header
        if REFERENCES_HEADERS.match(raw):
            flush_paragraph()
            flush_table()
            flush_quote()
            in_references = True
            continue

        # Verwerk regels in referentieblok — bewaar inline markdown voor cursief
        if in_references:
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

        # Als we in een tabel zaten maar deze regel is geen tabelregel, flush
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

            if not has_front_matter and level_md == 1 and title is None:
                # Fallback: geen front matter, eerste H1 = documenttitel
                title = heading_text
            else:
                # Directe mapping: # → 1, ## → 2, ### → 3, #### → 4
                blocks.append({"type": "heading", "level": level_md, "text": heading_text})
            continue

        # Gewone tekstregel → verzamel in buffer voor huidige alinea
        paragraph_buffer.append(raw)

    # Flush resterende buffers
    flush_paragraph()
    flush_table()
    flush_quote()

    return title, blocks, references, front_matter_meta


def build_payload(
    title: Optional[str],
    blocks: List[Dict],
    references: List[str],
    metadata_extra: dict,
    front_matter_meta: Optional[dict] = None,
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
    title, blocks, references, front_matter_meta = parse_markdown(text)

    # Bouw payload
    payload = build_payload(title, blocks, references, metadata_extra, front_matter_meta)

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
