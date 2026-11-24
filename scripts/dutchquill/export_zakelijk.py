#!/usr/bin/env python3
"""
professional_export.py — Markdown naar professioneel .docx rapport

Twee modi:
  1. Standalone: genereert een eigen titelblad en opmaak
  2. Template: vult een bestaande .docx-template (huisstijl) met content

Gebruik (standalone):
    python3 tools/professional_export.py \\
        --input .tmp/rapport.md \\
        --output .tmp/rapport-professioneel/voorstel.docx \\
        --metadata '{"title":"Titel","author":"Naam","organization":"Org","date":"27 maart 2026"}'

Gebruik (template):
    python3 tools/professional_export.py \\
        --input .tmp/rapport.md \\
        --output .tmp/rapport-professioneel/voorstel.docx \\
        --template templates/huisstijl.docx \\
        --metadata '{"title":"Titel","author":"Naam","version":"1.0","date":"27-3-2026","ref":"1234","client":"Organisatie"}'

Metadata JSON-schema (standalone):
{
    "title": "Rapporttitel",                [VERPLICHT]
    "subtitle": "Ondertitel",
    "author": "Voornaam Achternaam",
    "role": "Functie",
    "organization": "Organisatienaam",
    "date": "27 maart 2026",
    "version": "1.0",
    "classification": "Intern — Vertrouwelijk",
    "audience": "Doelgroep",
    "font": "calibri",                      — "calibri" | "arial" | "times" (standaard: calibri)
    "accent_color": "2196F3"                — hex kleurcode zonder # (standaard: 2196F3)
}

Metadata JSON-schema (template):
{
    "title": "Rapporttitel",                [VERPLICHT]
    "doc_type": "Rapportage",               — documenttype op titelblad (standaard: Rapportage)
    "client": "Klantnaam",                  — "Bij:" veld op titelblad
    "author": "Voornaam Achternaam",
    "version": "1.0",
    "date": "27-3-2026",
    "ref": "Referentienummer"
}

Ondersteunde markdown-elementen:
    # Heading 1, ## Heading 2, ### Heading 3, #### Heading 4
    Paragrafen (met **vet** en *cursief* inline)
    - Ongeordende lijsten
    1. Geordende lijsten
    - [ ] Checklists (onafgevinkt)
    - [x] Checklists (afgevinkt)
    | Tabel | Kolom | (met header-rij en separator)
    > Blokcitaten
    ```code blokken```
    --- Horizontale lijn / pagina-einde
    ![caption](pad/naar/afbeelding.png)

Stdout bij succes: absoluut pad naar het gegenereerde .docx-bestand
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

# Stijlnamen in een huisstijl-template. Bestaat een naam niet, dan valt de export terug op de Word-standaard.
# In fase 5 komen deze uit de `stijlen:`-mapping in dutchquill.yaml.
HUISSTIJL = {
    "lijst_bullet": "List Bullet",
    "lijst_nummer": "List Number",
    "tabel": "Table Grid",
    "tabeltekst": "Normal",
    "code": "Code",
}


# ── Standaardwaarden ────────────────────────────────────────────────────────

DEFAULT_FONT = 'Calibri'
DEFAULT_ACCENT = '2196F3'
FONT_MAP = {
    'calibri': 'Calibri',
    'arial': 'Arial',
    'times': 'Times New Roman',
}


def hex_to_rgb(hex_color):
    """Converteer hex string (zonder #) naar RGBColor."""
    h = hex_color.lstrip('#')
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ── Markdown parser ─────────────────────────────────────────────────────────

def parse_markdown(text, strip_heading_numbers=False):
    """
    Parse markdown naar een lijst van blokken.
    Elk blok is een dict met 'type' en type-specifieke velden.

    strip_heading_numbers: verwijder leading nummers (bijv. "1.", "4.1", "10.2.3")
                           uit heading-tekst. Gebruik bij template-modus waar Word
                           automatisch nummert via Heading-stijlen.
    """
    blocks = []
    lines = text.split('\n')
    i = 0
    in_references = False

    # Patronen voor bronnen/referentie-secties
    _REF_HEADERS = re.compile(
        r'^(bronnen|bronnenlijst|literatuurlijst|referenties|referentielijst|sources|references)\s*$',
        re.IGNORECASE
    )

    while i < len(lines):
        line = lines[i]

        # Lege regel
        if not line.strip():
            i += 1
            continue

        # Code blok
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip sluitende ```
            blocks.append({'type': 'code', 'text': '\n'.join(code_lines), 'language': lang})
            continue

        # Heading
        heading_match = re.match(r'^(#{1,4})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            if strip_heading_numbers:
                heading_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', heading_text)
            # Detecteer bronnen/referentie-secties
            clean_text = re.sub(r'^\d+(\.\d+)*\.?\s+', '', heading_text)
            in_references = bool(_REF_HEADERS.match(clean_text))
            blocks.append({'type': 'heading', 'level': level, 'text': heading_text})
            i += 1
            continue

        # Horizontale lijn / pagina-einde
        if re.match(r'^---+\s*$', line):
            blocks.append({'type': 'page_break'})
            i += 1
            continue

        # Afbeelding
        img_match = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', line)
        if img_match:
            blocks.append({'type': 'image', 'caption': img_match.group(1), 'path': img_match.group(2)})
            i += 1
            continue

        # Tabel
        if '|' in line and i + 1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i + 1]):
            headers = [c.strip() for c in line.strip().strip('|').split('|')]
            i += 2  # skip header + separator
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                row = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(row)
                i += 1
            blocks.append({'type': 'table', 'headers': headers, 'rows': rows})
            continue

        # Blokcitaat
        if line.startswith('>'):
            quote_lines = []
            while i < len(lines) and lines[i].startswith('>'):
                quote_lines.append(lines[i].lstrip('>').strip())
                i += 1
            blocks.append({'type': 'blockquote', 'text': '\n'.join(quote_lines)})
            continue

        # Checklist
        check_match = re.match(r'^[-*]\s+\[([ xX])\]\s+(.+)$', line)
        if check_match:
            items = []
            while i < len(lines):
                cm = re.match(r'^[-*]\s+\[([ xX])\]\s+(.+)$', lines[i])
                if not cm:
                    break
                items.append({'checked': cm.group(1).lower() == 'x', 'text': cm.group(2).strip()})
                i += 1
            blocks.append({'type': 'checklist', 'items': items})
            continue

        # Ongeordende lijst (of bronnenlijst als in_references actief is)
        if re.match(r'^[-*]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^[-*]\s+', lines[i]):
                items.append(re.sub(r'^[-*]\s+', '', lines[i]).strip())
                i += 1
            if in_references:
                blocks.append({'type': 'reference_list', 'items': items})
            else:
                blocks.append({'type': 'ul', 'items': items})
            continue

        # Geordende lijst (of bronnenlijst als in_references actief is)
        if re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                items.append(re.sub(r'^\d+\.\s+', '', lines[i]).strip())
                i += 1
            if in_references:
                blocks.append({'type': 'reference_list', 'items': items})
            else:
                blocks.append({'type': 'ol', 'items': items})
            continue

        # Paragraaf (alles wat niet eerder gematcht is)
        para_lines = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') \
                and not lines[i].startswith('```') and not lines[i].startswith('>') \
                and not re.match(r'^---+\s*$', lines[i]) \
                and not re.match(r'^[-*]\s+\[', lines[i]) \
                and not re.match(r'^[-*]\s+', lines[i]) \
                and not re.match(r'^\d+\.\s+', lines[i]) \
                and not re.match(r'^!\[', lines[i]) \
                and not ('|' in lines[i] and i + 1 < len(lines) and
                         re.match(r'^[\s|:-]+$', lines[i + 1])):
            para_lines.append(lines[i])
            i += 1
        if para_lines:
            blocks.append({'type': 'paragraph', 'text': ' '.join(para_lines)})

    return blocks


# ── Inline formatting ────────────────────────────────────────────────────────

def add_formatted_text(paragraph, text, font_name, font_size, color=None):
    """Voeg tekst toe met **vet**, *cursief* en `code` inline formatting."""
    # Split op markdown inline patterns
    pattern = r'(\*\*.*?\*\*|\*.*?\*|`[^`]+`)'
    parts = re.split(pattern, text)

    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*'):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`'):
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(font_size - 1)
            # Lichtgrijze achtergrond voor inline code
            shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E8E8E8"/>')
            run._element.get_or_add_rPr().append(shading)
        else:
            run = paragraph.add_run(part)

        run.font.name = font_name
        if not (part.startswith('`') and part.endswith('`')):
            run.font.size = Pt(font_size)
        if color:
            run.font.color.rgb = color


# ── Document builder ─────────────────────────────────────────────────────────

def build_title_page(doc, metadata, font_name, accent_color):
    """Genereer een professioneel titelblad."""
    # Witruimte bovenaan
    for _ in range(4):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)

    # Accentlijn
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('━' * 40)
    run.font.color.rgb = accent_color
    run.font.size = Pt(14)
    run.font.name = font_name

    # Titel
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(24)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(metadata.get('title', 'Rapport'))
    run.font.name = font_name
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    run.bold = True

    # Ondertitel
    if metadata.get('subtitle'):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(4)
        run = p.add_run(metadata['subtitle'])
        run.font.name = font_name
        run.font.size = Pt(16)
        run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)

    # Accentlijn
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    run = p.add_run('━' * 40)
    run.font.color.rgb = accent_color
    run.font.size = Pt(14)
    run.font.name = font_name

    # Metadata-blok
    meta_items = []
    if metadata.get('author'):
        label = 'Auteur'
        if metadata.get('role'):
            meta_items.append(('Auteur', f"{metadata['author']}, {metadata['role']}"))
        else:
            meta_items.append(('Auteur', metadata['author']))
    if metadata.get('organization'):
        meta_items.append(('Organisatie', metadata['organization']))
    if metadata.get('date'):
        meta_items.append(('Datum', metadata['date']))
    if metadata.get('version'):
        meta_items.append(('Versie', metadata['version']))
    if metadata.get('classification'):
        meta_items.append(('Classificatie', metadata['classification']))
    if metadata.get('audience'):
        meta_items.append(('Doelgroep', metadata['audience']))

    if meta_items:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(36)

        for i, (label, value) in enumerate(meta_items):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)

            run = p.add_run(f'{label}: ')
            run.font.name = font_name
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)
            run.bold = True

            run = p.add_run(value)
            run.font.name = font_name
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)

    # Pagina-einde na titelblad
    doc.add_page_break()


def build_document(markdown_text, metadata, output_path):
    """Bouw het volledige professionele document."""
    font_name = FONT_MAP.get(metadata.get('font', 'calibri'), DEFAULT_FONT)
    accent_hex = metadata.get('accent_color', DEFAULT_ACCENT)
    accent_color = hex_to_rgb(accent_hex)
    accent_light = hex_to_rgb(_lighten(accent_hex, 0.85))

    doc = Document()

    # Documentmarges
    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

    # Standaard lettertype instellen
    style = doc.styles['Normal']
    style.font.name = font_name
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    # Titelblad
    build_title_page(doc, metadata, font_name, accent_color)

    # Content
    blocks = parse_markdown(markdown_text)
    table_counter = 0
    figure_counter = 0

    for block in blocks:
        btype = block['type']

        if btype == 'heading':
            level = block['level']
            p = doc.add_paragraph()

            if level == 1:
                p.paragraph_format.space_before = Pt(24)
                p.paragraph_format.space_after = Pt(12)
                run = p.add_run(block['text'])
                run.font.size = Pt(18)
                run.font.color.rgb = accent_color
                run.bold = True
                # Onderlijn
                p2 = doc.add_paragraph()
                p2.paragraph_format.space_before = Pt(0)
                p2.paragraph_format.space_after = Pt(12)
                run2 = p2.add_run('━' * 60)
                run2.font.size = Pt(8)
                run2.font.color.rgb = accent_light

            elif level == 2:
                p.paragraph_format.space_before = Pt(18)
                p.paragraph_format.space_after = Pt(8)
                run = p.add_run(block['text'])
                run.font.size = Pt(14)
                run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
                run.bold = True

            elif level == 3:
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
                run = p.add_run(block['text'])
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
                run.bold = True
                run.italic = True

            elif level == 4:
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(block['text'])
                run.font.size = Pt(11)
                run.font.color.rgb = accent_color
                run.bold = True

            run.font.name = font_name

        elif btype == 'paragraph':
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            add_formatted_text(p, block['text'], font_name, 11)

        elif btype == 'ul':
            for item in block['items']:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                run = p.add_run('•  ')
                run.font.name = font_name
                run.font.size = Pt(11)
                run.font.color.rgb = accent_color
                add_formatted_text(p, item, font_name, 11)

        elif btype == 'ol':
            for idx, item in enumerate(block['items'], 1):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                run = p.add_run(f'{idx}.  ')
                run.font.name = font_name
                run.font.size = Pt(11)
                run.font.color.rgb = accent_color
                run.bold = True
                add_formatted_text(p, item, font_name, 11)

        elif btype == 'reference_list':
            for item in block['items']:
                p = doc.add_paragraph()
                p.paragraph_format.first_line_indent = Cm(-1.27)
                p.paragraph_format.left_indent = Cm(1.27)
                p.paragraph_format.space_after = Pt(4)
                add_formatted_text(p, item, font_name, 11)

        elif btype == 'checklist':
            for item in block['items']:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(1)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(2)
                symbol = '☑' if item['checked'] else '☐'
                color = hex_to_rgb('4CAF50') if item['checked'] else RGBColor(0x5C, 0x6E, 0x8A)
                run = p.add_run(f'{symbol}  ')
                run.font.name = 'Segoe UI Symbol'
                run.font.size = Pt(12)
                run.font.color.rgb = color
                add_formatted_text(p, item['text'], font_name, 11)

        elif btype == 'table':
            table_counter += 1
            headers = block['headers']
            rows = block['rows']
            ncols = len(headers)

            table = doc.add_table(rows=1 + len(rows), cols=ncols)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.style = 'Table Grid'

            # Header-rij
            for j, header in enumerate(headers):
                cell = table.rows[0].cells[j]
                cell.text = ''
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                run = p.add_run(header)
                run.font.name = font_name
                run.font.size = Pt(10)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                # Achtergrondkleur header
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{accent_hex}"/>')
                cell._element.get_or_add_tcPr().append(shading)

            # Data-rijen
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    if j >= ncols:
                        break
                    cell = table.rows[i + 1].cells[j]
                    cell.text = ''
                    p = cell.paragraphs[0]
                    add_formatted_text(p, val, font_name, 10)
                    # Alternerend: lichte achtergrond
                    if i % 2 == 0:
                        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F5F7FA"/>')
                        cell._element.get_or_add_tcPr().append(shading)

            # Tabel-opmaak: dunne borders
            tbl = table._tbl
            tblPr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
            borders = parse_xml(
                f'<w:tblBorders {nsdecls("w")}>'
                f'  <w:top w:val="single" w:sz="4" w:color="D0D8E8"/>'
                f'  <w:left w:val="single" w:sz="4" w:color="D0D8E8"/>'
                f'  <w:bottom w:val="single" w:sz="4" w:color="D0D8E8"/>'
                f'  <w:right w:val="single" w:sz="4" w:color="D0D8E8"/>'
                f'  <w:insideH w:val="single" w:sz="4" w:color="D0D8E8"/>'
                f'  <w:insideV w:val="single" w:sz="4" w:color="D0D8E8"/>'
                f'</w:tblBorders>'
            )
            tblPr.append(borders)

            # Witruimte na tabel
            doc.add_paragraph().paragraph_format.space_after = Pt(6)

        elif btype == 'blockquote':
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(1.5)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(8)
            # Verticale accentlijn via border
            pPr = p._element.get_or_add_pPr()
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:left w:val="single" w:sz="18" w:color="{accent_hex}" w:space="8"/>'
                f'</w:pBdr>'
            )
            pPr.append(pBdr)
            run = p.add_run(block['text'])
            run.font.name = font_name
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)
            run.italic = True

        elif btype == 'code':
            for code_line in block['text'].split('\n'):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.5)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                # Achtergrond
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F0F2F5"/>')
                p._element.get_or_add_pPr().append(shading)
                run = p.add_run(code_line if code_line else ' ')
                run.font.name = 'Consolas'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x2E)
            # Witruimte na codeblok
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

        elif btype == 'image':
            figure_counter += 1
            img_path = block['path']
            if os.path.isfile(img_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(img_path, width=Cm(14))
            if block.get('caption'):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(12)
                run = p.add_run(f'Figuur {figure_counter}. ')
                run.font.name = font_name
                run.font.size = Pt(10)
                run.font.color.rgb = accent_color
                run.italic = True
                run = p.add_run(block['caption'])
                run.font.name = font_name
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)
                run.italic = True

        elif btype == 'page_break':
            doc.add_page_break()

    # Header en footer
    _add_header_footer(doc, metadata, font_name, accent_color)

    # Metadata opschonen (geen tool-fingerprints)
    _clean_metadata(doc, metadata)

    # Opslaan
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    print(os.path.abspath(output_path))


def _lighten(hex_color, factor=0.85):
    """Maak een kleur lichter (richting wit)."""
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r + (255 - r) * factor)
    g = int(g + (255 - g) * factor)
    b = int(b + (255 - b) * factor)
    return f'{r:02x}{g:02x}{b:02x}'


def _add_header_footer(doc, metadata, font_name, accent_color):
    """Voeg header en footer toe aan alle secties."""
    for section in doc.sections:
        section.different_first_page_header_footer = True

        # Header (niet op eerste pagina)
        header = section.header
        p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = p.add_run(metadata.get('title', ''))
        run.font.name = font_name
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)

        # Footer met paginanummering
        footer = section.footer
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)

        if metadata.get('classification'):
            run = p.add_run(f"{metadata['classification']}  |  ")
            run.font.name = font_name
            run.font.size = Pt(8)
            run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)

        # Paginanummer via field code
        run = p.add_run('Pagina ')
        run.font.name = font_name
        run.font.size = Pt(8)
        run.font.color.rgb = RGBColor(0x5C, 0x6E, 0x8A)

        fld_char_begin = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
        run._element.append(fld_char_begin)
        instr = parse_xml(f'<w:instrText {nsdecls("w")}> PAGE </w:instrText>')
        run._element.append(instr)
        fld_char_end = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
        run._element.append(fld_char_end)


def _clean_metadata(doc, metadata):
    """Verwijder tool-fingerprints uit documentmetadata."""
    core = doc.core_properties
    core.author = metadata.get('author', '')
    core.title = metadata.get('title', '')
    core.subject = metadata.get('subtitle', '')
    core.comments = ''
    core.keywords = ''
    core.category = metadata.get('classification', '')
    # Laat created/modified op de standaard python-docx waarden
    # (die worden als "vandaag" gezet, wat realistisch is)


# ── Template-modus ───────────────────────────────────────────────────────────

def _set_cell_text(cell, text):
    """Vervang tekst in een tabelcel, behoud de eerste run-opmaak."""
    for paragraph in cell.paragraphs:
        for run in paragraph.runs:
            if run.text.strip():
                run.text = text
                return
    # Fallback: geen bestaande runs met tekst gevonden
    if cell.paragraphs:
        cell.paragraphs[0].text = text


def _find_toc_paragraph(doc):
    """Vind de inhoudsopgave-paragraaf (toc 1 stijl of 'No table of contents')."""
    for i, p in enumerate(doc.paragraphs):
        if p.style and p.style.name.startswith('toc'):
            return i
        if 'table of contents' in p.text.lower():
            return i
    return None


def build_from_template(markdown_text, metadata, template_path, output_path):
    """Bouw document door een bestaande template te vullen met content."""
    doc = Document(template_path)

    # ── Stap 1: Metadata invullen op titelblad ──

    # Tabel 0: titelblad (6 rijen x 1 kolom)
    # [0] = logo area, [1] = doc_type, [2] = "Betreft:", [3] = titel, [4] = "Bij:", [5] = client
    if len(doc.tables) >= 1:
        t0 = doc.tables[0]
        if len(t0.rows) >= 6:
            doc_type = metadata.get('doc_type', 'Rapportage')
            title = metadata.get('title', '')
            client = metadata.get('client', metadata.get('organization', ''))

            # Documenttype (rij 1)
            _set_cell_text(t0.rows[1].cells[0], doc_type)
            # Titel (rij 3)
            _set_cell_text(t0.rows[3].cells[0], title)
            # Klantnaam (rij 5)
            _set_cell_text(t0.rows[5].cells[0], client)

    # Tabel 1: metadata (4 rijen x 2 kolommen)
    # [0] = Auteur(s), [1] = Versie, [2] = Datum, [3] = Referentienummer
    if len(doc.tables) >= 2:
        t1 = doc.tables[1]
        meta_map = {
            0: metadata.get('author', ''),
            1: metadata.get('version', '0.1'),
            2: metadata.get('date', ''),
            3: metadata.get('ref', ''),
        }
        for row_idx, value in meta_map.items():
            if row_idx < len(t1.rows) and value:
                _set_cell_text(t1.rows[row_idx].cells[1], value)

    # Tabel 2: Historie — eerste rij invullen
    if len(doc.tables) >= 3:
        t2 = doc.tables[2]
        if len(t2.rows) >= 2:
            # Rij 1 (na header): versie, datum, auteur, opmerkingen
            hist_data = [
                metadata.get('version', '0.1'),
                metadata.get('date', ''),
                metadata.get('author', ''),
                'Eerste versie',
            ]
            for j, val in enumerate(hist_data):
                if j < len(t2.rows[1].cells):
                    _set_cell_text(t2.rows[1].cells[j], val)

    # ── Stap 2: Content voorbereiden ──

    # Strip front matter (metadata-blok bovenaan het markdown-bestand)
    # Dit wordt al afgehandeld door het titelblad van de template
    lines = markdown_text.split('\n')
    content_start = 0
    for i, line in enumerate(lines):
        # Zoek de eerste echte heading (## of hoger) die na de metadata komt
        if line.startswith('## ') and i > 1:
            # Skip ook de inhoudsopgave-sectie als die er is
            if 'inhoudsopgave' in line.lower():
                # Zoek het einde van de inhoudsopgave (volgende ## of ---)
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('## ') or lines[j].strip() == '---':
                        content_start = j
                        if lines[j].strip() == '---':
                            content_start = j + 1  # skip de ---
                        break
                break
            else:
                content_start = i
                break
        elif line.startswith('# ') and i > 0:
            # Skip de titel-heading (al op titelblad)
            continue

    # Verwijder alles voor de eerste echte content-sectie
    if content_start > 0:
        markdown_text = '\n'.join(lines[content_start:])

    blocks = parse_markdown(markdown_text, strip_heading_numbers=True)

    # Zoek het invoegpunt: na de laatste boilerplate-paragraaf
    # De inhoudsopgave staat in sectie 2, daarna komt de content
    # We voegen toe aan het einde van het document (na alle boilerplate)
    body = doc.element.body

    # Bepaal de stijlen die beschikbaar zijn in de template
    available_styles = {s.name for s in doc.styles}

    def _get_style(name, fallback='Normal'):
        return name if name in available_styles else fallback

    figure_counter = 0

    for block in blocks:
        btype = block['type']

        if btype == 'heading':
            level = block['level']
            style_name = _get_style(f'Heading {level}')
            p = doc.add_paragraph(block['text'], style=style_name)

        elif btype == 'paragraph':
            p = doc.add_paragraph(style=_get_style('Normal'))
            add_formatted_text(p, block['text'], None, 11)

        elif btype == 'ul':
            style = _get_style(HUISSTIJL['lijst_bullet'], 'List Bullet')
            for item in block['items']:
                p = doc.add_paragraph(style=style)
                add_formatted_text(p, item, None, 11)

        elif btype == 'ol':
            style = _get_style(HUISSTIJL['lijst_nummer'], 'List Number')
            for item in block['items']:
                p = doc.add_paragraph(style=style)
                add_formatted_text(p, item, None, 11)

        elif btype == 'reference_list':
            for item in block['items']:
                p = doc.add_paragraph(style=_get_style('Normal'))
                p.paragraph_format.first_line_indent = Cm(-1.27)
                p.paragraph_format.left_indent = Cm(1.27)
                p.paragraph_format.space_after = Pt(4)
                add_formatted_text(p, item, None, 11)

        elif btype == 'checklist':
            for item in block['items']:
                p = doc.add_paragraph(style=_get_style('Normal'))
                symbol = '☑' if item['checked'] else '☐'
                run = p.add_run(f'{symbol}  ')
                run.font.size = Pt(12)
                add_formatted_text(p, item['text'], None, 11)

        elif btype == 'table':
            headers = block['headers']
            rows = block['rows']
            ncols = len(headers)

            # Gebruik de tabelstijl van de template als die er is
            table_style = _get_style(HUISSTIJL['tabel'], 'Table Grid')
            table = doc.add_table(rows=1 + len(rows), cols=ncols)
            try:
                table.style = table_style
            except KeyError:
                table.style = 'Table Grid'
            table.alignment = WD_TABLE_ALIGNMENT.CENTER

            # Headers
            for j, header in enumerate(headers):
                cell = table.rows[0].cells[j]
                cell.text = ''
                p = cell.paragraphs[0]
                try:
                    p.style = doc.styles[_get_style(HUISSTIJL['tabeltekst'])]
                except KeyError:
                    pass
                run = p.add_run(header)
                run.font.bold = True
                run.font.size = Pt(10)

            # Data
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    if j >= ncols:
                        break
                    cell = table.rows[i + 1].cells[j]
                    cell.text = ''
                    p = cell.paragraphs[0]
                    try:
                        p.style = doc.styles[_get_style(HUISSTIJL['tabeltekst'])]
                    except KeyError:
                        pass
                    add_formatted_text(p, val, None, 10)

            doc.add_paragraph()  # witruimte

        elif btype == 'blockquote':
            p = doc.add_paragraph(style=_get_style('Normal'))
            p.paragraph_format.left_indent = Cm(1.5)
            pPr = p._element.get_or_add_pPr()
            pBdr = parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'  <w:left w:val="single" w:sz="18" w:color="262262" w:space="8"/>'
                f'</w:pBdr>'
            )
            pPr.append(pBdr)
            run = p.add_run(block['text'])
            run.font.size = Pt(11)
            run.italic = True

        elif btype == 'code':
            code_style = _get_style(HUISSTIJL['code'], 'Normal')
            for code_line in block['text'].split('\n'):
                p = doc.add_paragraph(style=code_style)
                if code_style == 'Normal':
                    # Fallback styling als de codestijl niet beschikbaar is
                    run = p.add_run(code_line if code_line else ' ')
                    run.font.name = 'Courier New'
                    run.font.size = Pt(9)
                else:
                    p.add_run(code_line if code_line else ' ')
            doc.add_paragraph()

        elif btype == 'image':
            figure_counter += 1
            img_path = block['path']
            if os.path.isfile(img_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run()
                run.add_picture(img_path, width=Cm(14))
            if block.get('caption'):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(f'Figuur {figure_counter}. {block["caption"]}')
                run.font.size = Pt(10)
                run.italic = True

        elif btype == 'page_break':
            doc.add_page_break()

    # Metadata opschonen
    _clean_metadata(doc, metadata)

    # Opslaan
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    print(os.path.abspath(output_path))


# ── CLI ──────────────────────────────────────────────────────────────────────

def _load_professional_profile():
    """Laad config/user_profile.json professionele sectie als fallback."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    profile_path = os.path.join(project_root, 'config', 'user_profile.json')
    if not os.path.exists(profile_path):
        return {}
    try:
        with open(profile_path, encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
    prof = data.get('professioneel', {})
    if not prof:
        return {}
    result = {}
    if prof.get('naam'):
        result['author'] = prof['naam']
    if prof.get('functie'):
        result['role'] = prof['functie']
    if prof.get('organisatie'):
        result['organization'] = prof['organisatie']
    return result


def _resolve_template_path(template_arg):
    """Los template-pad op: relatief naar project root of absoluut."""
    if os.path.isabs(template_arg) and os.path.isfile(template_arg):
        return template_arg
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(project_root, template_arg)
    if os.path.isfile(candidate):
        return candidate
    return template_arg  # laat het falen met een duidelijke foutmelding


def main():
    parser = argparse.ArgumentParser(description='Genereer professioneel .docx rapport')
    parser.add_argument('--input', required=True, help='Pad naar markdown-bestand')
    parser.add_argument('--output', required=True, help='Pad voor het gegenereerde .docx-bestand')
    parser.add_argument('--metadata', default='{}',
                        help='JSON-string of pad naar JSON-bestand met metadata')
    parser.add_argument('--template', default=None,
                        help='Pad naar .docx-template (bijv. templates/huisstijl.docx)')
    args = parser.parse_args()

    # Input lezen
    with open(args.input, encoding='utf-8') as f:
        markdown_text = f.read()

    # Metadata laden
    if os.path.isfile(args.metadata):
        with open(args.metadata, encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = json.loads(args.metadata)

    # Profiel als fallback
    profile_defaults = _load_professional_profile()
    for key, val in profile_defaults.items():
        if key not in metadata:
            metadata[key] = val

    # Datum fallback
    if 'date' not in metadata:
        metadata['date'] = datetime.now().strftime('%-d %B %Y')

    # Bouwen: template of standalone
    if args.template:
        template_path = _resolve_template_path(args.template)
        build_from_template(markdown_text, metadata, template_path, args.output)
    else:
        build_document(markdown_text, metadata, args.output)


if __name__ == '__main__':
    main()
