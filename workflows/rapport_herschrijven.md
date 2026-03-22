# Workflow: Rapport Herschrijven

## Doel
Verbeter, herschrijf of parafraseer bestaande tekst zodat deze beter aansluit bij
academisch Nederlands, APA 7e editie richtlijnen en een menselijke schrijfstijl.

## Wanneer gebruik je deze workflow?
- Er is al **bestaande tekst** die verbeterd moet worden
- De tekst is te AI-achtig, te informeel, te wollig of te slordig
- De gebruiker wil een passage parafraseren (bijv. voor originele formulering)
- De structuur klopt maar de taalkundige kwaliteit schiet tekort

Gebruik in plaats hiervan `rapport_schrijven.md` als er nog geen tekst bestaat.

---

## Stap 0: Gebruikersprofiel laden [OPTIONEEL]

Controleer of `config/user_profile.json` bestaat. Zo ja:
- Lees het bestand met de Read tool
- Gebruik de gegevens als context voor de herschrijving (bijv. instelling, opleiding, vak)
- Stel een bevestigingsvraag als de gegevens relevant zijn voor de titelpagina

Zo nee: ga gewoon door — het profiel is optioneel.

---

## Stap 1: Invoer Verzamelen

**Word-bestand als invoer:** Als de gebruiker een `.docx` bestandspad aanlevert in plaats van geplakte tekst, lees de inhoud eerst uit:
```bash
python3 tools/docx_to_text.py --input <pad naar .docx>
```
`docx_to_text.py` extraheert automatisch inline afbeeldingen naar `.tmp/images/figure_NN.ext` en schrijft `![caption](pad)` Markdown-placeholders in de tekst. `md_to_docx.py` plaatst de afbeeldingen bij de generatie van de .docx terug op hun originele plek. Gebruik NOOIT `--no-images` bij het herschrijven van een rapport met figuren.

Gebruik de geëxtraheerde tekst als de te herschrijven tekst en ga verder met de rest van de stap.

**Stap 1b — Figuren inventariseren [indien aanwezig]:**
1. Controleer of `.tmp/images/` bestanden bevat (geëxtraheerd door `docx_to_text.py`)
2. Lees elke afbeelding met de Read tool om de inhoud te begrijpen
3. Noteer per figuur: bestandsnaam, wat de afbeelding toont, logische positie in de tekst
4. Behoud `![caption](pad)` placeholders in de herschreven tekst op de juiste plek
5. Pas APA-figuurreferenties aan: "zie Figuur X" moet altijd vóór de figuur staan
6. Nieuwe figuren die de gebruiker aanlevert: kopieer naar `.tmp/images/` en voeg een `![caption](pad)` placeholder toe

**Rapporten-map als invoer:** De map `rapporten/` bevat eerder aangeleverde rapportbestanden (.docx). Als de gebruiker verwijst naar een bestaand rapport zonder volledig pad, zoek in `rapporten/`. Converteer met `docx_to_text.py`.

| Invoer | Beschrijving | Verplicht? |
|--------|-------------|-----------|
| Originele tekst | De tekst die herschreven moet worden | **Ja** |
| Doel | Verbeteren / parafraseren / humaniseren / APA-correctie / toonverbetering | **Ja** |
| Intentie behouden | Moet de betekenis volledig bewaard blijven? | **Ja** |
| Doelgroep | Voor wie is de eindversie bedoeld? | Nee |
| Specifieke instructies | Bijv. "maak het formeler", "maak het korter", "verwijder herhaling" | Nee |
| Figuren | Nieuwe screenshots (.jpg, .jpeg, .png) toe te voegen, of bestaande te controleren | Nee |

---

## Stap 2: Gidsen laden + tekst analyseren [VERPLICHT]

**Lees de volgende gidsen met de Read tool [VERPLICHT]:**
1. `workflows/taal_gids.md` — taalfouten, afkortingen, samenstellingen, kommaregels
2. `workflows/humanize_nl_gids.md` — AI-patronen, Niveau 1/2-woorden, formulaische openers
3. `workflows/apa_nl_gids.md` — citaties, koppen, literatuurlijst
4. `workflows/academische_stijl_gids.md` — schrijfstijl, registers, naamwoordstijl
5. `.claude/rules/schrijfstijl.md` — 28 verboden woorden en 6 verboden openers die NIET volledig in de gidsen staan

### Stap 2a — Schrijfklaar-check (intern, niet tonen aan gebruiker)

Bevestig voordat je begint met herschrijven:
- [ ] Alle 5 gidsen gelezen (taal, humanize_nl, apa, academische_stijl, schrijfstijl)
- [ ] Verboden woorden genoteerd (28 woorden uit `.claude/rules/schrijfstijl.md`)
- [ ] Verboden openers genoteerd (6 patronen uit schrijfstijl.md)
- [ ] `[BRON NODIG - reden]` format voor ontbrekende bronnen
- [ ] Figuren: in-text verwijzing VOOR de afbeelding

**Voer de volgende analysetools uit op het origineel [VERPLICHT]:**
```bash
# Grammatica- en spellingcheck:
python3 tools/grammar_check.py --input .tmp/origineel.txt

# Humanizer voor een eerste AI-risicoscore:
python3 tools/humanizer_nl.py --input .tmp/origineel.txt --suggest
```

Voordat je één woord wijzigt, analyseer je de tekst op vier gebieden:

1. **Inhoud** - Wat is de kernboodschap? Wat wil de auteur zeggen?
2. **Structuur** - Is de opbouw logisch? Welke alinea's hangen samen?
3. **Problemen** - Ga systematisch per categorie door:

### Taalfouten - zie `taal_gids.md`
- [ ] D/T-fouten (werkwoordsvervoeging, voltooid deelwoord)
- [ ] Samenstellingen onjuist los- of aaneengeschreven
- [ ] Verkeerde verwijswoorden (dat/die/wat)
- [ ] Congruentiefouten (onderwerp ↔ persoonsvorm)
- [ ] Kommafouten
- [ ] Onjuiste apostrofs of aanhalingstekens

### AI-patronen - zie `humanize_nl_gids.md`
- [ ] Niveau 1-woorden aanwezig? → lijst ze op met locatie
- [ ] Niveau 2-woorden bij hoge dichtheid?
- [ ] Formulaïsche openers (Type 1: brede aanloop / Type 2: aankondiging / Type 3: herhaling)?
- [ ] Vullingszinnen?
- [ ] Uniform zinsritme (vijf of meer zinnen van gelijke lengte)?
- [ ] Alinea's die telkens met hetzelfde woord beginnen?

### APA-overtredingen - zie `apa_nl_gids.md`
- [ ] Voornamen in citaties?
- [ ] "&" in lopende tekst (moet "en" zijn)?
- [ ] Directe citaten zonder paginanummer?
- [ ] Directe citaten zonder aanhalingstekens, of blokcitaatfouten?
- [ ] Referenties die ontbreken in de literatuurlijst (of andersom)?

### Schrijfstijlproblemen - zie `academische_stijl_gids.md`
- [ ] Spreektaal of informele uitdrukkingen ("best wel", "eigenlijk", "best")?
- [ ] Naamwoordstijl ("het + werkwoord", voorzetselgroepen zoals "in het kader van")?
- [ ] Onnodig passief (handelende persoon is bekend maar wordt weggelaten)?
- [ ] Persoonlijke voornaamwoorden (ik/je/we) in de hoofdtekst?
- [ ] Verkeerde werkwoordstijden per sectietype?
- [ ] Verboden woorden (uiteraard, eigenlijk, heel veel, maar liefst)?

### Structuurproblemen
- [ ] Herhaling van dezelfde gedachte in één alinea?
- [ ] Alinea behandelt meer dan één onderwerp?
- [ ] Geen duidelijke topic sentence?
- [ ] Logische gaten (ontbrekende redenering tussen zinnen)?

### Toonproblemen
- [ ] Te informeel voor de doelgroep?
- [ ] Te stijf of wollig (omslachtige formuleringen)?
- [ ] Te vaag (geen specifieke details, alleen algemeenheden)?

### Figuren (volg EXACT `apa_nl_gids.md § 10`)
- [ ] Label + caption APA-conform volgens `apa_nl_gids.md § 10`?
- [ ] In-tekst verwijzing vóór de figuur? ("zie Figuur X" moet altijd vóór de figuur staan)
- [ ] Figuur inhoudelijk op de juiste plek?
- [ ] Nieuwe figuren aangeleverd? → verwerk via `rapport_schrijven.md` Stap 3b

**Noteer per gevonden probleem:** categorie + locatie (alinea/zin) + voorgestelde oplossing.

---

### Prioriteitsmatrix

| Ernst | Type probleem | Actie |
|-------|--------------|-------|
| Hoog | Niveau 1-woorden, feitelijke fouten, ontbrekende bronnen | Altijd corrigeren |
| Midden | APA-opmaak, passief overgebruik, toonproblemen | Corrigeren tenzij gebruiker expliciet anders aangeeft |
| Laag | Kommavoorkeur, synoniemkeuze, kleine stijlnuances | Alleen corrigeren als het de leesbaarheid verbetert |

---

## Stap 3: Bepaal de Aanpak

Kies op basis van de analyse:

| Probleem | Aanpak |
|----------|--------|
| AI-patronen maar verder goed | Gerichte woord- en zinsvervangingen |
| Inhoudelijk sterk maar slecht geformuleerd | Herschrijven per alinea, behoud structuur |
| Verkeerde toon | Volledige herformulering in juist register |
| Feitelijke fouten | Markeer, vraag gebruiker om verificatie - wijzig nooit feiten zelfstandig |
| Ontbrekende APA-elementen | Voeg toe of corrigeer zonder inhoud te wijzigen |
| Parafrase van een bron | Herschrijf volledig in eigen woorden + voeg (Auteur, jaar) toe |
| Tekst bijna volledig incorrect | Vraag of je opnieuw schrijft via `rapport_schrijven.md` |

---

## Stap 4: Herschrijf de Tekst

**Behoud altijd:**
- De kernboodschap en intentie van de auteur
- Feitelijke informatie en statistieken
- Bestaande correcte bronvermeldingen

**Verbeter altijd:**
- Zinsbouw die te lang, te kort of te repetitief is
- Woordkeuze die AI-achtig klinkt (zie `humanize_nl_gids.md`)
- APA-opmaak die incorrect is (zie `apa_nl_gids.md`)
- Passieve constructies die onnodig zijn

**Vraag altijd aan de gebruiker:**
- Of feitelijke informatie correct is als je twijfelt
- Of de intentie bewaard is gebleven bij ingrijpende wijzigingen
- Of specifieke woorden of formuleringen bewaard moeten blijven

---

## Stap 5: [VERPLICHT] APA-Check

**Voer apa_checker.py uit [VERPLICHT]:**
```bash
python3 tools/apa_checker.py --input .tmp/herschreven.txt
```

**Bronformattering [ALLEEN als ruwe brondata beschikbaar is]:**
```bash
python3 tools/source_formatter.py --input .tmp/bronnen.json
```

Controleer na het herschrijven:

1. Zijn alle bronvermeldingen in de tekst correct opgemaakt? (zie `apa_nl_gids.md` § 5)
2. Zijn directe citaten juist weergegeven? (zie `apa_nl_gids.md` § 6)
3. Als er koppen zijn aangepast: kloppen de niveaus nog? (zie `apa_nl_gids.md` § 3)
4. Zijn er [BRON NODIG]-plaatsen die de gebruiker zelf moet invullen? Markeer ze expliciet.

### [BRON NODIG] - Formele conventie

Gebruik deze marker wanneer een claim een bron vereist maar die bron niet beschikbaar of verifieerbaar is.

**Format (inline):**
```
[BRON NODIG - <reden>]
```
Gebruik een gewoon koppelteken ` - `, geen em dash `—`.

**Voorbeelden:**
- `Dit bleek in de praktijk vaak voor te komen [BRON NODIG - geen bron aangeleverd].`
- `Volgens onderzoek is X de meest gebruikte aanpak [BRON NODIG - welk onderzoek?].`

**In de literatuurlijst:**
Vervang een ontbrekende of onvolledige entry door:
```
Auteur. (jaar). [BRON NODIG - voeg volledige APA-vermelding toe]
```

**Gedrag bij export:**
- [BRON NODIG]-markers **blijven staan** in het .docx bestand - de student lost ze zelf op.
- Noem alle [BRON NODIG]-markeringen **altijd expliciet** bij de toelichting in Stap 8.
- Voer `apa_checker.py` uit na het herschrijven - de tool pikt bestaande [BRON NODIG]-markers niet op, maar jij controleert handmatig of alle claims een geldige bron hebben.

---

## Stap 6: [VERPLICHT] Humaniseringscheck

Voer ook na het herschrijven een volledige humaniseringscheck uit.

**Voer de volgende tools uit [VERPLICHT]:**
```bash
# Humanizer met alternatieven per gevonden patroon:
python3 tools/humanizer_nl.py --input .tmp/herschreven.txt --suggest

# Leesbaarheidsindex (Flesch-Douma, gemiddelde zinslengte, lettergrepen):
python3 tools/readability_nl.py --input .tmp/herschreven.txt
```

**Roep de `tekst-analist` subagent aan [VERPLICHT]:**
Geef `.tmp/herschreven.txt` als input. De agent voert `humanizer_nl.py --json` en `readability_nl.py --json` uit en rapporteert risicoscore, top-3 patronen met alternatieven, Oxford comma, anglicismen, MATTR en Flesch-Douma in één overzicht.

**Fallback:** Als de tekst-analist geen output geeft, gebruik de handmatige tool-output hierboven.

### Acceptatiedrempels - wanneer is de tekst klaar?

| Maat | Drempelwaarde | Actie bij overschrijding |
|------|---------------|--------------------------|
| Humanizer risicoscore | ≤ 2 = Laag ✓ | Acceptabel, geen actie |
| | 3 – 6 = Gemiddeld | Herschrijf de alinea's met de hoogste patternscore |
| | 7+ = Hoog | Herbeschouw volledige secties; overweeg volledig herschrijven |
| Flesch-Douma (HBO) | 30 – 50 ✓ | Acceptabel voor HBO-niveau |
| | < 30 | Te moeilijk - overweeg zinssplitsing of simpeler woordkeuze |
| | > 65 | Te eenvoudig voor academisch niveau |
| MATTR | ≥ 0.75 ✓ | Voldoende vocabulairevariatie |
| | < 0.75 | Vervang herhaalde zelfstandig naamwoorden door synoniemen of pronomen |
| APA-overtredingen | 0 kritieke fouten ✓ | Kritiek: ontbrekende pagina's bij directe citaten, z.d. zonder suffix, voornamen |

**Volledige gids toepassen [VERPLICHT]:**
`humanize_nl_gids.md` bevat meer dan wat de tools detecteren. Controleer handmatig op:
- Sectietype-specifieke regels (Cat. 9): passief beoordelen per sectietype
- Burstiness (Cat. 3): kort-lang afwisseling bewust toepassen
- Leesbaarheid vs. humanisering (Cat. 11): Flesch-Douma mag niet verslechteren
- Communicatievormen (Cat. 4): geen helper-taal, geen retorische vragen, geen meta-commentaar
- Whitelist (Cat. 10): geflagde termen controleren op vakterm-legitimiteit
- N-gram repetitie (Cat. 3): herhalende woordcombinaties over de hele tekst
- Voor/na-voorbeeld (onderaan gids): gebruik als ijkpunt

1. Controleer de herschreven tekst op Niveau 1-woorden (`humanize_nl_gids.md` § Categorie 1) → vervang
2. Controleer op formulaïsche structuren (`humanize_nl_gids.md` § Categorie 2) → herschrijf
3. Controleer zinslengtevariatie → varieer waar nodig
4. Controleer of er nieuwe AI-patronen zijn geïntroduceerd tijdens het herschrijven
5. Gebruik de snelcheck (`humanize_nl_gids.md` § Snelcheck) op de volledige tekst

---

## Stap 7: Vergelijkingscheck

**Voer de volgende vergelijkingstools uit [VERPLICHT]:**
```bash
# Woorddiff - toont wat is toegevoegd, gewijzigd of verwijderd:
python3 tools/diff_viewer.py --original .tmp/origineel.txt --rewritten .tmp/herschreven.txt

# Score-vergelijking - toont verbetering in AI-score voor/na:
python3 tools/humanizer_nl.py --compare .tmp/origineel.txt .tmp/herschreven.txt --json

# Reviewgrafiek - visualiseert Flesch-Douma, TTR en risicoscore:
python3 tools/generate_review_chart.py \
 --flesch <flesch_douma_score> \
 --ttr <ttr_score> \
 --patronen <aantal_gevonden_patronen> \
 --risico <laag|gemiddeld|hoog>
```

**Let op:** Gebruik ALTIJD het `score` veld uit de `humanizer_nl.py --json` output als waarde voor `--patronen`. Dit getal bevat alle penalties al (inclusief Flesch-Douma < 30). Tel NOOIT handmatig een Flesch-Douma penalty bij de score op.

Vergelijk intern de originele en herschreven tekst:

- [ ] Is de kernboodschap volledig bewaard?
- [ ] Is de lengte vergelijkbaar (tenzij inkorten gevraagd was)?
- [ ] Zijn alle AI-patronen verwijderd?
- [ ] Is de APA-opmaak correct?
- [ ] Is de toon consistent door de hele tekst?
- [ ] Zijn er geen nieuwe fouten geïntroduceerd?

---

## Stap 8: Aanbieden aan Gebruiker

- Bied **beide versies** aan: origineel + herschreven (tenzij de tekst erg lang is)
- Geef een korte toelichting van de belangrijkste wijzigingen
- Markeer grote inhoudelijke keuzes die je hebt gemaakt
- Benoem expliciet wat je **niet** hebt gewijzigd en waarom
- Als er [BRON NODIG]-markeringen zijn: noem dit prominent

**Word-export:**
```bash
python3 tools/md_to_docx.py \
  --input .tmp/herschreven.txt \
  --output .tmp/herschrijven/<titel>.docx
```
`md_to_docx.py` verwerkt de `![caption](pad)` placeholders die `docx_to_text.py` heeft geschreven en plaatst de afbeeldingen terug in het .docx bestand. Zorg dat `.tmp/images/` nog aanwezig is tijdens de export (opruimen pas in Stap 9d).

**Vereisten voor correcte .docx-generatie:**
- `# Inleiding` MOET aanwezig zijn in de markdown — `word_export.py` vervangt deze kop automatisch door de documenttitel (APA 7). Zonder `# Inleiding` wordt de introductiesectie niet herkend en belandt de tekst in de body.
- Afkortingenlijst: markdown-tabel (`| Afkorting | Definitie |`) OF bold+tab formaat (`**ABBR**\tDefinitie`) onder een heading met "Afkortingen". Beide worden herkend door `md_to_docx.py`.

**Titelpagina front matter — verplichte labelvelden:**
Gebruik in `.tmp/herschreven.txt` altijd gelabelde velden voor de titelpagina-metadata (platte tekst vóór de eerste `#` heading):
```
Hogeschool NOVI
Titel van het Rapport
Auteur Naam
Studentnummer: 12345
Opleiding: HBO-ICT
Vak: Systems Security
Begeleider: Naam Docent
Datum: 12 maart 2026
```
APA 7 volgorde (door `word_export.py` afgedwongen): Instelling → Titel (vet) → Auteur → Studentnummer → Opleiding → Vak → Begeleider → Datum.

---

## Subtypen Herschrijven

### Parafraseren (voor bronvermelding)
**Doel:** Originele formulering van een bron omschrijven in eigen woorden
- Behoud de betekenis volledig maar gebruik geen enkele zin of frase uit het origineel
- Voeg altijd `(Auteur, jaar)` toe na de parafrase (zie `apa_nl_gids.md` § 5)
- Controleer of de parafrase voldoende afwijkt van het origineel

### Humaniseren (AI-tekst menselijker maken)
**Doel:** AI-geschreven tekst omzetten naar menselijk klinkende tekst
- Gebruik `humanize_nl_gids.md` als primaire leidraad
- Vervang systematisch alle geïdentificeerde AI-woorden (Niveau 1 altijd, Niveau 2 bij hoge dichtheid)
- Pas zinslengtevariatie toe
- Voeg specifieke, concrete details toe waar de tekst te algemeen is

### Formaliseren (informele tekst academisch maken)
**Doel:** Schrijfstijl verhogen naar academisch niveau
- Verwijder spreektaal en Anglicismen
- Vervang "je/jij" door "men" of herformuleer
- Vervang informele woorden (bijv. "dingen", "best wel", "eigenlijk")
- Zorg voor overgangszinnen tussen alinea's

### Inkorten (tekst compacter maken)
**Doel:** Tekst korter maken zonder inhoudsverlies
- Verwijder herhaling van dezelfde gedachte
- Verwijder aanloopzinnen ("Het is interessant om op te merken dat...")
- Combineer alinea's die dezelfde gedachte bevatten
- Behoud alle inhoudelijke informatie - snij alleen het vet weg

---

## Stap 9: Verificatiechecklist [VERPLICHT]

Bevestig dat ALLE stappen zijn uitgevoerd voordat de tekst wordt aangeboden. Als een stap ontbreekt, ga terug en voer deze uit.

| Stap | Check | Herstelstap als NIET afgevinkt |
|------|-------|-------------------------------|
| 2 | Alle 5 gidsen gelezen (taal_gids, humanize_nl_gids, apa_nl_gids, academische_stijl_gids, schrijfstijl.md) | Lees de ontbrekende gids(en) alsnog - ga pas verder na lezing |
| 2 | grammar_check.py op origineel uitgevoerd | Voer grammar_check.py uit; rapporteer fout als API onbereikbaar is, sla stap niet stil over |
| 2 | humanizer_nl.py --suggest op origineel uitgevoerd | Voer tool uit; gebruik output als baseline voor de score-vergelijking in Stap 7 |
| 5 | apa_checker.py op herschreven tekst uitgevoerd | Voer tool uit; herstel kritieke bevindingen (z.d.-suffix, voornamen, paginanummers) voordat je doorgaat |
| 6 | humanizer_nl.py --suggest + readability_nl.py op herschreven tekst uitgevoerd | Voer beide tools uit; controleer of scores voldoen aan de acceptatiedrempels hierboven |
| 6 | tekst-analist subagent aangeroepen (of fallback tools bij falen) | Roep de subagent aan; bij timeout: gebruik de handmatige tool-output als fallback |
| 6 | humanize_nl_gids.md handmatig geraadpleegd (sectietype, burstiness, communicatievormen) | Lees de relevante categorieën (Cat. 3, 4, 9, 10, 11) alsnog en pas toe |
| 6 | Humanizer risicoscore ≤ 2 (Laag) | Herschrijf alinea's met de hoogste patronen; run humanizer opnieuw ter bevestiging |
| 7 | diff_viewer.py + humanizer --compare + generate_review_chart.py uitgevoerd | Voer de ontbrekende tools uit; genereer de reviewgrafiek voordat je aanbiedt |
| 8 | [BRON NODIG]-markeringen expliciet benoemd aan gebruiker | Noem elke [BRON NODIG] bij naam in de toelichting; student kan ze niet zelf zien als je ze verzwijgt |
| 9 | history_writer.py uitgevoerd | Voer history_writer.py uit - verplicht ook als gebruiker er niet om vraagt |
| 9 | md_to_docx.py uitgevoerd | Genereer .docx - verplicht ook als gebruiker er niet om vraagt |

---

## Randgevallen

| Situatie | Aanpak |
|----------|--------|
| Tekst is bijna volledig incorrect | Vraag of je opnieuw schrijft via `rapport_schrijven.md` |
| Gebruiker wil de betekenis wijzigen | Dit valt buiten herschrijven - gebruik `rapport_schrijven.md` |
| Tekst bevat claims zonder bron | Markeer met [BRON NODIG] en benoem aan gebruiker |
| Twee versies aangeleverd | Vraag welke versie leidend is voor het herschrijven |
| Feitelijke twijfel | Markeer de twijfelachtige claim, vraag gebruiker om verificatie - wijzig nooit feiten zelfstandig |
| Tekst is in het Engels | Vertaal en herschrijf in academisch Nederlands. Benoem dit aan de gebruiker voordat je begint. |

---

## Koppeling met Andere Workflows

- Eindcontrole na herschrijven: `rapport_reviewen.md`
- Nieuwe tekst schrijven: `rapport_schrijven.md`
- APA-details opzoeken: `apa_nl_gids.md`
- AI-patronen opzoeken: `humanize_nl_gids.md`
- Schrijfstijlregels opzoeken: `academische_stijl_gids.md`
- Taalregels opzoeken: `taal_gids.md`
- AI-tools citeren: `ai_gebruik_gids.md`

## Stap 10: History opslaan + .docx genereren [VERPLICHT]

Voer dit altijd uit na Stap 8, ook als de gebruiker er niet om vraagt.

**Stap 10a — Schrijf de herschreven output naar `.tmp/herschreven.txt`** (als dat nog niet gedaan is).

**Stap 10b — Sla op in geschiedenis:**
```bash
python3 tools/history_writer.py \
  --type herschrijven \
  --titel "<eerste 80 chars van de originele invoertekst of bestandsnaam>" \
  --metadata '{"doelen":["<doel1>","<doel2>"],"doelgroep":"<doelgroep>"}' \
  --output-file .tmp/herschreven.txt
```

**Stap 10c — Genereer .docx [VERPLICHT]:**
```bash
python3 tools/md_to_docx.py \
  --input .tmp/herschreven.txt \
  --output .tmp/herschrijven/<titel>.docx
```

**Sleutelwoorden:** Als het rapport een samenvatting bevat, voeg dan een regel `*Sleutelwoorden:* trefwoord1, trefwoord2, ...` toe na de samenvattingstekst. Dit wordt automatisch herkend door md_to_docx.py en correct gerenderd in de .docx.

**Stap 10d — Werkbestanden opruimen:**
Verwijder tussenbestanden uit `.tmp/` root die voor deze sessie zijn aangemaakt (bijv. `origineel.txt`, `herschreven.txt`, `bronnen.json`). Verwijder ook `.tmp/images/` als deze map tijdens de sessie is aangemaakt. Alleen het eindproduct in `.tmp/herschrijven/` blijft bewaard.

Meld daarna aan de gebruiker: "Opgeslagen in geschiedenis. Herschreven versie beschikbaar als `.tmp/herschrijven/<titel>.docx`"
