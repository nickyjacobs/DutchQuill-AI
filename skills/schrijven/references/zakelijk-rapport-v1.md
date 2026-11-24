# Workflow: Professioneel Rapport

## Doel
Genereer een professioneel rapport als .docx met optionele grafieken en infographics.
Geschikt voor interne voorstellen, documentatie, procesbeschrijvingen en klantrapportages.

## Wanneer gebruik je deze workflow?
- De gebruiker wil een professioneel (niet-academisch) document genereren
- Het document is bedoeld voor een zakelijke doelgroep
- Er is behoefte aan grafieken, infographics of visuele elementen
- Het rapport hoeft niet aan APA-richtlijnen te voldoen

Gebruik `rapport_schrijven.md` voor academische rapporten (APA 7e editie).

---

## Stap 0: Profiel laden [OPTIONEEL]

Controleer of `config/user_profile.json` een `professioneel` sectie bevat. Zo ja:
- Lees het bestand met de Read tool
- Gebruik de professionele gegevens (naam, functie, organisatie) als standaardwaarden
- Stel een bevestigingsvraag: "Ik gebruik de volgende professionele gegevens: [overzicht]. Klopt dit?"

Zo nee: vraag de benodigde metadata handmatig.

---

## Stap 1: Invoer verzamelen

Verzamel de volgende informatie. Vraag actief naar ontbrekende verplichte punten.

| Invoer | Beschrijving | Verplicht? |
|--------|-------------|-----------|
| Onderwerp | Waar gaat het rapport over? | **Ja** |
| Doelgroep | Voor wie is dit document? | **Ja** |
| Markdown-bron | Bestaand .md bestand of tekst om te verwerken | **Ja** |
| Grafieken | Welke visuele elementen zijn gewenst? | Nee |
| Toon | Formeel, semi-formeel, technisch | Nee (standaard: formeel) |

**Metadata voor het titelblad (vul aan vanuit profiel of vraag):**
- Titel [VERPLICHT]
- Ondertitel
- Auteur + functie
- Organisatie
- Datum
- Versie
- Classificatie (bijv. "Intern", "Vertrouwelijk")
- Doelgroep

---

## Stap 2: Taalcontrole [VERPLICHT]

Lees de volgende gidsen met de Read tool:
1. `workflows/taal_gids.md` — d/t-regels, samenstellingen, signaalwoorden
2. `workflows/humanize_nl_gids.md` — AI-patronen vermijden
3. `workflows/academische_stijl_gids.md` — werkwoordstijden, registers (ook relevant voor professioneel)

Bij professionele tekst gelden dezelfde taalregels als bij academisch werk. Het verschil zit in de structuur en opmaak, niet in de taalkwaliteit.

---

## Stap 3: Visuele elementen genereren [VERPLICHT]

Analyseer de brontekst en identificeer ALLE plaatsen waar data of concepten visueel gepresenteerd kunnen worden.

**Grafieken** (`tools/generate_chart.py`):

| Patroon in tekst | Type |
|------------------|------|
| Kosten, budget, vergelijking van waarden | `bar` |
| Voor/na situatie, huidige vs. gewenste staat | `comparison` |
| Fases, tijdlijn, implementatieplan | `timeline` |
| Risico's met kans x impact | `heatmap` |
| Verdeling, percentages, aandelen | `donut` |

```bash
python3 tools/generate_chart.py --type <type> --data '<json>' --output .tmp/rapport-professioneel/<naam>.png
```

**Diagrammen** (`tools/generate_diagram.py`):

| Patroon in tekst | Type |
|------------------|------|
| Systeem/infra architectuur, componenten | `architecture` |
| Proces, dataflow, beslisboom | `flow` |
| Netwerktopologie, security zones | `network` |
| Technologie stack, lagen | `layers` |

```bash
python3 tools/generate_diagram.py --type <type> --data '<json>' --output .tmp/rapport-professioneel/<naam>.png
```

**Thema:** Gebruik `--theme light` voor documenten met witte achtergrond (bijv. een huisstijl-template).

**Excalidraw-stijl visuals** (`scripts/generate-visual.js`):

Voor hand-drawn stijl visuals (professioneel maar informeel, Excalidraw-look). Geschikt voor conceptuele visualisaties, vergelijkingen en procesoverzichten die er visueel aantrekkelijk uitzien.

```bash
node scripts/generate-visual.js "<prompt>" .tmp/rapport-professioneel/<naam>.png "16:9" --input config/assets/excalidraw-style-reference.png
```

- Lees `config/assets/excalidraw-style-guide.md` voor het promptformat en kleurensysteem
- Kost ~€0.02-0.09 per afbeelding via kie.ai API
- Gebruik light mode (standaard) voor rapporten met witte achtergrond
- Aspect ratio's: `16:9` (standaard), `1:1`, `4:5`
- De style reference image (`--input`) is verplicht voor consistentie

**Wanneer welke tool:**

| Doel | Tool |
|------|------|
| Data-gedreven charts (staafdiagram, donut, heatmap) | `generate_chart.py` |
| Technische diagrammen (architectuur, flow, netwerk) | `generate_diagram.py` |
| Visueel aantrekkelijke conceptuele visuals | `generate-visual.js` (Excalidraw-stijl) |

Genereer **minimaal 1 visueel element** per rapport. Bij rapporten met meer dan 5 secties: streef naar 2-3 visuele elementen.

Sla alle gegenereerde visuals op in `.tmp/rapport-professioneel/`.
Verwijs in de markdown naar de visuals via `![caption](pad/naar/visual.png)`.

---

## Stap 4: Markdown voorbereiden

Zorg dat de markdown-bron voldoet aan de verwachte structuur:

- Headings: `#` t/m `####` (vrij te gebruiken, geen APA-levels)
- Tabellen: standaard markdown-tabellen
- Lijsten: `-` voor ongeordend, `1.` voor geordend
- Checklists: `- [ ]` en `- [x]`
- Codeblokken: ` ``` `
- Blokcitaten: `>`
- Afbeeldingen: `![caption](pad)`
- Pagina-einden: `---`

**Let op:** De markdown mag GEEN front matter bevatten (geen `---` YAML-blok aan het begin). Metadata wordt apart meegegeven via de CLI.

Als de bron een bestaand .md bestand is, controleer of het bovenstaande formaat klopt.
Als de bron tekst is die herschreven moet worden, schrijf eerst de verbeterde versie naar `.tmp/rapport-professioneel/bron.md`.

**Template-modus:** Wanneer je `--template` gebruikt bij de export, neem dan GEEN handmatige heading-nummering op in de markdown (bijv. schrijf `## Management Summary` in plaats van `## 1. Management Summary`). De template-stijlen nummeren automatisch via Word's Heading-stijlen.

---

## Stap 5: Humaniseringscheck [VERPLICHT]

Roep de tekst-analist subagent aan voor humaniseringsanalyse, of voer handmatig uit:

```bash
python3 tools/humanizer_nl.py --input .tmp/rapport-professioneel/bron.md --suggest
python3 tools/readability_nl.py --input .tmp/rapport-professioneel/bron.md
```

Bij risico gemiddeld of hoog: pas de tekst aan voordat je verdergaat.

---

## Stap 6: Document genereren [VERPLICHT]

```bash
python3 tools/professional_export.py \
    --input .tmp/rapport-professioneel/bron.md \
    --output .tmp/rapport-professioneel/<titel>.docx \
    --metadata '<json>'
```

De metadata JSON moet minimaal bevatten:
```json
{
    "title": "Rapporttitel",
    "author": "Naam",
    "organization": "Organisatie",
    "date": "27 maart 2026"
}
```

Optioneel: `subtitle`, `role`, `version`, `classification`, `audience`, `font`, `accent_color`.

**Template-modus** (huisstijl):
```bash
python3 tools/professional_export.py \
    --input .tmp/rapport-professioneel/bron.md \
    --output .tmp/rapport-professioneel/<titel>.docx \
    --template templates/huisstijl.docx \
    --metadata '{"title":"Titel","author":"Naam","version":"1.0","date":"27-3-2026","ref":"REF","client":"Organisatie","doc_type":"Rapportage"}'
```

---

## Stap 7: Afronden [VERPLICHT]

1. Sla de sessie op via `tools/history_writer.py`
2. Ruim werkbestanden op in `.tmp/` root (niet de output in `.tmp/rapport-professioneel/`)
3. Meld de gebruiker waar het bestand staat

---

## Verificatiechecklist [VERPLICHT]

Bevestig intern dat ALLE stappen zijn uitgevoerd:

- [ ] Alle relevante gidsen gelezen (taal, humanize, stijl)
- [ ] Visuele elementen gegenereerd (minimaal 1 grafiek of diagram per rapport)
- [ ] humanizer_nl.py + readability_nl.py uitgevoerd
- [ ] Risicobeoordeling laag, of tekst aangepast
- [ ] Geen handmatige heading-nummering bij template-modus
- [ ] Bronnenlijst correct geformateerd (geen genummerde lijst)
- [ ] professional_export.py uitgevoerd → .tmp/rapport-professioneel/<titel>.docx
- [ ] history_writer.py uitgevoerd
- [ ] Werkbestanden opgeruimd
