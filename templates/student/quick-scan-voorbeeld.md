---
vak: Vaknaam
vakcode: CODE
type: quick_scan
---

# Quick Scan — Vaknaam (CODE)

Dit bestand bevat de inlevereisen (quick scan) voor het vak. De agent leest alleen de items onder **## Rapportage** — items onder **## Praktijk** worden genegeerd.

## Hoe in te vullen

1. Kopieer dit bestand naar je werkmap, als `templates/vakken/<VAKCODE>/quick-scan.md`
   (bijvoorbeeld `templates/vakken/ABC1/quick-scan.md`). Makkelijker: upload het in DutchQuill Studio onder Vakken.
2. Plak de quick scan-items van je hogeschool
3. Verdeel ze in **Rapportage** (relevant voor DutchQuill AI) en **Praktijk** (niet relevant)
4. Elk item als Markdown-checkbox: `- [ ] Beschrijving van de eis`
5. Pas de frontmatter aan (vak, vakcode)

De mapnaam is de vakcode. Zet hetzelfde vak in je profiel (in Studio onder Vakken, of met
`dq config zet student.vakken '[{naam: Vaknaam, code: ABC1}]'`): heb je één vak, dan laadt de review de criteria vanzelf; heb je er meer, dan vraagt hij welk vak het is.
`dq vak lijst` laat zien welke vakken en bestanden DutchQuill vindt.

---

## Rapportage

- [ ] Voorbeeld: Titelpagina bevat studentnummer, naam, opleiding, vak en datum
- [ ] Voorbeeld: Samenvatting aanwezig (150-250 woorden)
- [ ] Voorbeeld: Inhoudsopgave aanwezig
- [ ] Voorbeeld: Literatuurlijst aanwezig conform APA 7
- [ ] Voorbeeld: Bijlagen genummerd en gerefereerd in de tekst

## Praktijk

(Items hieronder worden niet meegenomen in de review — alleen ter referentie)

- [ ] Voorbeeld: Praktijkopdracht X is ingeleverd
