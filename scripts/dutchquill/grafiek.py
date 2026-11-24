#!/usr/bin/env python3
"""
dq grafiek: grafieken voor rapporten (staaf, tijdlijn, vergelijking, donut, heatmap)

Gebruik:
    dq grafiek --type bar --data '<json>' --output chart.png
    dq grafiek --type timeline --data '<json>' --output timeline.png
    dq grafiek --type heatmap --data '<json>' --output heatmap.png
    dq grafiek --type comparison --data '<json>' --output comparison.png
    dq grafiek --type donut --data '<json>' --output donut.png

Grafiektypen:
    bar         — Staafdiagram (kosten/besparingen, vergelijkingen)
    timeline    — Tijdlijn (fases, implementatieplannen)
    heatmap     — Heatmap (risicomatrix: kans x impact)
    comparison  — Voor/na vergelijking (twee kolommen)
    donut       — Donut-grafiek (verdeling, percentages)

JSON-schema per type: zie voorbeelden onderaan dit bestand.

Stdout bij succes: absoluut pad naar het gegenereerde .png-bestand
"""

import argparse
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

# ── Kleurenpalet (professioneel, donker thema) ──────────────────────────────
BG        = '#0F1923'
PANEL     = '#162029'
BORDER    = '#1E3040'
TEXT      = '#C8D6E0'
TEXT_DIM  = '#6B8599'
WHITE     = '#E8F0F5'
ACCENT    = '#2196F3'   # Blauw
GREEN     = '#4CAF50'
AMBER     = '#FF9800'
RED       = '#F44336'
TEAL      = '#26A69A'
PURPLE    = '#AB47BC'
ORANGE    = '#FF7043'

PALETTE = [ACCENT, GREEN, AMBER, TEAL, PURPLE, ORANGE, RED]


def _setup_figure(width=10, height=6):
    """Maak een figuur met donker thema."""
    fig, ax = plt.subplots(figsize=(width, height), facecolor=BG)
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_color(BORDER)
    ax.tick_params(colors=TEXT_DIM, labelsize=10)
    return fig, ax


def _save(fig, output_path):
    """Sla figuur op en print pad."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(),
                edgecolor='none', pad_inches=0.3)
    plt.close(fig)
    print(os.path.abspath(output_path))


# ── Grafiektypen ─────────────────────────────────────────────────────────────

def chart_bar(data, output_path):
    """
    Staafdiagram.
    data: {
        "title": "Kosten vs. Besparingen",
        "categories": ["Alert enrichment", "Phishing", "Rapportage"],
        "series": [
            {"label": "Huidig (uur/maand)", "values": [60, 18, 10], "color": "#F44336"},
            {"label": "Na automatisering", "values": [10, 5, 2.5], "color": "#4CAF50"}
        ],
        "ylabel": "Uren per maand"
    }
    """
    fig, ax = _setup_figure(10, 6)
    categories = data['categories']
    series = data['series']
    n = len(categories)
    n_series = len(series)
    bar_width = 0.7 / n_series
    x = np.arange(n)

    for i, s in enumerate(series):
        offset = (i - n_series / 2 + 0.5) * bar_width
        color = s.get('color', PALETTE[i % len(PALETTE)])
        bars = ax.bar(x + offset, s['values'], bar_width * 0.9, label=s['label'],
                      color=color, edgecolor='none', alpha=0.9, zorder=3)
        for bar, val in zip(bars, s['values']):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f'{val:g}', ha='center', va='bottom', color=TEXT, fontsize=9,
                    fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(categories, color=TEXT, fontsize=11)
    ax.set_ylabel(data.get('ylabel', ''), color=TEXT, fontsize=11)
    ax.set_title(data.get('title', ''), color=WHITE, fontsize=14, fontweight='bold', pad=15)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=10, loc='upper right')
    ax.grid(axis='y', color=BORDER, alpha=0.5, linestyle='--', zorder=0)
    ax.set_axisbelow(True)
    _save(fig, output_path)


def chart_timeline(data, output_path):
    """
    Tijdlijn.
    data: {
        "title": "Implementatieplan",
        "phases": [
            {"label": "Fase 0: Goedkeuring", "start": 0, "duration": 2, "unit": "weken"},
            {"label": "Fase 1: Test", "start": 2, "duration": 4, "unit": "weken"},
            {"label": "Fase 2: Validatie", "start": 6, "duration": 4, "unit": "weken"},
            {"label": "Fase 3: Productie", "start": 10, "duration": 4, "unit": "weken"}
        ],
        "xlabel": "Weken"
    }
    """
    phases = data['phases']
    n = len(phases)
    fig, ax = _setup_figure(12, max(4, n * 0.9 + 1))

    for i, phase in enumerate(phases):
        color = PALETTE[i % len(PALETTE)]
        y = n - 1 - i
        ax.barh(y, phase['duration'], left=phase['start'], height=0.5,
                color=color, edgecolor='none', alpha=0.85, zorder=3)
        # Label links van de bar
        ax.text(phase['start'] + phase['duration'] / 2, y, phase['label'],
                ha='center', va='center', color=WHITE, fontsize=10, fontweight='bold',
                path_effects=[pe.withStroke(linewidth=3, foreground=BG)])

    ax.set_yticks([])
    ax.set_xlabel(data.get('xlabel', ''), color=TEXT, fontsize=11)
    ax.set_title(data.get('title', ''), color=WHITE, fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='x', color=BORDER, alpha=0.5, linestyle='--', zorder=0)
    ax.set_axisbelow(True)
    _save(fig, output_path)


def chart_heatmap(data, output_path):
    """
    Risicomatrix (heatmap).
    data: {
        "title": "Risicomatrix",
        "xlabels": ["Laag", "Medium", "Hoog"],
        "ylabels": ["Laag", "Medium", "Hoog"],
        "xlabel": "Impact",
        "ylabel": "Kans",
        "values": [[1, 2, 3], [2, 4, 6], [3, 6, 9]],
        "annotations": [
            {"row": 0, "col": 2, "text": "R3"},
            {"row": 1, "col": 1, "text": "R4, R8"},
            {"row": 1, "col": 2, "text": "R2"},
            {"row": 0, "col": 1, "text": "R5, R6"},
            {"row": 0, "col": 0, "text": "R1, R7"}
        ]
    }
    """
    values = np.array(data['values'])
    fig, ax = _setup_figure(8, 6)

    # Kleurenschema: groen → geel → rood
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('risk', [GREEN, AMBER, RED])

    im = ax.imshow(values, cmap=cmap, aspect='auto', alpha=0.7)

    xlabels = data.get('xlabels', [str(i) for i in range(values.shape[1])])
    ylabels = data.get('ylabels', [str(i) for i in range(values.shape[0])])

    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, color=TEXT, fontsize=11)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, color=TEXT, fontsize=11)
    ax.set_xlabel(data.get('xlabel', ''), color=TEXT, fontsize=11, labelpad=10)
    ax.set_ylabel(data.get('ylabel', ''), color=TEXT, fontsize=11, labelpad=10)
    ax.set_title(data.get('title', ''), color=WHITE, fontsize=14, fontweight='bold', pad=15)

    # Annotaties
    for ann in data.get('annotations', []):
        ax.text(ann['col'], ann['row'], ann['text'],
                ha='center', va='center', color=WHITE, fontsize=11, fontweight='bold',
                path_effects=[pe.withStroke(linewidth=2, foreground='#00000088')])

    # Grid
    for i in range(values.shape[0] + 1):
        ax.axhline(i - 0.5, color=BORDER, linewidth=1)
    for j in range(values.shape[1] + 1):
        ax.axvline(j - 0.5, color=BORDER, linewidth=1)

    ax.tick_params(top=False, bottom=True, left=True, right=False)
    _save(fig, output_path)


def chart_comparison(data, output_path):
    """
    Voor/na vergelijking.
    data: {
        "title": "Tijdbesteding: huidig vs. geautomatiseerd",
        "categories": ["Alert enrichment", "Phishing response", "Rapportage"],
        "before": {"label": "Huidig", "values": [60, 18, 10]},
        "after": {"label": "Geautomatiseerd", "values": [10, 5, 2.5]},
        "unit": "uur/maand"
    }
    """
    fig, ax = _setup_figure(10, 6)
    categories = data['categories']
    n = len(categories)
    x = np.arange(n)
    bar_width = 0.35

    before = data['before']
    after = data['after']

    bars1 = ax.bar(x - bar_width / 2, before['values'], bar_width,
                   label=before['label'], color=RED, alpha=0.8, edgecolor='none', zorder=3)
    bars2 = ax.bar(x + bar_width / 2, after['values'], bar_width,
                   label=after['label'], color=GREEN, alpha=0.8, edgecolor='none', zorder=3)

    # Waarde-labels
    for bar, val in zip(bars1, before['values']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'{val:g}', ha='center', va='bottom', color=TEXT, fontsize=9, fontweight='bold')
    for bar, val in zip(bars2, after['values']):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'{val:g}', ha='center', va='bottom', color=TEXT, fontsize=9, fontweight='bold')

    # Besparingspercentage
    for i, (b, a) in enumerate(zip(before['values'], after['values'])):
        if b > 0:
            pct = ((b - a) / b) * 100
            ax.text(i, max(b, a) + 3, f'-{pct:.0f}%', ha='center', va='bottom',
                    color=ACCENT, fontsize=11, fontweight='bold')

    ax.set_xticks(x)
    ax.set_xticklabels(categories, color=TEXT, fontsize=11)
    ax.set_ylabel(data.get('unit', ''), color=TEXT, fontsize=11)
    ax.set_title(data.get('title', ''), color=WHITE, fontsize=14, fontweight='bold', pad=15)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=10)
    ax.grid(axis='y', color=BORDER, alpha=0.5, linestyle='--', zorder=0)
    ax.set_axisbelow(True)
    _save(fig, output_path)


def chart_donut(data, output_path):
    """
    Donut-grafiek.
    data: {
        "title": "Verdeling tijdsbesparing",
        "segments": [
            {"label": "Alert enrichment", "value": 50},
            {"label": "Phishing response", "value": 15},
            {"label": "Rapportage", "value": 7}
        ],
        "center_text": "72\nuur/maand"
    }
    """
    fig, ax = _setup_figure(8, 8)
    segments = data['segments']
    values = [s['value'] for s in segments]
    labels = [s['label'] for s in segments]
    colors_list = [s.get('color', PALETTE[i % len(PALETTE)]) for i, s in enumerate(segments)]

    wedges, texts, autotexts = ax.pie(
        values, labels=None, autopct='%1.0f%%', startangle=90,
        colors=colors_list, pctdistance=0.78,
        wedgeprops={'width': 0.35, 'edgecolor': BG, 'linewidth': 2}
    )

    for t in autotexts:
        t.set_color(WHITE)
        t.set_fontsize(11)
        t.set_fontweight('bold')

    # Center tekst
    center_text = data.get('center_text', '')
    if center_text:
        ax.text(0, 0, center_text, ha='center', va='center',
                color=WHITE, fontsize=16, fontweight='bold')

    # Legenda
    legend_handles = [mpatches.Patch(color=c, label=l) for c, l in zip(colors_list, labels)]
    ax.legend(handles=legend_handles, loc='lower center', bbox_to_anchor=(0.5, -0.05),
              ncol=min(3, len(segments)), facecolor=PANEL, edgecolor=BORDER,
              labelcolor=TEXT, fontsize=10)

    ax.set_title(data.get('title', ''), color=WHITE, fontsize=14, fontweight='bold', pad=15)
    _save(fig, output_path)


# ── Dispatcher ───────────────────────────────────────────────────────────────

CHART_TYPES = {
    'bar': chart_bar,
    'timeline': chart_timeline,
    'heatmap': chart_heatmap,
    'comparison': chart_comparison,
    'donut': chart_donut,
}


def main():
    parser = argparse.ArgumentParser(description='Genereer grafieken voor professionele rapporten')
    parser.add_argument('--type', required=True, choices=CHART_TYPES.keys(),
                        help='Type grafiek')
    parser.add_argument('--data', required=True,
                        help='JSON-string of pad naar JSON-bestand met grafiekdata')
    parser.add_argument('--output', required=True,
                        help='Pad voor het gegenereerde .png-bestand')
    args = parser.parse_args()

    # Data laden
    if os.path.isfile(args.data):
        with open(args.data, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.loads(args.data)

    # Grafiek genereren
    chart_fn = CHART_TYPES[args.type]
    chart_fn(data, args.output)


if __name__ == '__main__':
    main()
