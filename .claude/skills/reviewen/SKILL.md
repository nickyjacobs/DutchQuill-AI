---
name: reviewen
description: Start de rapport_reviewen workflow. Gebruik dit wanneer de gebruiker een rapport of sectie wil laten nakijken op taal, APA, humanisering en structuur. Activeer proactief bij vragen als "check dit rapport", "nakijken", "review", "klaar voor inlevering?", "controleer mijn tekst".
model: sonnet
---

Je voert de `rapport_reviewen.md` workflow uit. Alle vier domeinen zijn verplicht bij een volledige review. Sla GEEN stap over.

## Stap 0a — Gebruikersprofiel laden [OPTIONEEL]

Controleer of `config/user_profile.json` bestaat. Zo ja:
- Lees het bestand met de Read tool
- Gebruik de gegevens als context bij de review (bijv. instelling voor APA-titelpaginacheck)

Zo nee: ga gewoon door — het profiel is optioneel.

## Stap 0b — Invoer voorbereiden [VERPLICHT]

**Als de invoer een .docx bestand is, converteer dit ALTIJD eerst [VERPLICHT]:**
```bash
python3 tools/docx_to_text.py --input <pad naar .docx>
```
Sla het resultaat op als `.tmp/tekst.txt`.

Als de invoer platte tekst is: schrijf deze naar `.tmp/tekst.txt`.

## Stap 1 — Invoer en gidsen laden [VERPLICHT]

| Veld | Verplicht? |
|------|-----------|
| Te reviewen tekst | Ja |
| Type review (volledig / alleen APA / alleen taal / alleen humanisering) | Nee — standaard: volledig |
| Opleidingsniveau | Nee |
| Specifieke zorgen | Nee |

**Lees de volgende gidsen met de Read tool [VERPLICHT]:**

1. `workflows/taal_gids.md` — voor Domein 1 (taalcorrectheid, afkortingen, samenstellingen, kommaregels)
2. `workflows/apa_nl_gids.md` — voor Domein 2 (APA 7e editie, titelpagina, koppen, citaties, literatuurlijst, figuren)
3. `workflows/humanize_nl_gids.md` — voor Domein 3 (AI-patroondetectie, Niveau 1/2-woorden, Oxford comma, anglicismen)
4. `workflows/academische_stijl_gids.md` — voor Domein 2 + 4 (schrijfstijl, registers, structuur)

Sla deze stap NOOIT over. De gidsen bevatten de volledige checklists en regels die je in de domeinen toepast.

## Domein 1 — Nederlandse Taalcorrectheid [VERPLICHT]

**Voer grammar_check.py uit [VERPLICHT]:**
```bash
python3 tools/grammar_check.py --input .tmp/tekst.txt
```
Verifieer de bevindingen zelf op basis van `workflows/taal_gids.md`. Controleer ook items die de tool niet detecteert.

Controleer:
- Werkwoordsvervoeging (d/t-fouten)
- Lidwoorden (de/het)
- Samenstellingen (los/vast schrijven, koppeltekens bij afkortingen: SSH-verbinding, SUID-binary)
- Zinsconstructies (congruentie, tangconstructies)
- Kommaregels (opsommingen, bijzinnen, tussenzinnen)
- Woordkeuze (geen Anglicismen, geen spreektaal)
- Consistentie in tijdsgebruik en terminologie
- Afkortingen: eerste gebruik = volledige term + afkorting tussen haakjes (bijv. "Capture The Flag (CTF)")

## Domein 2 — APA 7e Editie [VERPLICHT]

**Voer apa_checker.py uit [VERPLICHT]:**
```bash
python3 tools/apa_checker.py --input .tmp/tekst.txt
```

**Bronformattering [ALLEEN als ruwe brondata beschikbaar is]:**
```bash
python3 tools/source_formatter.py --input .tmp/bronnen.json
```

Controleer op basis van `workflows/apa_nl_gids.md`:
- Titelpagina (instelling, titel, auteur, studentnummer, opleiding, begeleider, datum, geen running head)
- Koppen (APA-hierarchie: Niveau 1-5, geen nummering, geen kop "Inleiding", minimaal twee per niveau)
- Bronvermelding in tekst (formaat per auteurssituatie, geen voornamen, geen & in lopende tekst)
- Literatuurlijst (hanging indent, alfabetisch, DOI als hyperlink, cursieve titels, sentence case, geen locatie)
- Tabellen (nummer + titel boven, geen verticale lijnen)
- Figuren (8-punts checklist hieronder)
- Bijlagen (na literatuurlijst, elk op nieuwe pagina, vet gecentreerde titel)

**Figuurchecklist (8 punten):**
- [ ] Label `Figuur X` **boven** de figuur, vet + cursief (APA 7)
- [ ] Caption direct na label, eindigt met punt
- [ ] In-tekst verwijzing "(zie Figuur X)" staat voor de figuur
- [ ] Nummering doorlopend
- [ ] Bronvermelding als figuur van elders komt
- [ ] Figuur inhoudelijk relevant op die plek
- [ ] Caption beschrijft wat de figuur toont (niet generiek)
- [ ] Figuur vermeld in hoofdtekst (niet alleen in bijlage)

Let op: de apa_checker.py kan false positives geven (bijv. & in brontitels). Verifieer bevindingen altijd handmatig.

## Domein 3 — Humanisering [VERPLICHT]

**Roep de `tekst-analist` subagent aan [VERPLICHT]:**
Geef `.tmp/tekst.txt` als input. De agent voert `humanizer_nl.py --json` en `readability_nl.py --json` uit en rapporteert:
- Risicoscore en risiconiveau
- Top-3 Niveau 1-patronen met alternatieven
- Oxford comma-bevindingen
- Anglicisme-bevindingen met alternatieven
- MATTR en Flesch-Douma score

**Noteer de volgende scores — deze zijn nodig voor Stap 5 (reviewchart):**
- Flesch-Douma score
- TTR (MATTR)
- Aantal patronen
- Risiconiveau (laag/gemiddeld/hoog)

**Fallback:** Als de tekst-analist geen output geeft, voer de tools handmatig uit:
```bash
python3 tools/humanizer_nl.py --input .tmp/tekst.txt --suggest
python3 tools/readability_nl.py --input .tmp/tekst.txt
```

Controleer op basis van `workflows/humanize_nl_gids.md`:
- Niveau 1-woorden (altijd vervangen)
- Niveau 2-dichtheid
- Formulaische openers
- Vullingszinnen
- Zinslengtevariatie
- TTR >= 0.45
- Specifieke details aanwezig
- Geen em dashes
- Geen Oxford comma ("X, Y, en Z" -> "X, Y en Z")
- Geen vage bronvermeldingen

Risicoscore: 0-2 laag / 3-6 gemiddeld / 7+ hoog.

## Domein 4 — Structuur [VERPLICHT]

Controleer op basis van `workflows/academische_stijl_gids.md`:
- **Macrostructuur:** vereiste secties aanwezig, logische volgorde, proportionele lengte, rode draad herkenbaar, conclusie beantwoordt centrale vraag
- **Mesostructuur:** een gedachte per alinea, topic sentences, overgangen tussen alinea's, max 150-200 woorden per alinea
- **Microstructuur:** geen weesinnen, geen onverwachte onderwerpswisselingen, geen herhaling zonder nieuwe informatie
- Terminologieconsistentie (zelfde term voor zelfde concept)

## Feedbackformaat

Geef de review als gestructureerd rapport:

```
## Reviewrapport

**Datum:** [datum]
**Beoordeeld onderdeel:** [naam/sectie]

---

### 1. Taalcorrectheid
Status: Correct / Kleine aandachtspunten / Structurele fouten

[Specifieke bevindingen — citeer zin uit tekst + correctie]

---

### 2. APA Compliance
Status: Volledig correct / Aanpassingen nodig / Meerdere fouten

[Per onderdeel: correct of fout + correctie]

---

### 3. Humanisering
Risicoscore: Laag / Gemiddeld / Hoog

[Gevonden patronen met voorbeeldzin + suggestie voor vervanging]

---

### 4. Structuur
Status: Sterk / Aandachtspunten / Herstructurering aanbevolen

[Bevindingen per structuurniveau: macro, meso, micro]

---

### Eindoordeel
Klaar voor inlevering / Kleine aanpassingen nodig / Herschrijven aanbevolen

**Volgende stap:** [concrete actie]
```

## Stap 5 — Reviewchart genereren [VERPLICHT]

Gebruik de scores uit Domein 3 (tekst-analist of handmatige tools):
```bash
python3 tools/generate_review_chart.py --flesch <score> --ttr <score> --patronen <n> --risico <laag|gemiddeld|hoog>
```

**Let op:** Gebruik ALTIJD het `score` veld uit de `humanizer_nl.py --json` output als waarde voor `--patronen`. Dit getal bevat alle penalties al (inclusief Flesch-Douma < 30). Tel NOOIT handmatig een Flesch-Douma penalty bij de score op.

Sla de base64-output op — deze wordt meegegeven als `chartImage` in de metadata van Stap 6.

## Stap 6 — History opslaan + PDF genereren [VERPLICHT]

Voer dit altijd uit na het afronden van alle domeinen.

**Stap 6a — Schrijf het volledige reviewrapport naar .tmp/review_output.txt:**
Sla de volledige markdown-output (het rapport van ## Reviewrapport t/m ### Eindoordeel) op als `.tmp/review_output.txt`.

**Stap 6b — Sla op in geschiedenis:**
```bash
python3 tools/history_writer.py \
  --type reviewen \
  --titel "<bestandsnaam of eerste 80 chars van de beoordeelde tekst>" \
  --metadata '{"reviewType":"volledig","chartImage":"<base64 output van Stap 5>"}' \
  --output-file .tmp/review_output.txt
```

**Stap 6c — Genereer review-PDF [VERPLICHT]:**

Leid de domeinbeoordelingen af uit de reviewresultaten:
- `--domein-scores`: geef per domein een korte statuslabel, bijv.:
  `"1. Taalcorrectheid:Kleine aandachtspunten||2. APA Compliance:Aanpassingen nodig||3. Humanisering:Gemiddeld risico||4. Structuur:Sterk"`
  Gebruik als statuslabel: `Correct`, `Kleine aandachtspunten`, `Aanpassingen nodig`, `Structurele fouten`, `Sterk`, `Gemiddeld risico`, `Hoog risico`
- `--apa-bevindingen`: specifieke APA-bevindingen als pipe-separated lijst (uit Domein 2)
- `--stijl-bevindingen`: specifieke stijl/structuurbevindingen als pipe-separated lijst (uit Domein 4)
- `--waarschuwingen`: overige taal- en humaniseringsbevindingen (Domein 1 + 3)

```bash
python3 tools/generate_report_pdf.py \
  --rapport-type reviewen \
  --risico <laag|gemiddeld|hoog> \
  --patronen <n> \
  --flesch <score> \
  --ttr <score> \
  --bestandsnaam "<bestandsnaam van het beoordeelde rapport>" \
  --niveau1 "<patroon1>|<alt1>||<patroon2>|<alt2>" \
  --domein-scores "1. Taalcorrectheid:<status>||2. APA Compliance:<status>||3. Humanisering:<status>||4. Structuur:<status>" \
  --apa-bevindingen "<apa-bevinding1>|<apa-bevinding2>|..." \
  --stijl-bevindingen "<stijl-bevinding1>|<stijl-bevinding2>|..." \
  --waarschuwingen "<taal- en humaniseringsbevindingen>|..." \
  --aanbevelingen "<aanbeveling1>|<aanbeveling2>" \
  --chart-file .tmp/review_chart.b64 \
  --output .tmp/reviewen/<titel>.pdf
```

**Stap 6d — Werkbestanden opruimen:**
Verwijder tussenbestanden uit `.tmp/` root (bijv. `tekst.txt`, `review_output.txt`, `review_chart.b64`). Alleen het eindproduct in `.tmp/reviewen/` blijft bewaard.

## Stap 7 — Presentatie in chat [VERPLICHT]

Presenteer een **korte samenvatting** in de chat (NIET het volledige rapport):

```
## Review-samenvatting

**Beoordeeld:** <bestandsnaam>
**Eindoordeel:** Klaar voor inlevering / Kleine aanpassingen nodig / Herschrijven aanbevolen

### Belangrijkste bevindingen
- **Taal:** <1 zin status>
- **APA:** <1 zin status>
- **Humanisering:** <risiconiveau> (<X> patronen)
- **Structuur:** <1 zin status>

**Volgende stap:** <concrete actie>

Volledig reviewrapport beschikbaar als `.tmp/reviewen/<titel>.pdf`
```

## Stap 8 — Verificatiechecklist [VERPLICHT]

Bevestig intern dat ALLE stappen zijn uitgevoerd. Als een stap is overgeslagen, ga terug en voer deze alsnog uit.

- [ ] Stap 0b: Tekst beschikbaar als .tmp/tekst.txt
- [ ] Stap 1: Alle 4 gidsen gelezen met Read tool (taal_gids, apa_nl_gids, humanize_nl_gids, academische_stijl_gids)
- [ ] Domein 1: grammar_check.py uitgevoerd
- [ ] Domein 2: apa_checker.py uitgevoerd
- [ ] Domein 3: tekst-analist subagent aangeroepen (of fallback tools handmatig)
- [ ] Domein 4: structuurcheck handmatig uitgevoerd
- [ ] Stap 5: generate_review_chart.py uitgevoerd
- [ ] Stap 6a: review_output.txt geschreven
- [ ] Stap 6b: history_writer.py uitgevoerd
- [ ] Stap 6c: generate_report_pdf.py uitgevoerd → .tmp/reviewen/<titel>.pdf
- [ ] Stap 7: Korte samenvatting in chat gepresenteerd

ALS een tool een fout gaf: vermeld dit in het reviewrapport bij het betreffende domein. Een toolfout is GEEN reden om de tool over te slaan — probeer het opnieuw of rapporteer de fout.
