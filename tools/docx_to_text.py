"""
docx_to_text.py — Converteer een .docx bestand naar Markdown-tekst.

Gebruik:
    python3 tools/docx_to_text.py --input pad/naar/bestand.docx
    python3 tools/docx_to_text.py --input pad/naar/bestand.docx --output .tmp/origineel.txt

Output:
    Tekst wordt geprint naar stdout én opgeslagen in .tmp/origineel.txt (standaard).
    Inline opmaak wordt bewaard: **vet** en *cursief* als Markdown-markers.
    Dit is relevant voor de APA-check: cursieve titels in de literatuurlijst blijven zichtbaar.
"""

import argparse
import sys
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn


def format_runs(para) -> str:
    """
    Combineer alle runs van een alinea met inline Markdown-opmaak.
    Vet → **tekst**, cursief → *tekst*.
    Aangrenzende runs met dezelfde opmaak worden samengevoegd.
    """
    parts = []
    for run in para.runs:
        text = run.text
        if not text:
            continue
        is_bold = bool(run.bold)
        is_italic = bool(run.italic)
        if is_bold and is_italic:
            parts.append(f'***{text}***')
        elif is_bold:
            parts.append(f'**{text}**')
        elif is_italic:
            parts.append(f'*{text}*')
        else:
            parts.append(text)
    return ''.join(parts).strip()


def extract_text(docx_path: str) -> str:
    doc = Document(docx_path)
    lines = []

    for para in doc.paragraphs:
        style = para.style.name if para.style else ''
        text = format_runs(para)

        if not text:
            lines.append('')
            continue

        if 'Heading 1' in style:
            lines.append(f'# {text}')
        elif 'Heading 2' in style:
            lines.append(f'## {text}')
        elif 'Heading 3' in style:
            lines.append(f'### {text}')
        elif 'List' in style or para.style.name.startswith('List'):
            lines.append(f'- {text}')
        else:
            lines.append(text)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Converteer .docx naar Markdown-tekst')
    parser.add_argument('--input', required=True, help='Pad naar het .docx bestand')
    parser.add_argument(
        '--output', default='.tmp/origineel.txt',
        help='Uitvoerbestand (standaard: .tmp/origineel.txt)'
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Fout: bestand niet gevonden: {input_path}', file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != '.docx':
        print(f'Fout: verwacht een .docx bestand, niet {input_path.suffix}', file=sys.stderr)
        sys.exit(1)

    text = extract_text(str(input_path))

    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True)
    output_path.write_text(text, encoding='utf-8')

    print(text)
    print(f'\n[Opgeslagen in {output_path}]', file=sys.stderr)


if __name__ == '__main__':
    main()
