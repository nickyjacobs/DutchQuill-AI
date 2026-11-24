#!/usr/bin/env python3
"""
tools/diff_viewer.py — DutchQuill AI

Vergelijkt originele en herschreven tekst op woordniveau.
Toont toegevoegde (groen) en verwijderde (rood) woorden in de terminal,
of genereert een HTML-weergave.

Gebruik:
    python3 tools/diff_viewer.py --original origineel.txt --rewritten herschreven.txt
    python3 tools/diff_viewer.py --original origineel.txt --rewritten herschreven.txt --html
    python3 tools/diff_viewer.py --original origineel.txt --rewritten herschreven.txt --html --output diff.html
    python3 tools/diff_viewer.py --original origineel.txt --rewritten herschreven.txt --summary
"""

import sys
import re
import argparse
import difflib
from typing import List, Tuple, Dict

# ANSI kleuren voor terminal
RED = "\033[91m"
GREEN = "\033[92m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

# ─── Heuristische categorisering voor --summary ───────────────────────────────

# Subset van bekende Niveau 1 AI-woorden (voor detectie in verwijderde tokens)
_AI_WOORDEN = {
    'cruciaal', 'essentieel', 'robuust', 'baanbrekend', 'naadloos',
    'transformatief', 'katalysator', 'speerpunt', 'faciliteert', 'faciliteert',
    'demonstreert', 'onderstreept', 'weerspiegelt', 'stroomlijnt', 'stroomlijnen',
    'scala', 'betekenisvol', 'diepgaand', 'genuanceerd', 'proactief',
    'integraal', 'zodoende', 'fosteren', 'uiteraard', 'eigenlijk',
}

# Werkwoorden die op passief wijzen
_PASSIEF = {'werd', 'werden', 'is', 'zijn', 'wordt', 'worden', 'word'}

# APA-markers in de wijziging (z.d.-letter, paginanummer, [BRON, cursief markering)
_APA_RE = re.compile(
    r'z\.d\.-[a-z]|p\.\s*\d|pp\.\s*\d|\[BRON|\*[^*]+\*|Literatuurlijst',
    re.IGNORECASE
)

# Trema-tekens
_TREMA_RE = re.compile(r'[ëïüÉÏÜ]')


def _categorize_change(deleted: str, inserted: str) -> str:
    """Heuristische categorisering van één delete+insert blok."""
    # APA-correctie: referentielijst, z.d.-letters, paginanummers, [BRON NODIG]
    if _APA_RE.search(inserted) or _APA_RE.search(deleted):
        return 'apa'
    # Trema toegevoegd (taalfout gecorrigeerd)
    if _TREMA_RE.search(inserted) and not _TREMA_RE.search(deleted):
        return 'trema'
    del_words = {w.lower().strip('.,;:!?()[]"\'') for w in deleted.split()}
    ins_words = {w.lower().strip('.,;:!?()[]"\'') for w in inserted.split()}
    # AI-woordkeuze: een bekend AI-woord verdwijnt
    if del_words & _AI_WOORDEN:
        return 'ai_woord'
    # Passief → actief: passief-werkwoord verdwijnt maar is er niet in de insertie
    if (del_words & _PASSIEF) and not (ins_words & _PASSIEF):
        return 'passief_actief'
    # Samenstelling: spatie tussen woorden verdwijnt (losse woorden → aaneengeschreven)
    del_stripped = deleted.strip()
    ins_stripped = inserted.strip()
    if (' ' in del_stripped and ' ' not in ins_stripped
            and len(ins_stripped) > 3 and ins_stripped.isalpha()):
        return 'samenstelling'
    return 'overig'


def generate_summary(diff: List[Tuple[str, str]], text_a: str, text_b: str) -> str:
    """
    Genereer een gegroepeerde samenvatting van wijzigingscategorieën.
    Heuristische aanpak — niet perfect maar informatief.
    """
    counts: Dict[str, int] = {
        'apa': 0,
        'trema': 0,
        'samenstelling': 0,
        'ai_woord': 0,
        'passief_actief': 0,
        'overig': 0,
    }

    # Groepeer aaneengesloten delete/insert blokken als één wijziging
    i = 0
    while i < len(diff):
        tag, text = diff[i]
        if tag in ('delete', 'insert'):
            deleted_parts: List[str] = []
            inserted_parts: List[str] = []
            j = i
            while j < len(diff) and diff[j][0] in ('delete', 'insert'):
                if diff[j][0] == 'delete':
                    deleted_parts.append(diff[j][1])
                else:
                    inserted_parts.append(diff[j][1])
                j += 1
            cat = _categorize_change(
                ' '.join(deleted_parts),
                ' '.join(inserted_parts),
            )
            counts[cat] += 1
            i = j
        else:
            i += 1

    stats = compute_stats(diff, text_a, text_b)
    lijn = '═' * 60
    lijn2 = '─' * 60

    lines = [
        f"\n{lijn}",
        "  DIFF-SAMENVATTING — DutchQuill AI",
        lijn,
        f"  Origineel:   {stats['woorden_origineel']} woorden  →  "
        f"Herschreven: {stats['woorden_herschreven']} woorden",
        f"  Gewijzigd:   ~{stats['gewijzigd_pct']}% van de tekst",
        lijn2,
        "",
        "  Wijzigingen per categorie (heuristisch):",
        "",
    ]

    labels = [
        ('apa',            'APA-correcties       (z.d.-letters, paginanr., literatuurlijst)'),
        ('trema',          'Trema\'s gecorrigeerd  (geüpload, geïdentificeerd, etc.)'),
        ('samenstelling',  'Samenstellingen      (losse woorden aaneengeschreven)'),
        ('ai_woord',       'AI-woordkeuze        (Niveau 1-woorden vervangen)'),
        ('passief_actief', 'Passief → actief     (passieve constructie geactiveerd)'),
        ('overig',         'Overige wijzigingen  (stijl, structuur, overig)'),
    ]

    for key, label in labels:
        n = counts[key]
        bar = '█' * min(n, 30)
        lines.append(f"  {label}: {n:>3}  {bar}")

    lines += ["", lijn,
              "  Let op: categorisering is heuristisch — niet alle wijzigingen",
              "  worden correct geclassificeerd. Controleer de volledige diff",
              "  voor een volledig beeld.",
              f"{lijn}\n"]

    return '\n'.join(lines)


def tokenize(text: str) -> List[str]:
    """Splits tekst in woorden én witruimte (beide als tokens bewaard)."""
    return re.findall(r'\S+|\s+', text)


def word_diff(text_a: str, text_b: str) -> List[Tuple[str, str]]:
    """
    Berekent woorddiff tussen twee teksten.
    Geeft lijst van (tag, text) tuples:
        'equal'  — ongewijzigd
        'delete' — verwijderd uit origineel
        'insert' — toegevoegd in herschreven
    """
    tokens_a = tokenize(text_a)
    tokens_b = tokenize(text_b)

    matcher = difflib.SequenceMatcher(None, tokens_a, tokens_b, autojunk=False)
    result = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            result.append(("equal", "".join(tokens_a[i1:i2])))
        elif tag == "delete":
            result.append(("delete", "".join(tokens_a[i1:i2])))
        elif tag == "insert":
            result.append(("insert", "".join(tokens_b[j1:j2])))
        elif tag == "replace":
            result.append(("delete", "".join(tokens_a[i1:i2])))
            result.append(("insert", "".join(tokens_b[j1:j2])))

    return result


def compute_stats(diff: List[Tuple[str, str]], text_a: str, text_b: str) -> dict:
    """Bereken wijzigingsstatistieken."""
    words_a = len(text_a.split())
    words_b = len(text_b.split())
    deleted = sum(len(t.split()) for tag, t in diff if tag == "delete")
    inserted = sum(len(t.split()) for tag, t in diff if tag == "insert")
    changed_pct = round(((deleted + inserted) / max(words_a * 2, 1)) * 100, 1)

    return {
        "woorden_origineel": words_a,
        "woorden_herschreven": words_b,
        "verwijderd": deleted,
        "toegevoegd": inserted,
        "gewijzigd_pct": changed_pct,
    }


def print_terminal_diff(diff: List[Tuple[str, str]], text_a: str, text_b: str, plain: bool = False) -> None:
    """Print diff naar stdout. Gebruik plain=True voor output zonder ANSI-kleuren."""
    stats = compute_stats(diff, text_a, text_b)
    b = "" if plain else BOLD
    d = "" if plain else DIM
    r = "" if plain else RESET
    red = "" if plain else RED
    green = "" if plain else GREEN

    print(f"\n{b}{'═' * 60}{r}")
    print(f"{b}  DIFF-RAPPORT — DutchQuill AI{r}")
    print(f"{b}{'═' * 60}{r}")
    if not plain:
        print(f"{d}  Rood  = verwijderd uit origineel{r}")
        print(f"{d}  Groen = toegevoegd in herschreven versie{r}")
    else:
        print("  [-] = verwijderd uit origineel")
        print("  [+] = toegevoegd in herschreven versie")
    print(f"{b}{'─' * 60}{r}\n")

    for tag, text in diff:
        if tag == "equal":
            print(text, end="")
        elif tag == "delete":
            print(f"{red}[-{text}-]{r}" if plain else f"{red}{text}{r}", end="")
        elif tag == "insert":
            print(f"{green}[+{text}+]{r}" if plain else f"{green}{text}{r}", end="")

    print(f"\n\n{b}{'─' * 60}{r}")
    print(f"\n  Origineel:    {stats['woorden_origineel']} woorden")
    print(f"  Herschreven:  {stats['woorden_herschreven']} woorden")
    print(f"  Verwijderd:   {stats['verwijderd']} woorden")
    print(f"  Toegevoegd:   {stats['toegevoegd']} woorden")
    print(f"  Gewijzigd:    ~{stats['gewijzigd_pct']}% van de tekst")
    print(f"{b}{'═' * 60}{r}\n")


def generate_html(diff: List[Tuple[str, str]], text_a: str, text_b: str) -> str:
    """Genereer een HTML-pagina met inline diff-weergave."""

    def escape(s: str) -> str:
        return (s.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace("\n", "<br>"))

    stats = compute_stats(diff, text_a, text_b)

    diff_html = ""
    for tag, text in diff:
        escaped = escape(text)
        if tag == "equal":
            diff_html += escaped
        elif tag == "delete":
            diff_html += f'<del>{escaped}</del>'
        elif tag == "insert":
            diff_html += f'<ins>{escaped}</ins>'

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <title>DutchQuill AI — Diff Rapport</title>
  <style>
    body {{
      font-family: Georgia, 'Times New Roman', serif;
      font-size: 15px;
      line-height: 1.9;
      background: #f9f9f7;
      color: #222;
      margin: 0;
      padding: 32px;
      max-width: 960px;
    }}
    h1 {{
      font-size: 1.2em;
      color: #333;
      border-bottom: 2px solid #ccc;
      padding-bottom: 10px;
      margin-bottom: 20px;
    }}
    .stats {{
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 12px 20px;
      margin-bottom: 24px;
      font-size: 0.88em;
      color: #555;
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .stats span {{ white-space: nowrap; }}
    .stats strong {{ color: #333; }}
    .diff-box {{
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 24px 28px;
    }}
    .legend {{
      font-size: 0.83em;
      color: #777;
      margin-bottom: 16px;
      display: flex;
      gap: 20px;
    }}
    del {{
      background: #fde8e8;
      color: #c0392b;
      text-decoration: line-through;
      border-radius: 2px;
      padding: 0 2px;
    }}
    ins {{
      background: #e8f8e8;
      color: #27ae60;
      text-decoration: none;
      border-radius: 2px;
      padding: 0 2px;
    }}
  </style>
</head>
<body>
  <h1>DutchQuill AI — Diff Rapport</h1>

  <div class="stats">
    <span><strong>Origineel:</strong> {stats['woorden_origineel']} woorden</span>
    <span><strong>Herschreven:</strong> {stats['woorden_herschreven']} woorden</span>
    <span><strong>Verwijderd:</strong> {stats['verwijderd']} woorden</span>
    <span><strong>Toegevoegd:</strong> {stats['toegevoegd']} woorden</span>
    <span><strong>Gewijzigd:</strong> ~{stats['gewijzigd_pct']}%</span>
  </div>

  <div class="diff-box">
    <div class="legend">
      <span><del>Verwijderd uit origineel</del></span>
      <span><ins>Toegevoegd in herschreven versie</ins></span>
    </div>
    {diff_html}
  </div>
</body>
</html>"""
    return html


def main():
    parser = argparse.ArgumentParser(
        description="Vergelijk originele en herschreven tekst op woordniveau (DutchQuill AI)"
    )
    parser.add_argument("--original", "-a", required=True,
                        help="Originele tekst (bestandspad)")
    parser.add_argument("--rewritten", "-b", required=True,
                        help="Herschreven tekst (bestandspad)")
    parser.add_argument("--html", action="store_true",
                        help="Genereer HTML-uitvoer in plaats van terminal-diff")
    parser.add_argument("--plain", action="store_true",
                        help="Terminal-diff zonder ANSI-kleuren (voor gebruik vanuit scripts)")
    parser.add_argument("--output", "-o",
                        help="Uitvoerbestand voor HTML (standaard: stdout)")
    parser.add_argument("--summary", action="store_true",
                        help="Toon gegroepeerde samenvatting van wijzigingscategorieën")
    args = parser.parse_args()

    try:
        with open(args.original, encoding="utf-8") as f:
            text_a = f.read()
        with open(args.rewritten, encoding="utf-8") as f:
            text_b = f.read()
    except FileNotFoundError as e:
        print(f"Fout: Bestand niet gevonden — {e}", file=sys.stderr)
        sys.exit(1)

    diff = word_diff(text_a, text_b)

    if args.html:
        html = generate_html(diff, text_a, text_b)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"HTML-rapport opgeslagen: {args.output}")
        else:
            print(html)
    elif args.summary:
        print(generate_summary(diff, text_a, text_b))
    elif args.plain:
        print_terminal_diff(diff, text_a, text_b, plain=True)
    else:
        print_terminal_diff(diff, text_a, text_b)


if __name__ == "__main__":
    main()
