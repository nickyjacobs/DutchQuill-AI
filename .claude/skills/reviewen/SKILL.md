---
name: reviewen
description: Start de rapport_reviewen workflow. Gebruik dit wanneer de gebruiker een rapport of sectie wil laten nakijken op taal, APA, humanisering en structuur. Activeer proactief bij vragen als "check dit rapport", "nakijken", "review", "klaar voor inlevering?", "controleer mijn tekst".
model: sonnet
---

Je voert de `rapport_reviewen.md` workflow uit.

## Uitvoering

1. Lees `workflows/rapport_reviewen.md` volledig met de Read tool
2. Volg ALLE stappen en domeinen uit die workflow in volgorde — sla GEEN stap over
3. Bij twijfel over een stap: lees de workflow opnieuw

## Constraints (altijd van kracht)

- Lees ALLE gidsen die in de workflow genoemd worden met de Read tool — "raadpleeg" is niet voldoende
- Alle vier reviewdomeinen zijn VERPLICHT bij een volledige review
- Tools gemarkeerd als [VERPLICHT] MOETEN worden uitgevoerd via Bash
- Een tool die een fout geeft: rapporteer de fout, maar sla de tool NIET over
- De verificatiechecklist aan het einde MOET volledig worden doorlopen
- `history_writer.py` + `generate_report_pdf.py` zijn ALTIJD de laatste stappen
- Output gaat naar `.tmp/reviewen/<titel>.pdf`
- Presenteer een korte samenvatting in de chat (NIET het volledige rapport)
- Werkbestanden in `.tmp/` root worden na afloop opgeruimd
