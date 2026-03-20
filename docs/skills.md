# Skills — Gebruikersgids

DutchQuill AI heeft vier skills die je als slash-commando typt in Claude Code. Elke skill voert een volledig proces uit: van invoer tot eindbestand. Je hoeft geen tools handmatig aan te roepen.

| Skill | Wanneer gebruiken | Output |
|-------|------------------|--------|
| `/schrijven` | Nieuwe rapporttekst schrijven | `.docx` |
| `/herschrijven` | Bestaande tekst verbeteren | `.docx` |
| `/reviewen` | Rapport nakijken voor inlevering | `.pdf` |
| `/humaniseer` | Snelle AI-detectiecheck | `.pdf` |

Twijfel je welke skill je nodig hebt? Gebruik `/herschrijven` als je al tekst hebt. Gebruik `/schrijven` als je nog niets op papier hebt.

---

## `/schrijven` — Nieuwe academische tekst

### Wat doet het

De skill schrijft een nieuwe rapportsectie of volledig rapport in formeel academisch Nederlands. Het proces controleert APA 7e editie, grammatica en AI-patronen voordat het iets aanbiedt.

### Wat je aanlevert

**Verplicht:**
- Onderwerp of onderzoeksvraag
- Sectie: `inleiding`, `methode`, `resultaten`, `discussie`, `conclusie` of `volledig rapport`
- Doelgroep: `docent`, `opdrachtgever` of `examencommissie`
- Opleidingsniveau: `HBO bachelor`, `HBO master` of `MBO`

**Optioneel:**
- Gewenst woordenaantal
- Beschikbare bronnen (ruwe data of APA-referenties)
- Invalshoek of centrale vraag
- Figuren als `.jpg` of `.png`

### Sectietypes

Elk sectiontype heeft zijn eigen eisen:

| Sectie | Bijzonderheden |
|--------|---------------|
| `inleiding` | Geen aankondigingskop ("Inleiding" is de documenttitel) |
| `methode` | Bevat: onderzoeksdesign, steekproef, dataverzameling, analyse, ethische overwegingen |
| `resultaten` | Alleen bevindingen, geen interpretatie |
| `discussie` | Interpretatie, beperkingen, vergelijking met literatuur |
| `conclusie` | Beantwoording van de centrale vraag, concrete afsluiting |
| `volledig rapport` | Bevat verplicht een samenvatting (150–250 woorden) met `Sleutelwoorden:` |

### Figuren toevoegen

Lever figuren aan als `.jpg` of `.png`. De skill plaatst de figuur op de juiste plek, schrijft een APA-conforme bijschriftregel en zorgt dat de in-tekst verwijzing (`zie Figuur X`) vóór de figuur staat.

### [BRON NODIG]-markers

Als een claim een bron nodig heeft die je niet aanlevert, plaatst de skill `[BRON NODIG - reden]` in de tekst. Die markers blijven staan in de `.docx`. Jij vult de bron in voordat je inlevert.

### Output

- `.tmp/schrijven/<titel>.docx` — APA-conforme Word-bestanden
- `.tmp/history.json` — logboekregel van deze sessie

---

## `/herschrijven` — Bestaande tekst verbeteren

### Wat doet het

De skill analyseert je tekst, bepaalt wat er verbeterd moet worden en herschrijft gericht. Je kiest zelf het doel. Na het herschrijven vergelijkt de skill de voor- en naversie met een woorddiff en een scoreoverzicht.

### Wat je aanlevert

**Verplicht:**
- De originele tekst (plak direct of geef een `.docx`-pad op)
- Het doel (zie subtypes hieronder)
- Bevestiging dat de bedoeling van de tekst bewaard moet blijven

**Optioneel:**
- Doelgroep
- Specifieke instructies ("maak korter", "verwijder herhaling", "houd alinea 2 intact")

### Subtypes

Je kiest één van de zes doelen:

| Doel | Wat er verandert |
|------|-----------------|
| `verbeteren` | Taal, APA, stijl en AI-patronen tegelijk |
| `parafraseren` | Zelfde inhoud, andere formulering. Bronvermelding blijft verplicht |
| `humaniseren` | AI-woorden en formulaïsche zinnen vervangen door menselijkere taal |
| `APA-correctie` | Alleen citaties, koppen en literatuurlijst aanpassen |
| `formaliseren` | Informele taal omzetten naar academisch register |
| `inkorten` | Overbodige zinnen verwijderen zonder inhoudsverlies |

### Vergelijkingsoverzicht

Na het herschrijven toont de skill:
- Beide versies naast elkaar (origineel en herschreven)
- Welke wijzigingen zijn aangebracht en waarom
- De verandering in AI-risicoscore (bv. Hoog → Laag)
- Alle `[BRON NODIG]`-markers expliciet benoemd

### Output

- `.tmp/herschrijven/<titel>.docx` — herschreven versie als Word-bestand
- `.tmp/history.json` — logboekregel van deze sessie

---

## `/reviewen` — Rapport nakijken

### Wat doet het

De skill beoordeelt je tekst op vier domeinen en levert een volledig reviewrapport als PDF. In de chat zie je een korte samenvatting. De details staan in het PDF-bestand.

### Wat je aanlevert

**Verplicht:**
- De te reviewen tekst (plak direct of geef een `.docx`-pad op)

**Optioneel:**
- Type review (standaard: volledig — zie hieronder)
- Opleidingsniveau
- Specifieke aandachtspunten ("check vooral de literatuurlijst")

### Vier reviewdomeinen

Een volledige review dekt alle vier domeinen:

**Domein 1 — Taalcorrectheid**
De/het, d/t-fouten, samenstellingen, kommaregels, werkwoordsvormen, consistentie in terminologie.

**Domein 2 — APA 7e editie**
Titelpagina, koppenstructuur (geen nummers tenzij instelling het vereist), in-tekst citaties, literatuurlijst (hangend inspringen, alfabetisch, DOI als hyperlink, italieflettertype voor titels), tabellen, figuren en bijlagen.

**Domein 3 — Humanisering**
AI-patronen in 20 categorieën. Risicoscore (0–2 Laag / 3–6 Gemiddeld / 7+ Hoog). De top drie gevonden patronen staan met context en alternatieven in het rapport.

**Domein 4 — Structuur**
Macrostructuur (zijn alle secties aanwezig?), mesostructuur (één idee per alinea, topic sentence aanwezig?), microstructuur (geen wees-zinnen, geen herhaling zonder nieuwe informatie).

### Partiële review

Wil je niet het volledige pakket? Geef een specifiek domein op:

```
/reviewen — alleen APA
/reviewen — alleen taal
/reviewen — alleen humanisering
```

Bij een partiële review controleert de skill het gevraagde domein volledig. Grote problemen in de andere domeinen benoemt het kort, maar worden niet uitgewerkt.

### Eindoordeel

Het reviewrapport sluit af met één van drie adviezen:
- **Klaar voor inlevering** — geen of alleen kleine punten
- **Kleine aanpassingen nodig** — concrete lijst met correcties
- **Herschrijven aanbevolen** — structurele problemen, gebruik `/herschrijven`

### Output

- `.tmp/reviewen/<titel>.pdf` — volledig reviewrapport
- Korte samenvatting in de chat (datum, status per domein, volgende stap)
- `.tmp/history.json` — logboekregel van deze sessie

---

## `/humaniseer` — Snelle AI-detectiecheck

### Wat doet het

De skill analyseert ingeplakte tekst op AI-patronen en geeft een risicoscore. Het is de snelste manier om te checken of tekst "AI-achtig" klinkt. Het proces voert geen grammaticacheck of APA-check uit — dat doet `/reviewen`.

### Wat je aanlevert

- Tekst (plak direct in de chat of geef een `.docx`-pad op)
- Minimaal 100 woorden voor betrouwbare statistische analyse. Bij minder dan 100 woorden werkt de woorddetectie nog wel, maar zijn de Flesch-Douma score en MATTR minder betrouwbaar.

### Wat je terugkrijgt

In de chat:
- Risicoscore en niveau (Laag / Gemiddeld / Hoog)
- Top 3 gevonden patronen met context en een alternatief
- Oxford comma-bevindingen
- Anglicismen met alternatieven
- Concrete aanbeveling (kleine aanpassing / herschrijf deze alinea's / start `/herschrijven`)

Als PDF:
- Volledig analyserapport met scores, patronen en reviewchart

### Wanneer `/humaniseer` en wanneer `/herschrijven`

| Situatie | Aanbevolen skill |
|----------|-----------------|
| Je wilt weten of tekst AI-achtig klinkt | `/humaniseer` |
| Je wilt de tekst ook daadwerkelijk verbeteren | `/herschrijven` met doel `humaniseren` |
| Je wilt een volledige kwaliteitscheck | `/reviewen` |

### Output

- `.tmp/humaniseer/<titel>.pdf` — analyserapport
- `.tmp/history.json` — logboekregel van deze sessie

---

## Invoer via .docx-bestand

Alle vier skills werken met `.docx`-bestanden als invoer. Zet het bestand in de map `rapporten/` en verwijs ernaar:

```
Verwerk rapporten/mijn_rapport.docx
```

De skill converteert het bestand automatisch naar tekst. Opmaak als **vet** en *cursief* blijft bewaard.

---

## Gebruikersprofiel

Als `config/user_profile.json` bestaat, haalt de skill daar standaardwaarden vandaan voor de titelpagina: naam, studentnummer, instelling, faculteit, opleiding en docent. De skill vraagt altijd om bevestiging voordat het die gegevens gebruikt.

Het profiel is niet verplicht. Zie [docs/configuratie.md](configuratie.md) voor het instellen.

---

## Geschiedenis raadplegen

Elke uitgevoerde skill schrijft een logboekregel naar `.tmp/history.json`. Dat bestand bevat de datum, het type skill, de titel en de volledige output. Je kunt het bestand openen om eerder gegenereerde teksten terug te vinden.
