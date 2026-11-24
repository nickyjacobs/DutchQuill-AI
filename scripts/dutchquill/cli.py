"""Ingang van `scripts/dq`: kiest het commando en roept de juiste module aan."""

from __future__ import annotations

import importlib
import sys

# Eigen commando's: module met main(argv)
EIGEN = {
    "config": "config",
    "werkmap": "werkmap",
    "versie": "versies",
    "historie": "historie",
    "doctor": "doctor",
    "materiaal": "materiaal",
    "extraheer": "extraheer",
    "beeld": "beeld",
    "stem": "stem",
    "feiten": "feiten",
    "gids": "gidsen",
}

# Bestaande tools uit v1 (worden in latere fases omgebouwd); hun main() leest sys.argv
TOOLS = {
    "tells": ("tells", "AI-patronen in NL- en EN-tekst, met stem en eigen regels"),
    "leesbaarheid": ("leesbaarheid", "Flesch-Douma en zinslengte (was readability_nl.py)"),
    "apa-check": ("apa_check", "APA-controles (was apa_checker.py)"),
    "apa-bron": ("apa_bron", "APA-bronvermelding uit JSON (was source_formatter.py)"),
    "taalcheck": ("taalcheck", "LanguageTool, alleen als privacy.languagetool aan staat (was grammar_check.py)"),
    "diff": ("diff", "Woordverschil origineel/nieuw (was diff_viewer.py)"),
    "docx-tekst": ("docx_tekst", ".docx naar Markdown en afbeeldingen (was docx_to_text.py)"),
    "md-docx": ("md_docx", "Markdown naar APA-.docx (was md_to_docx.py)"),
    "export-apa": ("export_apa", "APA-.docx uit payload-JSON (was word_export.py)"),
    "export-zakelijk": ("export_zakelijk", "Zakelijk .docx (was professional_export.py)"),
    "grafiek": ("grafiek", "Grafieken als png (was generate_chart.py)"),
    "diagram": ("diagram", "Diagrammen als png (was generate_diagram.py)"),
    "scorekaart": ("scorekaart", "Scoredashboard als png (was generate_review_chart.py)"),
    "rapport-pdf": ("rapport_pdf", "Analyse-/reviewrapport als pdf (was generate_report_pdf.py)"),
}


def hulp() -> str:
    regels = ["Gebruik: dq <commando> [opties]   (dq <commando> --help voor details)", "", "Eigen commando's:"]
    regels += [f"  {c}" for c in EIGEN]
    regels += ["", "Tools:"]
    regels += [f"  {c:<16} {uitleg}" for c, (_, uitleg) in TOOLS.items()]
    return "\n".join(regels)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(hulp())
        return
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd in ("--version", "versie-plugin"):
        from dutchquill import __version__
        print(__version__)
        return
    if cmd in EIGEN:
        importlib.import_module(f"dutchquill.{EIGEN[cmd]}").main(rest)
    elif cmd in TOOLS:
        module = importlib.import_module(f"dutchquill.{TOOLS[cmd][0]}")
        sys.argv = [f"dq {cmd}", *rest]
        module.main()
    else:
        print(f"Onbekend commando '{cmd}'.\n\n{hulp()}", file=sys.stderr)
        sys.exit(2)
