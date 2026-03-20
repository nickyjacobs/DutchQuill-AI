#!/usr/bin/env python3
"""
generate_review_chart.py
Modern stat-card dashboard for DutchQuill review reports.
Outputs a base64-encoded PNG to stdout.

Usage:
  python3 tools/generate_review_chart.py \
    --flesch 39.5 \
    --ttr 0.383 \
    --patronen 3 \
    --risico gemiddeld
"""

import argparse
import base64
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = '#0A0E1A'
PANEL    = '#0D1225'
BORDER   = '#1A2140'
DIVIDER  = '#1E2B45'
TEXT_DIM = '#5C6E8A'
TEXT     = '#B8C8DC'
WHITE    = '#E8EDF5'
ACCENT   = '#FF6820'
GREEN    = '#3DD68C'
AMBER    = '#F5B944'
RED      = '#F06464'


def risico_color(risico):
    return {'laag': GREEN, 'gemiddeld': AMBER, 'hoog': RED}.get(risico.lower(), AMBER)


def risico_label(risico):
    return {
        'laag':      'Menselijk klinkend',
        'gemiddeld': 'Licht AI-aangeraakt',
        'hoog':      'Sterk AI-achtig',
    }.get(risico.lower(), risico.capitalize())


def draw_card_bg(ax):
    """Draw card background with subtle border."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_facecolor(PANEL)
    border = mpatches.FancyBboxPatch(
        (0.0, 0.0), 1.0, 1.0,
        boxstyle='round,pad=0.0',
        linewidth=1.2, edgecolor=BORDER,
        facecolor=PANEL, zorder=0,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(border)


def draw_progress_bar(ax, val, vmin, vmax, color,
                      y=0.36, h=0.085, x0=0.08, w=0.84,
                      norm_pos=None, norm_range=None):
    """Flat rounded progress bar with optional norm markers."""
    # Track
    ax.barh(y + h / 2, w, left=x0, height=h,
            color=DIVIDER, zorder=2)

    # Norm zone
    if norm_range:
        lo, hi = norm_range
        flo = np.clip((lo - vmin) / (vmax - vmin), 0, 1)
        fhi = np.clip((hi - vmin) / (vmax - vmin), 0, 1)
        ax.barh(y + h / 2, w * (fhi - flo), left=x0 + w * flo, height=h,
                color=GREEN, alpha=0.25, zorder=3)

    # Fill
    fill_f = np.clip((val - vmin) / (vmax - vmin), 0, 1)
    if fill_f > 0.005:
        ax.barh(y + h / 2, w * fill_f, left=x0, height=h,
                color=color, alpha=0.88, zorder=4)

    # Norm line
    if norm_pos is not None:
        nx = x0 + w * np.clip((norm_pos - vmin) / (vmax - vmin), 0, 1)
        ax.vlines(nx, y - 0.03, y + h + 0.03,
                  colors=WHITE, linewidth=2.0, alpha=0.55, zorder=5)


def draw_metric_card(ax, value_str, title, norm_text, color,
                     prog_val, prog_min, prog_max,
                     norm_pos=None, norm_range=None):
    draw_card_bg(ax)

    # Top accent stripe
    ax.axhspan(0.915, 1.0, color=color, alpha=0.7, zorder=2)

    # Card title
    ax.text(0.5, 0.845, title,
            ha='center', va='center',
            fontsize=13, color=TEXT_DIM,
            fontfamily='monospace', fontweight='bold')

    # Big value
    ax.text(0.5, 0.625, value_str,
            ha='center', va='center',
            fontsize=34, fontweight='bold', color=color,
            fontfamily='monospace')

    # Progress bar
    draw_progress_bar(ax, prog_val, prog_min, prog_max, color,
                      norm_pos=norm_pos, norm_range=norm_range)

    # Norm caption
    ax.text(0.5, 0.215, norm_text,
            ha='center', va='center',
            fontsize=12, color=TEXT_DIM, fontfamily='monospace')


def draw_risk_card(ax, risico, patronen):
    rc = risico_color(risico)
    draw_card_bg(ax)

    # Top accent (risk color)
    ax.axhspan(0.915, 1.0, color=rc, alpha=0.7, zorder=2)

    # Title
    ax.text(0.5, 0.845, 'AI-PATRONEN',
            ha='center', va='center',
            fontsize=13, color=TEXT_DIM,
            fontfamily='monospace', fontweight='bold')

    # Big count
    ax.text(0.5, 0.645, str(patronen),
            ha='center', va='center',
            fontsize=34, fontweight='bold', color=rc,
            fontfamily='monospace')

    ax.text(0.5, 0.525, 'patroon' if patronen == 1 else 'patronen',
            ha='center', va='center',
            fontsize=12, color=TEXT_DIM, fontfamily='monospace')

    # Segmented risk bar
    bar_y, bar_h = 0.355, 0.1
    seg_x0, seg_w = 0.06, 0.29
    gap = 0.01

    segments = [
        ('LAAG',      '0–2', GREEN),
        ('GEMIDDELD', '3–6', AMBER),
        ('HOOG',      '7+',  RED),
    ]
    active = {'laag': 0, 'gemiddeld': 1, 'hoog': 2}.get(risico.lower(), 1)

    for i, (lbl, rng, seg_col) in enumerate(segments):
        x = seg_x0 + i * (seg_w + gap + 0.005)
        is_active = (i == active)
        ax.barh(bar_y + bar_h / 2, seg_w, left=x, height=bar_h,
                color=seg_col, alpha=0.75 if is_active else 0.14, zorder=3)
        ax.text(x + seg_w / 2, bar_y - 0.06, lbl,
                ha='center', va='top', fontsize=10,
                color=seg_col if is_active else TEXT_DIM,
                fontfamily='monospace', fontweight='bold',
                alpha=1.0 if is_active else 0.55)
        ax.text(x + seg_w / 2, bar_y - 0.155, rng,
                ha='center', va='top', fontsize=10,
                color=TEXT_DIM, fontfamily='monospace',
                alpha=0.75 if is_active else 0.45)

    # Status label
    ax.text(0.5, 0.1, risico_label(risico.lower()),
            ha='center', va='center',
            fontsize=12, color=rc, fontfamily='monospace')


def generate_chart(flesch, ttr, patronen, risico):
    """Generate the chart and return as base64 PNG string."""
    fig = plt.figure(figsize=(8.5, 3.1), facecolor=BG)
    fig.patch.set_facecolor(BG)

    # Header
    fig.text(0.5, 0.975, 'HUMANISERINGSANALYSE',
             ha='center', va='top',
             fontsize=11.5, color=ACCENT,
             fontfamily='monospace', fontweight='bold')

    gs = fig.add_gridspec(1, 3,
                          left=0.02, right=0.98,
                          bottom=0.03, top=0.89,
                          wspace=0.055)

    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    ax3 = fig.add_subplot(gs[2])

    flesch_color = GREEN if 30 <= flesch <= 55 else (AMBER if 20 <= flesch <= 65 else RED)
    ttr_color    = GREEN if ttr >= 0.45 else (AMBER if ttr >= 0.35 else RED)

    draw_metric_card(
        ax1, f'{flesch:.1f}', 'LEESBAARHEID', 'HBO-norm: 30 – 55',
        flesch_color, flesch, 0, 100,
        norm_range=(30, 55)
    )
    draw_metric_card(
        ax2, f'{ttr:.3f}', 'WOORDVARIATIE', 'Norm: ≥ 0.45',
        ttr_color, ttr, 0, 1.0,
        norm_pos=0.45
    )
    draw_risk_card(ax3, risico, patronen)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=130, bbox_inches='tight',
                facecolor=BG, edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


def main():
    parser = argparse.ArgumentParser(description='Generate DutchQuill review chart')
    parser.add_argument('--flesch',   type=float, required=True)
    parser.add_argument('--ttr',      type=float, required=True)
    parser.add_argument('--patronen', type=int,   required=True)
    parser.add_argument('--risico',   type=str,   required=True,
                        choices=['laag', 'gemiddeld', 'hoog'])
    args = parser.parse_args()
    print(generate_chart(args.flesch, args.ttr, args.patronen, args.risico))


if __name__ == '__main__':
    main()
