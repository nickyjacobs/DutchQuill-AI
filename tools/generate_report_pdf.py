#!/usr/bin/env python3
"""
generate_report_pdf.py — Humaniseringsanalyse rapport als clean PDF

Gebruik:
    python3 tools/generate_report_pdf.py \
        --risico hoog \
        --patronen 18 \
        --flesch 13.0 \
        --ttr 0.83 \
        --bestandsnaam "apa_rapport_3.docx" \
        --niveau1 "in toenemende mate|steeds meer||optimaliseren|verbeteren||inzichten|bevindingen" \
        --waarschuwingen "Flesch-Douma: 13.0 — Zeer moeilijk|Passieve zinnen: 29.7%|Type 2b frames: 3x" \
        --aanbevelingen "Breek lange zinnen op (max. 18–20 woorden)|Vervang vage openers|Zet passieve zinnen om naar actief" \
        --chart-base64 <base64_png> \
        --output .tmp/humaniseer_rapport.pdf

Stdout bij succes: absoluut pad naar het gegenereerde .pdf-bestand
"""

import argparse
import base64
import io
import os
import sys
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Kleurenpalet ─────────────────────────────────────────────────────────────
C_BG       = colors.HexColor('#FFFFFF')
C_DARK     = colors.HexColor('#0A0E1A')
C_PANEL    = colors.HexColor('#F5F7FA')
C_BORDER   = colors.HexColor('#E0E5EE')
C_TEXT     = colors.HexColor('#1A2140')
C_DIM      = colors.HexColor('#5C6E8A')
C_ACCENT   = colors.HexColor('#FF6820')
C_GREEN    = colors.HexColor('#1A9E5B')
C_AMBER    = colors.HexColor('#C8860A')
C_RED      = colors.HexColor('#C0392B')
C_RULE     = colors.HexColor('#D0D8E8')

# ── Risicokleuren ─────────────────────────────────────────────────────────────
def risico_color(risico: str):
    return {'laag': C_GREEN, 'gemiddeld': C_AMBER, 'hoog': C_RED}.get(risico.lower(), C_AMBER)


def hex_str(c) -> str:
    """Geeft een '#rrggbb' string terug voor gebruik in ReportLab Paragraph-markup."""
    return '#{:02x}{:02x}{:02x}'.format(
        int(c.red * 255), int(c.green * 255), int(c.blue * 255)
    )

def risico_label(risico: str) -> str:
    return {
        'laag':      'Laag risico — Tekst klinkt menselijk',
        'gemiddeld': 'Gemiddeld risico — Licht AI-aangeraakt',
        'hoog':      'Hoog risico — Sterk AI-achtig',
    }.get(risico.lower(), risico.capitalize())

def risico_advies(risico: str) -> str:
    return {
        'laag':      'De tekst ziet er goed uit. Kleine aanpassingen zijn optioneel.',
        'gemiddeld': 'Herschrijf de vermelde alinea\'s. Gebruik /herschrijven voor gerichte verbetering.',
        'hoog':      'De tekst vereist dringende herziening. Start /herschrijven voor een volledige aanpak.',
    }.get(risico.lower(), '')


def build_styles():
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        'DQTitle',
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=C_DARK,
        spaceAfter=2 * mm,
    )
    subtitle = ParagraphStyle(
        'DQSubtitle',
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=C_DIM,
        spaceAfter=0,
    )
    section_header = ParagraphStyle(
        'DQSectionHeader',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=C_DARK,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
        borderPadding=(0, 0, 2, 0),
    )
    body = ParagraphStyle(
        'DQBody',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=C_TEXT,
        spaceAfter=2 * mm,
    )
    label = ParagraphStyle(
        'DQLabel',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=C_DIM,
        spaceAfter=1 * mm,
    )
    patroon_woord = ParagraphStyle(
        'DQPatroon',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=C_TEXT,
    )
    alt_woord = ParagraphStyle(
        'DQAlt',
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=C_DIM,
    )
    warn_text = ParagraphStyle(
        'DQWarn',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=C_TEXT,
        leftIndent=4,
    )
    advies = ParagraphStyle(
        'DQAdvies',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=C_TEXT,
    )
    footer = ParagraphStyle(
        'DQFooter',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=C_DIM,
        alignment=TA_CENTER,
    )

    return {
        'title': title,
        'subtitle': subtitle,
        'section_header': section_header,
        'body': body,
        'label': label,
        'patroon': patroon_woord,
        'alt': alt_woord,
        'warn': warn_text,
        'advies': advies,
        'footer': footer,
    }


def hr(color=C_RULE, width=1):
    return HRFlowable(width='100%', thickness=width, color=color, spaceAfter=4 * mm, spaceBefore=0)


def header_badge(risico: str, patronen: int, s):
    """Genereer een samenvatting-badge bovenaan als tabel."""
    rc = risico_color(risico)
    label = risico_label(risico)

    data = [[
        Paragraph(f'<font color="{hex_str(rc)}" size="11"><b>{patronen} patronen</b></font>', s['title']),
        Paragraph(f'<b>{label}</b>', ParagraphStyle(
            'badge_label',
            fontName='Helvetica-Bold',
            fontSize=10,
            leading=14,
            textColor=rc,
        )),
    ]]

    tbl = Table(data, colWidths=['25%', '75%'])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_PANEL),
        ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return tbl


def niveau1_tabel(items: list, s) -> Table:
    """
    items = lijst van tuples: (patroon, alternatief, context_snippet)
    """
    rows = []
    for i, (patroon, alternatief, _context) in enumerate(items):
        bg = C_PANEL if i % 2 == 0 else C_BG
        rows.append([
            Paragraph(f'"{patroon}"', s['patroon']),
            Paragraph(f'→ <i>{alternatief}</i>', s['alt']),
        ])

    tbl = Table(rows, colWidths=['45%', '55%'])
    style = [
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (0, -1), 12),
        ('LEFTPADDING', (1, 0), (1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.4, C_BORDER),
        ('BACKGROUND', (0, 0), (-1, 0), C_PANEL),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [C_PANEL, C_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]
    # Markeer de linkerkolom
    for i in range(len(rows)):
        style.append(('LINEAFTER', (0, i), (0, i), 0.5, C_BORDER))
    tbl.setStyle(TableStyle(style))
    return tbl


def waarschuwingen_tabel(items: list, s) -> Table:
    rows = []
    for item in items:
        rows.append([
            Paragraph('⚠', ParagraphStyle('icon', fontName='Helvetica', fontSize=9, textColor=C_AMBER)),
            Paragraph(item, s['warn']),
        ])

    tbl = Table(rows, colWidths=['5%', '95%'])
    tbl.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (0, -1), 8),
        ('LEFTPADDING', (1, 0), (1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, C_BORDER),
    ]))
    return tbl


def aanbevelingen_tabel(items: list, risico: str, s) -> Table:
    rc = risico_color(risico)
    rows = []
    for i, item in enumerate(items, start=1):
        rows.append([
            Paragraph(f'<font color="{hex_str(rc)}"><b>{i}</b></font>', ParagraphStyle(
                'nr', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=rc,
                alignment=TA_CENTER,
            )),
            Paragraph(item, s['advies']),
        ])

    tbl = Table(rows, colWidths=['8%', '92%'])
    tbl.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (0, -1), 4),
        ('LEFTPADDING', (1, 0), (1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, C_BORDER),
    ]))
    return tbl


def generate_pdf(
    output_path: str,
    risico: str,
    patronen: int,
    flesch: float,
    ttr: float,
    bestandsnaam: str,
    niveau1_items: list,
    waarschuwingen: list,
    aanbevelingen: list,
    chart_base64: str = '',
) -> str:
    """Genereer het PDF-rapport. Geeft het absoluut pad terug."""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2.0 * cm,
        title='Humaniseringsanalyse — DutchQuill AI',
        author='DutchQuill AI',
    )

    s = build_styles()
    story = []
    rc = risico_color(risico)
    vandaag = date.today().strftime('%d %B %Y').lstrip('0')

    # ── Header ─────────────────────────────────────────────────────────────────
    story.append(Paragraph('HUMANISERINGSANALYSE', ParagraphStyle(
        'rapporttitel',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=C_ACCENT,
        spaceAfter=1 * mm,
    )))
    story.append(Paragraph(bestandsnaam or 'Tekst zonder bestandsnaam', s['title']))
    story.append(Paragraph(f'DutchQuill AI &nbsp;·&nbsp; {vandaag}', s['subtitle']))
    story.append(Spacer(1, 4 * mm))
    story.append(hr(C_ACCENT, 1.5))

    # ── Risico-badge ───────────────────────────────────────────────────────────
    story.append(header_badge(risico, patronen, s))
    story.append(Spacer(1, 5 * mm))

    # ── Reviewchart ────────────────────────────────────────────────────────────
    if chart_base64:
        try:
            img_data = base64.b64decode(chart_base64)
            img_buf = io.BytesIO(img_data)
            chart_img = Image(img_buf, width=16 * cm, height=5.85 * cm)
            chart_img.hAlign = 'LEFT'
            story.append(chart_img)
            story.append(Spacer(1, 4 * mm))
        except Exception:
            pass  # chart overslaan bij decode-fout

    # ── Sectie: Niveau 1-patronen ──────────────────────────────────────────────
    if niveau1_items:
        story.append(Paragraph('Niveau 1 — Directe AI-indicatoren', s['section_header']))
        story.append(hr())
        story.append(niveau1_tabel(niveau1_items, s))
        story.append(Spacer(1, 3 * mm))

    # ── Sectie: Kritieke waarschuwingen ───────────────────────────────────────
    if waarschuwingen:
        story.append(Paragraph('Kritieke bevindingen', s['section_header']))
        story.append(hr())
        story.append(waarschuwingen_tabel(waarschuwingen, s))
        story.append(Spacer(1, 3 * mm))

    # ── Sectie: Aanbevelingen ─────────────────────────────────────────────────
    if aanbevelingen:
        story.append(Paragraph('Aanbevelingen', s['section_header']))
        story.append(hr())
        advies_intro = risico_advies(risico)
        if advies_intro:
            story.append(Paragraph(advies_intro, ParagraphStyle(
                'advies_intro',
                fontName='Helvetica-Oblique',
                fontSize=9.5,
                leading=14,
                textColor=rc,
                spaceAfter=4 * mm,
            )))
        story.append(aanbevelingen_tabel(aanbevelingen, risico, s))
        story.append(Spacer(1, 3 * mm))

    # ── Statistieken ──────────────────────────────────────────────────────────
    story.append(Paragraph('Statistieken', s['section_header']))
    story.append(hr())

    flesch_kleur = C_GREEN if 30 <= flesch <= 55 else (C_AMBER if 20 <= flesch <= 65 else C_RED)
    ttr_kleur    = C_GREEN if ttr >= 0.45 else (C_AMBER if ttr >= 0.35 else C_RED)

    flesch_str = f'{flesch:.1f}'
    ttr_str = f'{ttr:.3f}'

    stat_data = [
        ['', 'Maatstaf', 'Waarde', 'Norm', 'Status'],
        ['', 'Flesch-Douma (leesbaarheid)', flesch_str, '30 – 55 (HBO)', '✓ OK' if 30 <= flesch <= 55 else '✗ Afwijking'],
        ['', 'MATTR (woordvariatie)', ttr_str, '≥ 0.45', '✓ OK' if ttr >= 0.45 else '✗ Afwijking'],
        ['', 'AI-patronen gevonden', str(patronen), '0 – 2 (laag)', risico.capitalize()],
    ]

    stat_colors = [
        flesch_kleur if not (30 <= flesch <= 55) else C_GREEN,
        ttr_kleur if ttr < 0.45 else C_GREEN,
        rc,
    ]

    stat_tbl = Table(stat_data, colWidths=['3%', '42%', '15%', '25%', '15%'])
    stat_style = [
        ('BACKGROUND', (0, 0), (-1, 0), C_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_PANEL, C_BG]),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Kleur voor status-kolom per rij
        ('TEXTCOLOR', (4, 1), (4, 1), stat_colors[0]),
        ('TEXTCOLOR', (4, 2), (4, 2), stat_colors[1]),
        ('TEXTCOLOR', (4, 3), (4, 3), stat_colors[2]),
        ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
        # Kleurstreep links
        ('BACKGROUND', (0, 1), (0, 1), stat_colors[0]),
        ('BACKGROUND', (0, 2), (0, 2), stat_colors[1]),
        ('BACKGROUND', (0, 3), (0, 3), stat_colors[2]),
    ]
    stat_tbl.setStyle(TableStyle(stat_style))
    story.append(stat_tbl)
    story.append(Spacer(1, 6 * mm))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(hr(C_BORDER))
    story.append(Paragraph(
        f'Gegenereerd door DutchQuill AI &nbsp;·&nbsp; {vandaag} &nbsp;·&nbsp; '
        'Humanizer v2.0 (20 detectiecategorieën)',
        s['footer']
    ))

    doc.build(story)
    return os.path.abspath(output_path)


def parse_niveau1(raw: str) -> list:
    """
    Verwacht format: "patroon|alternatief||patroon2|alternatief2||..."
    Geeft lijst van (patroon, alternatief, '') tuples.
    """
    items = []
    for entry in raw.split('||'):
        parts = entry.split('|')
        if len(parts) >= 2:
            items.append((parts[0].strip(), parts[1].strip(), ''))
    return items


def parse_lijst(raw: str) -> list:
    """Splits op | voor enkelvoudige lijsten (waarschuwingen, aanbevelingen)."""
    return [x.strip() for x in raw.split('|') if x.strip()]


def main():
    parser = argparse.ArgumentParser(
        description='Genereer een humaniseringsanalyse PDF-rapport'
    )
    parser.add_argument('--risico',       required=True, choices=['laag', 'gemiddeld', 'hoog'])
    parser.add_argument('--patronen',     required=True, type=int)
    parser.add_argument('--flesch',       required=True, type=float)
    parser.add_argument('--ttr',          required=True, type=float)
    parser.add_argument('--bestandsnaam', default='')
    parser.add_argument('--niveau1',      default='',
                        help='patroon|alternatief||patroon2|alternatief2||...')
    parser.add_argument('--waarschuwingen', default='',
                        help='Waarschuwing 1|Waarschuwing 2|...')
    parser.add_argument('--aanbevelingen', default='',
                        help='Aanbeveling 1|Aanbeveling 2|...')
    parser.add_argument('--chart-base64', default='', dest='chart_base64',
                        help='Base64-encoded PNG van generate_review_chart.py')
    parser.add_argument('--chart-file',   default='', dest='chart_file',
                        help='Pad naar bestand met base64 chart-output')
    parser.add_argument('--output',       default='.tmp/humaniseer_rapport.pdf')
    args = parser.parse_args()

    # Laad chart base64 uit bestand als --chart-file wordt meegegeven
    chart_b64 = args.chart_base64
    if not chart_b64 and args.chart_file and os.path.exists(args.chart_file):
        with open(args.chart_file, 'r') as f:
            chart_b64 = f.read().strip()

    niveau1 = parse_niveau1(args.niveau1) if args.niveau1 else []
    waarschuwingen = parse_lijst(args.waarschuwingen) if args.waarschuwingen else []
    aanbevelingen = parse_lijst(args.aanbevelingen) if args.aanbevelingen else []

    out = generate_pdf(
        output_path=args.output,
        risico=args.risico,
        patronen=args.patronen,
        flesch=args.flesch,
        ttr=args.ttr,
        bestandsnaam=args.bestandsnaam,
        niveau1_items=niveau1,
        waarschuwingen=waarschuwingen,
        aanbevelingen=aanbevelingen,
        chart_base64=chart_b64,
    )
    print(out)


if __name__ == '__main__':
    main()
