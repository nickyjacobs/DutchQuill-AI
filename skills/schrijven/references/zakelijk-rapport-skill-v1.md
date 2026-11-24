---
name: rapport-professioneel
description: Genereer een professioneel rapport als .docx met optionele grafieken. Gebruik bij zakelijke documenten, interne voorstellen, procesbeschrijvingen en rapportages. Activeer bij "maak een rapport", "genereer een voorstel", "zet dit om naar een professioneel document".
model: sonnet
---

Je voert de `rapport_professioneel.md` workflow uit.

## Uitvoering

1. Lees `workflows/rapport_professioneel.md` volledig met de Read tool
2. Volg ALLE stappen uit die workflow in volgorde
3. Bij twijfel over een stap: lees de workflow opnieuw

## Constraints (altijd van kracht)

- Lees ALLE gidsen die in de workflow genoemd worden met de Read tool
- Tools gemarkeerd als [VERPLICHT] MOETEN worden uitgevoerd via Bash
- Een tool die een fout geeft: rapporteer de fout, maar sla de tool NIET over
- De verificatiechecklist aan het einde MOET volledig worden doorlopen
- `history_writer.py` + `professional_export.py` zijn ALTIJD de laatste stappen
- Output gaat naar `.tmp/rapport-professioneel/<titel>.docx`
- Werkbestanden in `.tmp/` root worden na afloop opgeruimd

## Visuele elementen

**Grafieken** (`tools/generate_chart.py`):

| Type | Gebruik |
|------|---------|
| `bar` | Staafdiagram (kosten, vergelijkingen) |
| `comparison` | Voor/na vergelijking |
| `timeline` | Fases, implementatieplannen |
| `heatmap` | Risicomatrix |
| `donut` | Verdelingen, percentages |

**Diagrammen** (`tools/generate_diagram.py`):

| Type | Gebruik |
|------|---------|
| `architecture` | Systeem/infra architectuur |
| `flow` | Proces, dataflow, beslisboom |
| `network` | Netwerktopologie, security zones |
| `layers` | Technologie stack, lagen |

Gebruik `--theme light` bij documenten met witte achtergrond (huisstijl-template).

**Excalidraw-stijl visuals** (`scripts/generate-visual.js`):

Visueel aantrekkelijke hand-drawn stijl PNGs via kie.ai API (~€0.02-0.09/afbeelding).
Lees `config/assets/excalidraw-style-guide.md` voor promptformat.

| Doel | Tool |
|------|------|
| Data-gedreven charts | `generate_chart.py` |
| Technische diagrammen | `generate_diagram.py` |
| Conceptuele visuals (Excalidraw-stijl) | `generate-visual.js` |

## Verificatiechecklist [VERPLICHT]

- [ ] Alle gidsen gelezen (taal, humanize, stijl)
- [ ] Visuele elementen gegenereerd (minimaal 1 per rapport)
- [ ] humanizer_nl.py + readability_nl.py uitgevoerd
- [ ] Risicobeoordeling laag, of tekst aangepast
- [ ] Geen handmatige heading-nummering bij template-modus
- [ ] Bronnenlijst correct geformateerd
- [ ] professional_export.py uitgevoerd → .tmp/rapport-professioneel/<titel>.docx
- [ ] history_writer.py uitgevoerd
- [ ] Werkbestanden opgeruimd
