#!/usr/bin/env python3
"""
dq diagram: diagrammen voor rapporten (flow, architectuur, lagen, netwerk)

Gebruik:
    dq diagram --type architecture --data '<json>' --output diagram.png
    dq diagram --type flow --data '<json>' --output flow.png
    dq diagram --type network --data '<json>' --output network.png
    dq diagram --type layers --data '<json>' --output layers.png
    dq diagram --type flow --data '<json>' --output flow.png --theme light

Diagramtypen:
    architecture — Systeem-/infrastructuurarchitectuur (zones, nodes, verbindingen)
    flow         — Proces-/dataflow (stappen, beslissingen, richtingspijlen)
    network      — Netwerktopologie met securityzones
    layers       — Technologiestack / gelaagde architectuur

Thema's:
    dark  (standaard) — Donker thema voor presentaties en rapporten
    light             — Licht thema voor Word-documenten met witte achtergrond

JSON-schema per type: zie docstrings bij elke functie.

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
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
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

# ── Licht thema (voor Word-documenten) ──────────────────────────────────────
LIGHT_BG       = '#FFFFFF'
LIGHT_PANEL    = '#F5F7FA'
LIGHT_BORDER   = '#D0D8E8'
LIGHT_TEXT     = '#1A1A2E'
LIGHT_TEXT_DIM = '#5C6E8A'
LIGHT_WHITE    = '#1A1A2E'

# ── Actief thema (wordt gezet door main) ────────────────────────────────────
_theme = {}


def _set_theme(name):
    """Stel het actieve kleurenthema in."""
    global _theme
    if name == 'light':
        _theme = {
            'bg': LIGHT_BG, 'panel': LIGHT_PANEL, 'border': LIGHT_BORDER,
            'text': LIGHT_TEXT, 'text_dim': LIGHT_TEXT_DIM, 'white': LIGHT_WHITE,
        }
    else:
        _theme = {
            'bg': BG, 'panel': PANEL, 'border': BORDER,
            'text': TEXT, 'text_dim': TEXT_DIM, 'white': WHITE,
        }


def _setup_figure(width=10, height=6):
    """Maak een figuur met het actieve thema."""
    fig, ax = plt.subplots(figsize=(width, height), facecolor=_theme['bg'])
    ax.set_facecolor(_theme['bg'])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    return fig, ax


def _save(fig, output_path):
    """Sla figuur op en print pad."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor=fig.get_facecolor(),
                edgecolor='none', pad_inches=0.3)
    plt.close(fig)
    print(os.path.abspath(output_path))


def _hex_to_rgba(hex_color, alpha=0.15):
    """Converteer hex kleur naar RGBA tuple."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16) / 255, int(hex_color[2:4], 16) / 255, int(hex_color[4:6], 16) / 255
    return (r, g, b, alpha)


def _draw_node(ax, x, y, label, width=2.0, height=0.8, color=ACCENT, shape='box'):
    """Teken een node (box, rounded of diamond) en geef het center terug."""
    if shape == 'diamond':
        # Teken een ruit
        size = max(width, height) * 0.7
        diamond = plt.Polygon(
            [(x, y + size / 2), (x + size / 2, y), (x, y - size / 2), (x - size / 2, y)],
            closed=True, facecolor=_hex_to_rgba(color, 0.3), edgecolor=color, linewidth=1.5,
            zorder=5
        )
        ax.add_patch(diamond)
        ax.text(x, y, label, ha='center', va='center', color=_theme['white'],
                fontsize=9, fontweight='bold', zorder=6)
        return x, y

    if shape == 'rounded':
        boxstyle = 'round,pad=0.3,rounding_size=0.3'
    else:
        boxstyle = 'round,pad=0.3,rounding_size=0.1'

    box = FancyBboxPatch(
        (x - width / 2, y - height / 2), width, height,
        boxstyle=boxstyle, facecolor=_hex_to_rgba(color, 0.3),
        edgecolor=color, linewidth=1.5, zorder=5
    )
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', color=_theme['white'],
            fontsize=9, fontweight='bold', zorder=6)
    return x, y


def _draw_arrow(ax, start, end, label=None, color=None):
    """Teken een pijl tussen twee punten met optioneel label."""
    arrow_color = color or _theme['text_dim']
    arrow = FancyArrowPatch(
        start, end, arrowstyle='->', mutation_scale=15,
        color=arrow_color, linewidth=1.5, zorder=4,
        connectionstyle='arc3,rad=0.05'
    )
    ax.add_patch(arrow)
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.25, label, ha='center', va='center',
                color=_theme['text'], fontsize=8, fontstyle='italic', zorder=7,
                bbox=dict(boxstyle='round,pad=0.15', facecolor=_theme['bg'],
                          edgecolor='none', alpha=0.8))


# ── Diagramtypen ────────────────────────────────────────────────────────────

def diagram_architecture(data, output_path):
    """
    Systeem-/infrastructuurarchitectuur.
    data: {
        "title": "Deployment Architectuur",
        "zones": [
            {"id": "dmz", "label": "DMZ", "color": "#2196F3", "nodes": ["proxy", "vpn"]},
            {"id": "intern", "label": "Intern Netwerk", "color": "#4CAF50", "nodes": ["n8n", "siem"]}
        ],
        "nodes": [
            {"id": "proxy", "label": "Reverse Proxy"},
            {"id": "vpn", "label": "VPN Gateway"},
            {"id": "n8n", "label": "n8n Server"},
            {"id": "siem", "label": "SIEM"}
        ],
        "connections": [
            {"from": "proxy", "to": "n8n", "label": "HTTPS"},
            {"from": "n8n", "to": "siem", "label": "Log stream"}
        ]
    }
    """
    zones = data.get('zones', [])
    nodes_def = {n['id']: n for n in data.get('nodes', [])}
    connections = data.get('connections', [])

    # Layout berekenen
    zone_width = 3.0
    zone_padding = 0.8
    node_width = 2.2
    node_height = 0.8
    node_spacing_y = 1.4
    total_width = len(zones) * (zone_width + zone_padding) + zone_padding
    max_nodes = max((len(z.get('nodes', [])) for z in zones), default=1)
    total_height = max_nodes * node_spacing_y + 2.5

    fig, ax = _setup_figure(max(10, total_width + 2), max(6, total_height + 1))

    # Node posities bijhouden
    node_positions = {}

    for zi, zone in enumerate(zones):
        zone_x = zone_padding + zi * (zone_width + zone_padding)
        zone_y = 0.5
        zone_h = max_nodes * node_spacing_y + 1.2
        zone_color = zone.get('color', PALETTE[zi % len(PALETTE)])

        # Zone achtergrond
        zone_rect = FancyBboxPatch(
            (zone_x, zone_y), zone_width, zone_h,
            boxstyle='round,pad=0.2,rounding_size=0.2',
            facecolor=_hex_to_rgba(zone_color, 0.08),
            edgecolor=zone_color, linewidth=1.5, linestyle='--', zorder=2
        )
        ax.add_patch(zone_rect)

        # Zone label
        ax.text(zone_x + zone_width / 2, zone_y + zone_h - 0.3, zone.get('label', ''),
                ha='center', va='top', color=zone_color, fontsize=11, fontweight='bold', zorder=3)

        # Nodes in zone
        zone_nodes = zone.get('nodes', [])
        for ni, node_id in enumerate(zone_nodes):
            node_info = nodes_def.get(node_id, {'label': node_id})
            nx = zone_x + zone_width / 2
            ny = zone_y + zone_h - 1.2 - ni * node_spacing_y
            _draw_node(ax, nx, ny, node_info.get('label', node_id),
                       width=node_width, height=node_height, color=zone_color)
            node_positions[node_id] = (nx, ny)

    # Verbindingen tekenen
    for conn in connections:
        start_id = conn['from']
        end_id = conn['to']
        if start_id in node_positions and end_id in node_positions:
            sx, sy = node_positions[start_id]
            ex, ey = node_positions[end_id]
            # Bepaal aansluitpunten op basis van relatieve positie
            if abs(ex - sx) > abs(ey - sy):
                # Horizontale verbinding
                s_out = (sx + node_width / 2 if ex > sx else sx - node_width / 2, sy)
                e_in = (ex - node_width / 2 if ex > sx else ex + node_width / 2, ey)
            else:
                # Verticale verbinding
                s_out = (sx, sy - node_height / 2 if ey < sy else sy + node_height / 2)
                e_in = (ex, ey + node_height / 2 if ey < sy else ey - node_height / 2)
            _draw_arrow(ax, s_out, e_in, label=conn.get('label'), color=_theme['text_dim'])

    # Titel
    title = data.get('title', '')
    if title:
        ax.set_title(title, color=_theme['white'], fontsize=14, fontweight='bold', pad=15)

    ax.set_xlim(-0.5, total_width + 0.5)
    ax.set_ylim(-0.5, total_height + 0.5)
    ax.set_aspect('equal')
    _save(fig, output_path)


def diagram_flow(data, output_path):
    """
    Proces-/dataflow diagram.
    data: {
        "title": "Alert Processing Flow",
        "direction": "horizontal",
        "steps": [
            {"id": "alert", "label": "Alert\\nOntvangen", "shape": "rounded"},
            {"id": "enrich", "label": "Enrichment\\n(n8n)", "shape": "box"},
            {"id": "decide", "label": "Ernst?", "shape": "diamond"},
            {"id": "auto", "label": "Auto\\nResponse", "shape": "box"},
            {"id": "manual", "label": "Handmatige\\nTriage", "shape": "box"}
        ],
        "connections": [
            {"from": "alert", "to": "enrich"},
            {"from": "enrich", "to": "decide"},
            {"from": "decide", "to": "auto", "label": "Laag"},
            {"from": "decide", "to": "manual", "label": "Hoog"}
        ]
    }
    """
    steps = data.get('steps', [])
    connections = data.get('connections', [])
    direction = data.get('direction', 'horizontal')
    is_horizontal = direction == 'horizontal'

    # Bepaal layout met topologische sortering voor beter plaatsing
    node_width = 2.2
    node_height = 1.0
    spacing = 3.0

    # Bouw adjacency voor layout: bepaal kolom/rij per node
    step_ids = [s['id'] for s in steps]
    step_map = {s['id']: s for s in steps}

    # Eenvoudige layout: wijs positie toe op basis van volgorde in steps,
    # maar splits bij branches (meerdere uitgaande verbindingen)
    outgoing = {}
    incoming = {}
    for conn in connections:
        outgoing.setdefault(conn['from'], []).append(conn['to'])
        incoming.setdefault(conn['to'], []).append(conn['from'])

    # Bereken niveau (afstand vanaf start) via BFS
    levels = {}
    # Start bij nodes zonder inkomende verbindingen
    roots = [s for s in step_ids if s not in incoming]
    if not roots:
        roots = [step_ids[0]]

    queue = [(r, 0) for r in roots]
    while queue:
        node, level = queue.pop(0)
        if node in levels:
            levels[node] = max(levels[node], level)
        else:
            levels[node] = level
            for target in outgoing.get(node, []):
                queue.append((target, level + 1))

    # Nodes zonder level (niet bereikt via BFS)
    for s in step_ids:
        if s not in levels:
            levels[s] = len(levels)

    # Groepeer nodes per level
    level_groups = {}
    for node_id, level in levels.items():
        level_groups.setdefault(level, []).append(node_id)

    max_level = max(levels.values()) if levels else 0
    max_per_level = max(len(g) for g in level_groups.values()) if level_groups else 1

    # Posities berekenen
    node_positions = {}
    for level, group in level_groups.items():
        for idx, node_id in enumerate(group):
            # Center de groep
            offset = (idx - (len(group) - 1) / 2) * spacing
            if is_horizontal:
                x = level * spacing + 1.5
                y = -offset
            else:
                x = offset
                y = -level * spacing + (max_level * spacing / 2)
            node_positions[node_id] = (x, y)

    # Figuurgrootte berekenen
    if is_horizontal:
        fig_w = max(10, (max_level + 1) * spacing + 2)
        fig_h = max(5, max_per_level * spacing + 2)
    else:
        fig_w = max(8, max_per_level * spacing + 2)
        fig_h = max(6, (max_level + 1) * spacing + 2)

    fig, ax = _setup_figure(fig_w, fig_h)

    # Nodes tekenen
    for step in steps:
        sid = step['id']
        if sid not in node_positions:
            continue
        x, y = node_positions[sid]
        shape = step.get('shape', 'box')
        color_idx = step_ids.index(sid) if sid in step_ids else 0
        color = step.get('color', PALETTE[color_idx % len(PALETTE)])
        _draw_node(ax, x, y, step.get('label', sid),
                   width=node_width, height=node_height, color=color, shape=shape)

    # Verbindingen tekenen
    for conn in connections:
        start_id = conn['from']
        end_id = conn['to']
        if start_id not in node_positions or end_id not in node_positions:
            continue

        sx, sy = node_positions[start_id]
        ex, ey = node_positions[end_id]
        start_shape = step_map.get(start_id, {}).get('shape', 'box')
        end_shape = step_map.get(end_id, {}).get('shape', 'box')

        # Aansluitpunten berekenen
        dx = ex - sx
        dy = ey - sy

        if start_shape == 'diamond':
            d_size = max(node_width, node_height) * 0.7 / 2
            if abs(dx) > abs(dy):
                s_out = (sx + d_size * (1 if dx > 0 else -1), sy)
            else:
                s_out = (sx, sy + d_size * (1 if dy > 0 else -1))
        else:
            if abs(dx) > abs(dy):
                s_out = (sx + node_width / 2 * (1 if dx > 0 else -1), sy)
            else:
                s_out = (sx, sy + node_height / 2 * (1 if dy > 0 else -1))

        if end_shape == 'diamond':
            d_size = max(node_width, node_height) * 0.7 / 2
            if abs(dx) > abs(dy):
                e_in = (ex - d_size * (1 if dx > 0 else -1), ey)
            else:
                e_in = (ex, ey - d_size * (1 if dy > 0 else -1))
        else:
            if abs(dx) > abs(dy):
                e_in = (ex - node_width / 2 * (1 if dx > 0 else -1), ey)
            else:
                e_in = (ex, ey - node_height / 2 * (1 if dy > 0 else -1))

        _draw_arrow(ax, s_out, e_in, label=conn.get('label'), color=_theme['text_dim'])

    # Titel
    title = data.get('title', '')
    if title:
        ax.set_title(title, color=_theme['white'], fontsize=14, fontweight='bold', pad=15)

    # Automatische grenzen
    all_x = [p[0] for p in node_positions.values()]
    all_y = [p[1] for p in node_positions.values()]
    margin = 2.0
    ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
    ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
    ax.set_aspect('equal')
    _save(fig, output_path)


def diagram_network(data, output_path):
    """
    Netwerktopologie met securityzones.
    data: {
        "title": "Netwerktopologie",
        "zones": [
            {"id": "internet", "label": "Internet", "color": "#F44336"},
            {"id": "dmz", "label": "DMZ", "color": "#FF9800"},
            {"id": "intern", "label": "Intern", "color": "#4CAF50"}
        ],
        "nodes": [
            {"id": "cloud", "label": "Cloud API's", "zone": "internet"},
            {"id": "fw", "label": "Firewall", "zone": "dmz"},
            {"id": "proxy", "label": "Reverse Proxy", "zone": "dmz"},
            {"id": "app", "label": "n8n Server", "zone": "intern"},
            {"id": "db", "label": "Database", "zone": "intern"}
        ],
        "connections": [
            {"from": "cloud", "to": "fw"},
            {"from": "fw", "to": "proxy"},
            {"from": "proxy", "to": "app"},
            {"from": "app", "to": "db"}
        ]
    }
    """
    zones = data.get('zones', [])
    nodes = data.get('nodes', [])
    connections = data.get('connections', [])

    # Groepeer nodes per zone
    zone_nodes = {}
    for node in nodes:
        zone_id = node.get('zone', 'default')
        zone_nodes.setdefault(zone_id, []).append(node)

    zone_map = {z['id']: z for z in zones}

    # Layout: zones als horizontale banden, nodes verticaal gestapeld binnen zones
    zone_width = 3.5
    zone_padding = 0.6
    node_width = 2.4
    node_height = 0.8
    node_spacing_y = 1.4

    total_zones = len(zones) if zones else 1
    total_width = total_zones * (zone_width + zone_padding) + zone_padding
    max_nodes_in_zone = max((len(v) for v in zone_nodes.values()), default=1)
    total_height = max_nodes_in_zone * node_spacing_y + 2.0

    fig, ax = _setup_figure(max(10, total_width + 2), max(6, total_height + 1))

    node_positions = {}

    for zi, zone in enumerate(zones):
        zx = zone_padding + zi * (zone_width + zone_padding)
        zy = 0.5
        z_nodes = zone_nodes.get(zone['id'], [])
        zh = max(len(z_nodes), 1) * node_spacing_y + 1.2
        zone_color = zone.get('color', PALETTE[zi % len(PALETTE)])

        # Zone achtergrond met stippellijn
        zone_rect = FancyBboxPatch(
            (zx, zy), zone_width, zh,
            boxstyle='round,pad=0.2,rounding_size=0.2',
            facecolor=_hex_to_rgba(zone_color, 0.06),
            edgecolor=zone_color, linewidth=1.5, linestyle='--', zorder=2
        )
        ax.add_patch(zone_rect)

        # Zone label
        ax.text(zx + zone_width / 2, zy + zh - 0.3, zone.get('label', ''),
                ha='center', va='top', color=zone_color, fontsize=11, fontweight='bold', zorder=3)

        # Nodes
        for ni, node in enumerate(z_nodes):
            nx = zx + zone_width / 2
            ny = zy + zh - 1.2 - ni * node_spacing_y
            _draw_node(ax, nx, ny, node.get('label', node['id']),
                       width=node_width, height=node_height, color=zone_color)
            node_positions[node['id']] = (nx, ny)

    # Verbindingen
    for conn in connections:
        start_id = conn['from']
        end_id = conn['to']
        if start_id in node_positions and end_id in node_positions:
            sx, sy = node_positions[start_id]
            ex, ey = node_positions[end_id]
            if abs(ex - sx) > abs(ey - sy):
                s_out = (sx + node_width / 2 if ex > sx else sx - node_width / 2, sy)
                e_in = (ex - node_width / 2 if ex > sx else ex + node_width / 2, ey)
            else:
                s_out = (sx, sy - node_height / 2 if ey < sy else sy + node_height / 2)
                e_in = (ex, ey + node_height / 2 if ey < sy else ey - node_height / 2)
            _draw_arrow(ax, s_out, e_in, label=conn.get('label'), color=_theme['text_dim'])

    # Titel
    title = data.get('title', '')
    if title:
        ax.set_title(title, color=_theme['white'], fontsize=14, fontweight='bold', pad=15)

    ax.set_xlim(-0.5, total_width + 0.5)
    ax.set_ylim(-0.5, max(total_height, max_nodes_in_zone * node_spacing_y + 2) + 0.5)
    ax.set_aspect('equal')
    _save(fig, output_path)


def diagram_layers(data, output_path):
    """
    Technologiestack / gelaagde architectuur.
    data: {
        "title": "Technologie Stack",
        "layers": [
            {"label": "Infrastructuur", "description": "Proxmox, Docker, VM's", "color": "#F44336"},
            {"label": "Platform", "description": "Automatisering, SIEM, ticketing", "color": "#FF9800"},
            {"label": "Automatisering", "description": "Workflows, Playbooks", "color": "#2196F3"},
            {"label": "AI Analyse", "description": "Claude Code, API", "color": "#AB47BC"},
            {"label": "Output", "description": "Rapporten, Alerts, Tickets", "color": "#4CAF50"}
        ]
    }
    """
    layers = data.get('layers', [])
    n = len(layers)

    layer_height = 1.2
    layer_spacing = 0.15
    layer_width = 8.0
    total_height = n * (layer_height + layer_spacing) + 2.0

    fig, ax = _setup_figure(10, max(6, total_height))

    x_start = 1.0

    for i, layer in enumerate(layers):
        # Lagen van onder naar boven
        y = 0.5 + i * (layer_height + layer_spacing)
        color = layer.get('color', PALETTE[i % len(PALETTE)])

        # Laag rechthoek
        rect = FancyBboxPatch(
            (x_start, y), layer_width, layer_height,
            boxstyle='round,pad=0.1,rounding_size=0.15',
            facecolor=_hex_to_rgba(color, 0.25),
            edgecolor=color, linewidth=1.5, zorder=3
        )
        ax.add_patch(rect)

        # Label (links)
        ax.text(x_start + 0.5, y + layer_height / 2, layer.get('label', ''),
                ha='left', va='center', color=_theme['white'], fontsize=12, fontweight='bold', zorder=4)

        # Beschrijving (rechts)
        description = layer.get('description', '')
        if description:
            ax.text(x_start + layer_width - 0.5, y + layer_height / 2, description,
                    ha='right', va='center', color=_theme['text'], fontsize=10, zorder=4)

    # Titel
    title = data.get('title', '')
    if title:
        ax.set_title(title, color=_theme['white'], fontsize=14, fontweight='bold', pad=15)

    ax.set_xlim(0, layer_width + 2)
    ax.set_ylim(-0.5, total_height)
    _save(fig, output_path)


# ── Dispatcher ───────────────────────────────────────────────────────────────

DIAGRAM_TYPES = {
    'architecture': diagram_architecture,
    'flow': diagram_flow,
    'network': diagram_network,
    'layers': diagram_layers,
}


def main():
    parser = argparse.ArgumentParser(description='Genereer diagrammen voor professionele rapporten')
    parser.add_argument('--type', required=True, choices=DIAGRAM_TYPES.keys(),
                        help='Type diagram')
    parser.add_argument('--data', required=True,
                        help='JSON-string of pad naar JSON-bestand met diagramdata')
    parser.add_argument('--output', required=True,
                        help='Pad voor het gegenereerde .png-bestand')
    parser.add_argument('--title', default=None,
                        help='Overschrijf de titel uit de data')
    parser.add_argument('--theme', default='dark', choices=['dark', 'light'],
                        help='Kleurenthema: dark (standaard) of light (voor Word-documenten)')
    args = parser.parse_args()

    # Thema instellen
    _set_theme(args.theme)

    # Data laden
    if os.path.isfile(args.data):
        with open(args.data, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = json.loads(args.data)

    # Titel override
    if args.title:
        data['title'] = args.title

    # Diagram genereren
    diagram_fn = DIAGRAM_TYPES[args.type]
    diagram_fn(data, args.output)


if __name__ == '__main__':
    main()
