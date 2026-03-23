# Tools — Technische Referentie

DutchQuill AI heeft 13 tools in de map `tools/` plus één hook in `.claude/hooks/`. Ze worden automatisch aangeroepen vanuit de skills. Je kunt ze ook handmatig draaien via de terminal voor losse taken.

Alle tools accepteren invoer via een bestand (`--input`) of via stdin. De output gaat standaard naar stdout tenzij je `--output` of `--json` gebruikt.

---

## 1. `humanizer_nl.py` — AI-patroondetectie

Analyseert een tekst op AI-schrijfpatronen en berekent een risicoscore. Dit is de tool achter `/humaniseer` en de humaniseringsstap in de andere skills.

### Gebruik

```bash
python3 tools/humanizer_nl.py --input tekst.txt
python3 tools/humanizer_nl.py --input tekst.txt --json
python3 tools/humanizer_nl.py --compare origineel.txt herschreven.txt
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input, -i` | pad | Invoerbestand (optioneel; standaard: stdin) |
| `--json` | schakelaar | Uitvoer als JSON-array |
| `--compare ORIGINEEL HERSCHREVEN` | 2 paden | Vergelijk twee versies naast elkaar |

### Risicoscore

De tool telt gevonden patronen en kent een niveau toe:

| Aantal patronen | Niveau | Aanbeveling |
|-----------------|--------|-------------|
| 0–2 | Laag | Kleine aanpassingen optioneel |
| 3–6 | Gemiddeld | Herschrijf de betreffende alinea's |
| 7+ | Hoog | Directe herziening noodzakelijk |

### 20 detectiecategorieën

De tool detecteert patronen in 20 categorieën:

| Nr. | Categorie | Wat het detecteert |
|-----|-----------|-------------------|
| 1 | Niveau 1-woorden | 47 directe AI-verraders (cruciaal, faciliteert, inzichten, etc.) — altijd vervangen |
| 2 | Niveau 2-dichtheid | 44 woorden die bij clustering verdacht zijn (drempel: >1,0 per 500 woorden) |
| 3 | Niveau 3-dichtheid | 6 context-afhankelijke termen (drempel: >3% van de tekst) |
| 4 | Formulaïsche openers | Type 1 brede intro's, Type 2 aankondigingen, Type 2b kaderstellingen, Type 3 samenvattingen |
| 5 | Opvulzinnen | 28 patronen inclusief vage toekomststelling |
| 6 | Em-dashes | Gedachtestreepjes zonder spaties (on-Nederlands) |
| 7 | Vage bronverwijzingen | 17 patronen als "uit onderzoek blijkt dat" en "studies tonen aan dat" |
| 8 | Uniforme zinslengte | 5+ opeenvolgende zinnen binnen 30% van elkaar in woordlengtes |
| 9 | Herhalende alineastarters | Dezelfde opener bij meerdere alinea's in de tekst |
| 10 | Zinsstartervariatie | Gebrek aan diversiteit in hoe zinnen beginnen binnen een alinea |
| 11 | Passieve dichtheid | 11 passiefconstructies (werd gedaan, is uitgevoerd, etc.) |
| 12 | Connectordichtheid | 15 overgebruikte verbindingswoorden (bovendien, tevens, daarnaast, etc.) |
| 13 | Bijvoeglijk stapelen | Drie of meer opeenvolgende adjectiva voor een zelfstandig naamwoord |
| 14 | Tricolon | Drie parallelle structuren in één zin (x, y en z — AI-patroon bij hoge dichtheid) |
| 15 | MATTR | Moving Average Type-Token Ratio — detecteert woordenschatarmoede |
| 16 | Proportionele scoring | Niveau 1-score aangepast naar documentlengte |
| 17 | Oxford comma | Komma vóór "en" in driedelige opsommingen (on-Nederlands, typisch Engels) |
| 18 | Anglicismen | 9 directe vertalingen (duiken in, fosteren, testament aan, etc.) |
| 19 | Communicatievormen | 9 chatbotpatronen ("Ik kan je helpen met...", "Samengevat..." etc.) |
| 20 | Alinealengtevariatie | Structurele uniformiteit in alinealengtes — AI schrijft alle alinea's even lang |

### Whitelist

De tool heeft een ingebouwde whitelist voor vakspecifieke termen die anders vals positief zouden scoren. Voorbeelden: "scala-programmeertaal" (informatica), "robuuste schatting" (statistiek), medische begrippen.

Termen op de whitelist worden niet meegeteld in de Niveau 1-score, ook al staan de woorden in de standaardlijst. De whitelist staat in `WHITELIST_NIVEAU1` in het script.

### JSON-uitvoer

```json
[
  {
    "categorie": 1,
    "naam": "Niveau 1-woorden",
    "gevonden": ["faciliteert", "inzichten"],
    "alternatieven": ["maakt mogelijk", "bevindingen"]
  }
]
```

---

## 2. `readability_nl.py` — Leesbaarheid (Flesch-Douma)

Berekent de Flesch-Douma leesbaarheidsindex voor Nederlandse tekst. Het HBO-norm ligt tussen 30 en 50.

### Gebruik

```bash
python3 tools/readability_nl.py --input tekst.txt
python3 tools/readability_nl.py --compare voor.txt na.txt
python3 tools/readability_nl.py --input tekst.txt --json
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input, -i` | pad | Invoerbestand (optioneel; standaard: stdin) |
| `--compare ORIGINEEL HERSCHREVEN` | 2 paden | Vergelijk scores voor en na |
| `--json` | schakelaar | Uitvoer als JSON-object |

### Score-interpretatie

| Score | Niveau | Geschikt voor HBO? |
|-------|--------|-------------------|
| 0–30 | Zeer moeilijk | Mogelijk te complex |
| 30–50 | Moeilijk | Ja, dit is het streefniveau |
| 50–65 | Redelijk | Aan de bovengrens |
| 65–80 | Standaard | Te eenvoudig |
| 80+ | Eenvoudig | Niet geschikt voor academisch |

### Formule

```
Score = 206,835 − 0,93 × (woorden / zinnen) − 77 × (lettergrepen / woorden)
```

De tool telt lettergrepen via Nederlandse klinkergroepen (ui, eu, au, oe, etc.) en herkent afkortingen (dr., drs., mr.) zodat die niet als zinsgrens gelden.

### JSON-uitvoer

```json
{
  "score": 42.3,
  "zinnen": 18,
  "woorden": 312,
  "lettergrepen": 498,
  "gemiddelde_zinslengte": 17.3,
  "gemiddelde_lettergrepen_per_woord": 1.6,
  "interpretatie": "Moeilijk — geschikt voor HBO"
}
```

---

## 3. `apa_checker.py` — APA 7-controle

Controleert tekst op APA 7e editie-overtredingen via reguliere expressies. De tool geeft meldingen met een suggestie per gevonden probleem.

### Gebruik

```bash
python3 tools/apa_checker.py --input rapport.txt
python3 tools/apa_checker.py --input rapport.txt --json
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input, -i` | pad | Invoerbestand (optioneel; standaard: stdin) |
| `--json` | schakelaar | Uitvoer als JSON-array |

### 8 APA-checks

1. **"&" in lopende tekst** — buiten haakjes moet "en" staan; binnen haakjes is "&" correct
2. **In-tekst citatieformaat** — detecteert voornamen, ontbrekende komma's, puntkomma tussen meerdere bronnen
3. **Directe citaten (<40 woorden)** — paginanummer verplicht (p. X of par. X)
4. **Positie van citatie** — moet vóór de punt staan, niet erna
5. **Aanwezigheid literatuurlijst** — zoekt naar kopjes "Literatuurlijst", "Referentielijst" of "Referenties"
6. **Voornamen in narratieve citaties** — "Jan de Vries (2021)" moet "De Vries (2021)" zijn
7. **Meerdere z.d.-bronnen van dezelfde auteur** — moeten z.d.-a, z.d.-b, etc. worden
8. **Citatie-dekking** — controleert of in-tekst citaties een overeenkomstige entry in de literatuurlijst hebben

### JSON-uitvoer

```json
[
  {
    "regel": 14,
    "categorie": "citatiepositie",
    "tekst": "...zoals beschreven. (De Vries, 2022)",
    "melding": "Citatie staat na de punt",
    "suggestie": "Zet de citatie vóór de punt: ...zoals beschreven (De Vries, 2022)."
  }
]
```

---

## 4. `grammar_check.py` — Grammatica en stijl

Stuurt de tekst naar de gratis LanguageTool API en toont grammatica-, spellings- en stijlfouten. De tool splitst grote teksten automatisch in stukken van maximaal 5.000 tekens.

### Gebruik

```bash
python3 tools/grammar_check.py --input tekst.txt
python3 tools/grammar_check.py --input tekst.txt --lang nl-NL
python3 tools/grammar_check.py --input tekst.txt --categorie grammatica
python3 tools/grammar_check.py --input tekst.txt --json --no-cache
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input, -i` | pad | Invoerbestand (optioneel; standaard: stdin) |
| `--lang` | code | Taalcode: `nl` (standaard) of `nl-NL` (strikter) |
| `--categorie` | tekst | Filter op categorie: grammatica, spelling, stijl, etc. |
| `--json` | schakelaar | Uitvoer als JSON-array |
| `--no-cache` | schakelaar | Cache overslaan en API opnieuw aanroepen |

### Categorieën

GRAMMAR, TYPOS, PUNCTUATION, STYLE, CASING, CONFUSED_WORDS, REDUNDANCY, MISC

### Cache

De tool slaat resultaten 24 uur op in `.tmp/grammar_cache.json`. Een volgende aanroep met dezelfde tekst geeft direct antwoord zonder API-vertraging. Gebruik `--no-cache` om dit te omzeilen.

**API-limieten (gratis, publiek):**
- Maximaal 20 verzoeken per minuut
- Pauze van 3,5 seconden tussen stukken
- Maximaal 5.000 tekens per verzoek

---

## 5. `diff_viewer.py` — Versievergelijking

Vergelijkt twee tekstbestanden op woordniveau. Toont welke woorden zijn toegevoegd, verwijderd of gewijzigd. Optioneel als HTML-bestand of met een categorieoverzicht.

### Gebruik

```bash
python3 tools/diff_viewer.py --original voor.txt --rewritten na.txt
python3 tools/diff_viewer.py --original voor.txt --rewritten na.txt --html --output vergelijking.html
python3 tools/diff_viewer.py --original voor.txt --rewritten na.txt --plain --summary
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--original, -a` | pad | Origineel tekstbestand (VERPLICHT) |
| `--rewritten, -b` | pad | Herschreven tekstbestand (VERPLICHT) |
| `--html` | schakelaar | HTML-uitvoer met kleurmarkering |
| `--plain` | schakelaar | Terminaluitvoer zonder ANSI-kleuren (voor scripts) |
| `--output, -o` | pad | Uitvoerbestand voor HTML (standaard: stdout) |
| `--summary` | schakelaar | Toon categorieoverzicht van wijzigingen |

### Categorieoverzicht (--summary)

De tool categoriseert wijzigingen automatisch in zes groepen:

| Categorie | Wat telt mee |
|-----------|-------------|
| apa | APA-correcties: z.d.-letters, paginanummers, literatuurlijstnotatie |
| trema | Trema-correcties: geüpload, geïdentificeerd |
| samenstelling | Losse woorden samengevoegd tot samenstellingen |
| ai_woord | Niveau 1 AI-woorden vervangen |
| passief_actief | Passieve zinnen omgezet naar actief |
| overig | Stijl, structuur en overige wijzigingen |

---

## 6. `source_formatter.py` — APA-bronformatter

Zet ruwe brongegevens (als JSON) om naar een correcte APA 7-referentieregel plus in-tekst citaties.

### Gebruik

```bash
python3 tools/source_formatter.py --input bron.json
python3 tools/source_formatter.py --input bronnen.json --json
python3 tools/source_formatter.py --help-schema
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input, -i` | pad | JSON-bestand met één of meerdere bronnen (optioneel; standaard: stdin) |
| `--help-schema` | schakelaar | Toon JSON-schemavoorbeelden per brontype |
| `--json` | schakelaar | Uitvoer als JSON-array |

### 15 brontypen

| Type | Gebruik voor |
|------|-------------|
| `boek` | Boek met of zonder DOI |
| `boek_hoofdstuk` | Hoofdstuk in een geredigeerd boek |
| `tijdschriftartikel` | Wetenschappelijk tijdschriftartikel |
| `webpagina` | Webpagina met publicatiedatum |
| `webpagina_geen_datum` | Webpagina zonder datum (z.d.) |
| `rapport` | Organisatierapport of beleidsdocument |
| `scriptie` | Bachelor- of masterthesis |
| `krant_online` | Online krantenartikel |
| `youtube` | YouTube-video |
| `podcast` | Podcastaflevering |
| `wet` | Wet of regelgeving |
| `wikipedia` | Wikipedia-artikel (auteur automatisch ingevuld) |
| `woordenboek_online` | Online woordenboekdefinitie |
| `film` | Film |
| `ted_talk` | TED-lezing |

### Invoerformaat

```json
{
  "type": "tijdschriftartikel",
  "auteurs": ["De Vries, J.", "Bakker, L."],
  "jaar": 2023,
  "titel": "Titel van het artikel",
  "tijdschrift": "Naam Tijdschrift",
  "volume": 15,
  "nummer": 2,
  "paginas": "44-58",
  "doi": "10.1234/tijdschrift.2023.001"
}
```

Meerdere bronnen: geef een JSON-array met meerdere objecten.

Voor een overzicht van alle velden per type: `python3 tools/source_formatter.py --help-schema`

### Auteursopmaak

De tool past automatisch de APA-regel voor het aantal auteurs toe:

- 1 auteur: `De Vries, J.`
- 2 auteurs: `De Vries, J., & Bakker, L.`
- 3–20 auteurs: alle namen met "&" voor de laatste
- 21+ auteurs: eerste 19 + "..." + laatste auteur

### JSON-uitvoer

```json
[
  {
    "type": "tijdschriftartikel",
    "referentie": "De Vries, J., & Bakker, L. (2023). Titel van het artikel. *Naam Tijdschrift*, *15*(2), 44–58. https://doi.org/10.1234/tijdschrift.2023.001",
    "intext_parenthetisch": "(De Vries & Bakker, 2023)",
    "intext_narratief": "De Vries en Bakker (2023)"
  }
]
```

---

## 7. `docx_to_text.py` — .docx naar tekst

Converteert een Word-bestand naar platte tekst met Markdown-opmaak. Gebruik dit als eerste stap als je een .docx wil verwerken met een van de andere tools.

### Gebruik

```bash
python3 tools/docx_to_text.py --input rapport.docx
python3 tools/docx_to_text.py --input rapport.docx --output .tmp/rapport.txt
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input` | pad | .docx-bestand (VERPLICHT) |
| `--output` | pad | Uitvoerbestand (standaard: `.tmp/origineel.txt`) |

### Opmaakconversie

| Word-opmaak | Uitvoer |
|-------------|---------|
| Kop Niveau 1 | `# Koptekst` |
| Kop Niveau 2 | `## Koptekst` |
| Kop Niveau 3 | `### Koptekst` |
| Vet | `**tekst**` |
| Cursief | `*tekst*` |
| Vet en cursief | `***tekst***` |
| Lijstitems | `- item` |
| Tabellen | Markdown-tabelformaat (`\| kop \| kop \|`) |

De tool itereert over paragrafen én tabellen in documentvolgorde. Word-tabellen worden als markdown-tabellen in de output opgenomen.

De tekst wordt opgeslagen in het uitvoerbestand en ook naar stdout gestuurd. Een bevestiging verschijnt op stderr: `[Opgeslagen in .tmp/origineel.txt]`.

---

## 8. `word_export.py` — Volledige .docx-generator

Bouwt een APA 7-conform Word-document op basis van een JSON-payload. Dit is de meest uitgebreide tool: hij ondersteunt titelpagina, samenvatting, inhoudsopgave, afkortingenlijst, bijlagen en alle APA-kopopmaak.

### Gebruik

```bash
python3 tools/word_export.py --input document.json
python3 tools/word_export.py --input document.json --output rapport.docx
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input` | pad | JSON-payload (optioneel; standaard: stdin) |
| `--output` | pad | Uitvoerpad .docx (standaard: `.tmp/output.docx`) |

### JSON-schema

```json
{
  "metadata": {
    "title": "Rapporttitel",
    "subtitle": "Ondertitel",
    "authors": ["Voornaam Achternaam"],
    "student_numbers": ["123456"],
    "institution": "Naam Instelling",
    "faculty": "Faculteitnaam",
    "course": "Vaknaam — Vakcode",
    "supervisor": "Dr. Naam",
    "submission_date": "19 maart 2026",
    "font": "times"
  },
  "abstract": {
    "text": "Samenvattingstekst (150–250 woorden).",
    "keywords": ["trefwoord1", "trefwoord2"]
  },
  "abbreviations": [
    {"afkorting": "MKB", "definitie": "Midden- en Kleinbedrijf"}
  ],
  "introduction_text": [ ],
  "body": [ ],
  "conclusion_text": [ ],
  "references": [
    "Auteur, A. (2023). *Titel.* Uitgever."
  ],
  "appendices": [
    {
      "label": "Bijlage A",
      "title": "Beschrijvende titel",
      "content": [ ]
    }
  ]
}
```

Alleen `metadata.title` is verplicht. Alle andere velden zijn optioneel.

**Lettertypeopties (`font`):**

| Waarde | Lettertype | Grootte |
|--------|-----------|---------|
| `times` (standaard) | Times New Roman | 12 pt |
| `arial` | Arial | 11 pt |
| `georgia` | Georgia | 11 pt |

### Bloktypes voor `body`, `introduction_text`, `conclusion_text` en bijlagen

```json
{ "type": "paragraph", "text": "Tekst van de alinea." }

{ "type": "heading", "level": 2, "text": "Kopnaam" }

{ "type": "block_quote", "text": "Geciteerde tekst...", "citation": "(Auteur, 2023, p. 14)" }

{ "type": "table", "number": 1, "title": "Tabeltitel", "headers": ["Kolom 1", "Kolom 2"], "rows": [["r1c1", "r1c2"]], "note": "Noot onder de tabel." }

{ "type": "figure_placeholder", "number": 1, "caption": "Figuuromschrijving.", "image_path": "afbeeldingen/figuur1.png", "note": "Noot onder de figuur." }
// APA 7: nummer + titel staan boven de afbeelding; noot staat onder

{ "type": "page_break" }
```

### Kopniveaus (APA 7)

| Level | Opmaak |
|-------|--------|
| 1 | Gecentreerd, vet — nieuwe pagina in hoofdtekst |
| 2 | Links uitgelijnd, vet |
| 3 | Links uitgelijnd, vet cursief |
| 4 | Ingesprongen, vet — tekst gaat op dezelfde regel door na een punt |
| 5 | Ingesprongen, vet cursief — tekst gaat op dezelfde regel door na een punt |

Numerieke voorvoegsels (1., 3.1) worden automatisch verwijderd uit kopnamen.

### Inline Markdown in tekstvelden

In alle tekstvelden werkt Markdown-inline-opmaak:
- `**vet**` wordt vet
- `*cursief*` wordt cursief
- DOI-URL's in de literatuurlijst worden automatisch klikbare hyperlinks

---

## 9. `md_to_docx.py` — Markdown naar APA .docx

Converteert een Markdown- of platte-tekstbestand naar een APA-conform Word-document. Herkent secties automatisch op basis van hun kopnaam.

### Gebruik

```bash
python3 tools/md_to_docx.py --input sectie.md
python3 tools/md_to_docx.py --input sectie.md --output rapport.docx
python3 tools/md_to_docx.py --input sectie.md --metadata '{"titel":"Mijn Rapport","naam":"Jan de Vries"}'
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--input` | pad | Invoerbestand (optioneel; standaard: stdin) |
| `--output` | pad | Uitvoerpad .docx |
| `--metadata` | JSON-string | Titelpaginagegevens als JSON (overschrijft front matter) |

### Metadatavelden (`--metadata`)

```json
{
  "titel": "Rapporttitel",
  "ondertitel": "Ondertitel",
  "naam": "Voornaam Achternaam",
  "studentnummer": "123456",
  "opleiding": "Software Engineering",
  "instelling": "Hogeschool Amsterdam",
  "datum": "19 maart 2026"
}
```

### Automatische sectieherkenning

De tool past APA-regels toe per sectienaam:

| Kopnaam | Behandeling |
|---------|-------------|
| Inleiding | Kop verwijderd — documenttitel als kop (APA-regel) |
| Samenvatting | Apart opgemaakt als abstract |
| Conclusie | Kop verwijderd — "Conclusie" als documentkop |
| Alle andere secties | Kop blijft staan |

### Front matter

Platte tekst vóór de eerste kop wordt herkend als titelpaginagegevens. De tool zoekt naar patronen zoals "Studentnummer:", "Opleiding:" en instellingsnamen (hogeschool, universiteit, fontys, avans, saxion, novi). Alle niet-herkende regels worden de titel of ondertitel.

Titelpagina-volgorde (APA 7 student paper): Titel (vet) → Auteur → Studentnummer → Instelling → Opleiding → Vak → Begeleider → Datum.

Afkortingentabellen worden automatisch herkend en als aparte afkortingenlijst in het document geplaatst, zonder "Tabel N" label. Twee formaten worden ondersteund:

1. **Markdown-tabel:** `| Afkorting | Definitie |` met rijen eronder
2. **Bold+tab formaat:** `**ABBR**\tDefinitie` onder een heading met "Afkortingen"

---

## 10. `generate_review_chart.py` — Statistiekenkaart

Genereert een PNG-afbeelding met drie statistiekenkaarten: leesbaarheid, woordvariatie en AI-patronen. De afbeelding wordt als base64-string naar stdout gestuurd voor inbedding in PDF-rapporten.

### Gebruik

```bash
python3 tools/generate_review_chart.py --flesch 42.1 --ttr 0.52 --patronen 3 --risico gemiddeld
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--flesch` | decimaal | Flesch-Douma score (VERPLICHT) |
| `--ttr` | decimaal | Type-Token Ratio (VERPLICHT) |
| `--patronen` | getal | Aantal gevonden AI-patronen (VERPLICHT) |
| `--risico` | keuze | Risiconiveau: `laag`, `gemiddeld` of `hoog` (VERPLICHT) |

De uitvoer is een base64-gecodeerde PNG op stdout. Je geeft die string door aan `generate_report_pdf.py` via `--chart-base64`.

---

## 11. `generate_report_pdf.py` — Analyserapport PDF

Genereert een PDF-analyserapport met scores, AI-woorden, waarschuwingen en aanbevelingen. Dit is het eindproduct van `/humaniseer`.

### Gebruik

```bash
python3 tools/generate_report_pdf.py \
  --risico gemiddeld \
  --patronen 4 \
  --flesch 42.1 \
  --ttr 0.52 \
  --bestandsnaam mijn_rapport.txt \
  --niveau1 "faciliteert|maakt mogelijk||inzichten|bevindingen" \
  --waarschuwingen "Hoge passieve dichtheid|Oxford comma gevonden" \
  --aanbevelingen "Vervang faciliteert door maakt mogelijk|Controleer zinslengtevariatie" \
  --chart-base64 "$(python3 tools/generate_review_chart.py --flesch 42.1 --ttr 0.52 --patronen 4 --risico gemiddeld)" \
  --output .tmp/humaniseer/rapport.pdf
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--risico` | keuze | `laag`, `gemiddeld` of `hoog` (VERPLICHT) |
| `--patronen` | getal | Aantal gevonden patronen (VERPLICHT) |
| `--flesch` | decimaal | Flesch-Douma score (VERPLICHT) |
| `--ttr` | decimaal | Type-Token Ratio (VERPLICHT) |
| `--bestandsnaam` | tekst | Oorspronkelijke bestandsnaam voor weergave (VERPLICHT) |
| `--niveau1` | tekst | Pipe-gescheiden AI-woorden met alternatieven (VERPLICHT) |
| `--waarschuwingen` | tekst | Pipe-gescheiden waarschuwingen (VERPLICHT) |
| `--aanbevelingen` | tekst | Pipe-gescheiden aanbevelingen (VERPLICHT) |
| `--chart-base64` | tekst | Base64-PNG van generate_review_chart.py (optioneel) |
| `--output` | pad | Uitvoerpad .pdf (VERPLICHT) |

### Formaat voor --niveau1

Schei term-alternatiefparen met dubbele pipe (`||`). Schei term en alternatief met enkele pipe (`|`):

```
"faciliteert|maakt mogelijk||inzichten|bevindingen||baanbrekend|vernieuwend"
```

### PDF-structuur

Het rapport bevat: koptekst met risicolabel, scorekaart, tabel met Niveau 1-woorden en alternatieven, waarschuwingen, aanbevelingen en de statistiekenkaart als de `--chart-base64` wordt meegegeven.

---

## 12. `history_writer.py` — Sessielog

Schrijft een logboekregel naar `.tmp/history.json`. Elke skill roept dit als laatste stap aan.

### Gebruik

```bash
python3 tools/history_writer.py \
  --type humaniseer \
  --titel "Eerste 80 tekens van de invoertekst" \
  --metadata '{"doelgroep": "docent"}' \
  --output-file .tmp/humaniseer/rapport.pdf
```

### Vlaggen

| Vlag | Type | Omschrijving |
|------|------|-------------|
| `--type` | keuze | `schrijven`, `herschrijven`, `reviewen` of `humaniseer` (VERPLICHT) |
| `--titel` | tekst | Eerste 80 tekens van de invoer (VERPLICHT) |
| `--metadata` | JSON-string | Extra informatie: doelen, doelgroep, sectie, etc. (standaard: `{}`) |
| `--output-file` | pad | Pad naar het gegenereerde bestand om op te nemen in de log (optioneel) |
| `--history-path` | pad | Overschrijf het standaard `.tmp/history.json`-pad (voor testdoeleinden) |

### Logboekregel

```json
{
  "id": "1711000445123-a7k3m9",
  "type": "humaniseer",
  "datum": "2026-03-20T15:30:45.123456+00:00",
  "titel": "Eerste 80 tekens van de invoertekst",
  "metadata": { "doelgroep": "docent" },
  "output": "<volledige inhoud van --output-file>"
}
```

Het bestand `.tmp/history.json` bevat een array. Nieuwe regels worden bovenaan toegevoegd. Het bestand wordt aangemaakt als het nog niet bestaat.

---

## 13. `check_verboden_woorden.py` — Stop-hook

Dit script staat in `.claude/hooks/` en is geen handmatig te draaien tool. Het wordt automatisch uitgevoerd na elke Claude-respons als stop-hook.

### Wat het doet

Het script leest de laatste assistent-reactie uit de conversatiecontext en zoekt naar verboden woorden en openingszinnen uit CLAUDE.md. Als er een match is, stuurt het een foutmelding terug naar Claude (exit code 2), waarna Claude de betreffende passage automatisch herschrijft.

**Verboden woorden:** cruciaal, essentieel, robuust, baanbrekend, naadloos, transformatief, katalysator, speerpunt, faciliteert, demonstreert, onderstreept, weerspiegelt, stroomlijnen, duiken in, scala aan, betekenisvol, diepgaand, genuanceerd, uitgebreid, proactief, integraal, zodoende, passie, verheugd, fosteren, testament aan

**Verboden openers:** "In de huidige samenleving...", "In een wereld waar...", "In het huidige tijdperk...", "Het is belangrijk om te benadrukken dat...", "In het kader van...", "Het is belangrijker dan ooit..."

### Uitzonderingen

- Code-blokken (` ``` ` en `` ` `` ) worden overgeslagen
- Reacties korter dan 100 tekens worden niet gecheckt
- Alleen tekst-blokken worden geanalyseerd, geen tool-resultaten

### Configuratie

De hook is geconfigureerd in `.claude/settings.json` onder `hooks.Stop`. Je kunt de woordenlijst uitbreiden door het script aan te passen.

---

## Tools combineren

De skills voeren tools in een vaste volgorde uit. Je kunt die volgorde ook handmatig nabootsen:

```bash
# Stap 1: .docx naar tekst
python3 tools/docx_to_text.py --input rapporten/mijn_rapport.docx --output .tmp/tekst.txt

# Stap 2: AI-patronen analyseren
python3 tools/humanizer_nl.py --input .tmp/tekst.txt --json > .tmp/humaniseer_resultaat.json

# Stap 3: Leesbaarheid berekenen
python3 tools/readability_nl.py --input .tmp/tekst.txt --json > .tmp/leesbaarheid.json

# Stap 4: Statistiekenkaart genereren
python3 tools/generate_review_chart.py --flesch 42.1 --ttr 0.52 --patronen 3 --risico gemiddeld > .tmp/chart.b64

# Stap 5: PDF-rapport maken
python3 tools/generate_report_pdf.py \
  --risico gemiddeld --patronen 3 --flesch 42.1 --ttr 0.52 \
  --bestandsnaam mijn_rapport.docx \
  --niveau1 "inzichten|bevindingen" \
  --waarschuwingen "3 AI-patronen gevonden" \
  --aanbevelingen "Vervang inzichten door bevindingen" \
  --chart-base64 "$(cat .tmp/chart.b64)" \
  --output .tmp/humaniseer/mijn_rapport.pdf
```
