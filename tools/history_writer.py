#!/usr/bin/env python3
"""
history_writer.py — Schrijft een entry naar .tmp/history.json

Gebruik:
    python3 tools/history_writer.py \\
        --type herschrijven \\
        --titel "Eerste 80 chars van de invoer" \\
        --metadata '{"doelen":["humaniseren"],"doelgroep":"docent"}' \\
        --output-file .tmp/herschreven.txt

Het output-bestand wordt gelezen voor de 'output'-waarde in de history-entry.
Als --output-file niet bestaat of niet opgegeven is, wordt 'output' een lege string.

Stdout bij succes: "✓ Opgeslagen in geschiedenis (id: <id>)"
"""

import argparse
import json
import os
import random
import string
import sys
from datetime import datetime, timezone


HISTORY_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '.tmp', 'history.json'
)

VALID_TYPES = {'schrijven', 'herschrijven', 'reviewen', 'humaniseer'}


def read_history(path: str):
    try:
        if not os.path.exists(path):
            return []
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def write_history(path: str, entries: list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def generate_id() -> str:
    ts = int(datetime.now(timezone.utc).timestamp() * 1000)
    rand = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{ts}-{rand}"


def main():
    parser = argparse.ArgumentParser(
        description='Schrijf een workflow-output naar .tmp/history.json'
    )
    parser.add_argument(
        '--type',
        required=True,
        choices=list(VALID_TYPES),
        help='Workflowtype: schrijven | herschrijven | reviewen | humaniseer'
    )
    parser.add_argument(
        '--titel',
        required=True,
        help='Titel voor de history-entry (eerste 80 chars van de invoer)'
    )
    parser.add_argument(
        '--metadata',
        default='{}',
        help='JSON-string met extra metadata (doelen, doelgroep, sectie, etc.)'
    )
    parser.add_argument(
        '--output-file',
        default=None,
        help='Pad naar het tekstbestand met de volledige workflow-output'
    )
    parser.add_argument(
        '--history-path',
        default=None,
        help='Overschrijf het standaard .tmp/history.json pad (voor testen)'
    )
    args = parser.parse_args()

    history_path = os.path.abspath(args.history_path or HISTORY_PATH)

    # Lees output-bestand
    output_text = ''
    if args.output_file:
        output_file = os.path.abspath(args.output_file)
        if os.path.exists(output_file):
            with open(output_file, encoding='utf-8') as f:
                output_text = f.read()
        else:
            print(f"Waarschuwing: output-bestand niet gevonden: {output_file}", file=sys.stderr)

    # Parseer metadata
    try:
        metadata = json.loads(args.metadata)
    except json.JSONDecodeError as e:
        print(f"Fout: ongeldige metadata JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # Bouw entry
    entry_id = generate_id()
    entry = {
        "id": entry_id,
        "type": args.type,
        "datum": datetime.now(timezone.utc).isoformat(),
        "titel": args.titel[:80],
        "metadata": metadata,
        "output": output_text,
    }

    # Lees, prepend, schrijf
    entries = read_history(history_path)
    entries.insert(0, entry)
    write_history(history_path, entries)

    print(f"✓ Opgeslagen in geschiedenis (id: {entry_id})")


if __name__ == '__main__':
    main()
