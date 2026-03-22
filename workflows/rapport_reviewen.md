# Workflow: Rapport Reviewen

## Doel
Voer een volledige kwaliteitscontrole uit op een bestaand rapport of sectie. Beoordeel
Nederlandse taalcorrectheid, APA 7e editie compliance, humanisering van de schrijfstijl
en tekststructuur.

## Wanneer gebruik je deze workflow?
- De tekst is (bijna) af en moet nagekeken worden
- De gebruiker wil weten of het rapport klaar is voor inlevering
- Je wilt een gestructureerd feedbackrapport genereren
- Er is twijfel over APA-opmaak, taal of AI-detectierisico

---

## Stap 0: Gebruikersprofiel laden [OPTIONEEL]

Controleer of `config/user_profile.json` bestaat. Zo ja:
- Lees het bestand met de Read tool
- Gebruik de gegevens als context bij de review (bijv. instelling voor APA-titelpaginacheck)

Zo nee: ga gewoon door — het profiel is optioneel.

---

## Stap 1: Invoer Verzamelen

**Word-bestand als invoer:** Als de gebruiker een `.docx` bestandspad aanlevert in plaats van geplakte tekst, lees de inhoud eerst uit:
```bash
python3 tools/docx_to_text.py --input <pad naar .docx>
```
Gebruik de geëxtraheerde tekst als de te reviewen tekst en ga verder met de rest van de stap.

**Rapporten-map als invoer:** De map `rapporten/` bevat eerder aangeleverde rapportbestanden (.docx). Als de gebruiker verwijst naar een bestaand rapport zonder volledig pad, zoek in `rapporten/`. Converteer met `docx_to_text.py`.

| Invoer | Beschrijving | Verplicht? |
|--------|-------------|-----------|
| Te reviewen tekst | Het volledige rapport of de sectie | **Ja** |
| Type review | Volledig / alleen APA / alleen taal / alleen humanisering | Nee - standaard: volledig |
| Opleidingsniveau | HBO bachelor / HBO master / MBO | Nee |
| Specifieke zorgen | Wat wil de gebruiker extra goed nagekeken hebben? | Nee |

---

## De Vier Verplichte Reviewdomeinen

Alle vier domeinen zijn **verplicht** bij een volledige review. Bij een deelreview voer je alleen het gevraagde domein uit, maar noem je kort eventuele ernstige problemen in de andere domeinen.

**Lees de volgende gidsen met de Read tool [VERPLICHT]:**
1. `workflows/taal_gids.md` — voor Domein 1 (taalcorrectheid)
2. `workflows/apa_nl_gids.md` — voor Domein 2 (APA 7e editie)
3. `workflows/humanize_nl_gids.md` — voor Domein 3 (AI-patroondetectie)
4. `workflows/academische_stijl_gids.md` — voor Domein 2 + 4 (schrijfstijl, structuur)
5. `.claude/rules/schrijfstijl.md` — 28 verboden woorden en 6 verboden openers

---

## [VERPLICHT] Domein 1: Nederlandse Taalcorrectheid

*Raadpleeg `taal_gids.md` en `academische_stijl_gids.md` voor details bij elk punt.*

**Voer grammar_check.py uit [VERPLICHT]:**
```bash
python3 tools/grammar_check.py --input .tmp/tekst.txt
```
De tool detecteert spelling- en grammaticafouten via LanguageTool. Verifieer bevindingen altijd zelf.

### Grammatica
- [ ] Werkwoordsvervoeging correct (hij loopt, zij lopen, ik ben, ik heb)
- [ ] Lidwoordgebruik correct (de/het - twijfelgevallen: gebruik Van Dale of Groene Boekje)
- [ ] Zelfstandige naamwoorden correct gespeld (hoofdletters alleen bij eigennamen)
- [ ] Zinsconstructies compleet (geen losse bijzinnen zonder hoofdzin)
- [ ] Samenstellingen correct aaneengeschreven (arbeidsmarktbeleid, niet "arbeidsmarkt beleid")

### Interpunctie
- [ ] Kommaregels correct: bijzinnen, opsommingen, tussenzinnen
- [ ] Puntkomma's en dubbele punten correct gebruikt
- [ ] Geen komma voor "dat", "omdat", "doordat", "zodat" tenzij er een tussenzin is

### Woordkeuze
- [ ] Geen Anglicismen of directe Engelse vertalingen
- [ ] Geen spreektaal of informele uitdrukkingen ("best wel", "eigenlijk", "soort van")
- [ ] Vaktermen correct en consistent gebruikt
- [ ] Geen overbodige synoniemvervanging - één term voor één concept

### Consistentie
- [ ] Tijdsgebruik consistent door de tekst (verleden of tegenwoordige tijd, geen wisselen)
- [ ] Aanspreekvorm consistent ("men" / "de onderzoeker" - nooit "je/jij")
- [ ] Terminologie consistent (niet "onderzoek" hier en "studie" daar voor hetzelfde)

**Beoordeling:**
- Geen fouten: ✓ Taal correct
- 1–3 kleine fouten: Geef specifieke correcties per punt
- Structurele fouten: Adviseer herschrijven via `rapport_herschrijven.md`

---

## [VERPLICHT] Domein 2: APA 7e Editie Compliance

*Raadpleeg `apa_nl_gids.md` voor alle details bij elk punt.*

**Voer apa_checker.py uit [VERPLICHT]:**
```bash
python3 tools/apa_checker.py --input .tmp/tekst.txt
```
Verifieer bevindingen van de APA-checker altijd zelf.

**Bronformattering [ALLEEN als ruwe brondata beschikbaar is]:**
```bash
python3 tools/source_formatter.py --input .tmp/bronnen.json
```

### Titelpagina (indien aanwezig)
- [ ] Instellingsnaam aanwezig
- [ ] Rapporttitel aanwezig (vet, gecentreerd)
- [ ] Auteursnaam zonder titels
- [ ] Studentnummer aanwezig
- [ ] Opleiding/vak aanwezig
- [ ] Begeleider aanwezig
- [ ] Datum aanwezig (dag maand jaar)
- [ ] Geen running head (afgeschaft in APA 7)

### Structuur en Koppen
- [ ] Koppen volgen APA-hiërarchie (Level 1–3, correct opgemaakt)
- [ ] Inleiding begint met `# Inleiding` in markdown (word_export vervangt dit door de documenttitel)
- [ ] Minimaal twee koppen op elk niveau dat gebruikt wordt
- [ ] Geen nummering van koppen (tenzij instituut vereist)
- [ ] Inhoudsopgave aanwezig bij rapporten > 5 pagina's

### Opmaak
- [ ] Lettertype consistent (Times New Roman 12 / Arial 11 / Georgia 11)
- [ ] Dubbele regelafstand of conform institutionele richtlijn
- [ ] Marges 2,54 cm
- [ ] Eerste regel elke alinea ingesprongen (1,27 cm)
- [ ] Paginanummering rechtsbovenaan, doorlopend

### Samenvatting (indien aanwezig)
- [ ] Aparte pagina na titelpagina
- [ ] 150–250 woorden - tel het woordenaantal expliciet (korte samenvattingen zijn een veelgemaakte fout)
- [ ] Geen inspringing eerste regel
- [ ] Titel "Samenvatting" vet, gecentreerd
- [ ] Sleutelwoorden aanwezig (indien vereist)

### Bronvermelding in de Tekst
- [ ] Parafrasering: `(Auteur, jaar)` - na de zin, vóór de punt
- [ ] 1 auteur: `(Achternaam, jaar)` ✓
- [ ] 2 auteurs: `(Achternaam & Achternaam, jaar)` - & tussen haakjes, "en" in de tekst ✓
- [ ] 3+ auteurs: `(Eerste auteur et al., jaar)` ✓
- [ ] Directe citaten < 40 woorden: aanhalingstekens + `(Auteur, jaar, p. X)` ✓
- [ ] Directe citaten ≥ 40 woorden: blokcitaat zonder aanhalingstekens, bronvermelding ná de punt ✓
- [ ] Geen voornamen of titels bij in-text citations
- [ ] Meerdere bronnen: alfabetisch, gescheiden door puntkomma's

### Literatuurlijst
- [ ] Titel: "Literatuurlijst" of "Referentielijst" (niet "Bibliografie")
- [ ] Op aparte pagina, aan het einde (vóór bijlagen)
- [ ] Alfabetisch op achternaam eerste auteur
- [ ] Hanging indent aanwezig
- [ ] Alle in-text citaties hebben een overeenkomstige referentie
- [ ] Geen referenties zonder in-text citatie
- [ ] DOI aanwezig als hyperlink waar beschikbaar
- [ ] Titels van zelfstandige werken cursief, sentence case
- [ ] Geen locatie van uitgever (afgeschaft in APA 7)

### Tabellen (indien aanwezig)
- [ ] Nummer + titel **boven** de tabel (`Tabel 1`, vet; titel, cursief)
- [ ] Geen verticale lijnen
- [ ] Noot correct: *Noot.* (cursief) gevolgd door reguliere tekst
- [ ] In tekst benoemd vóór de tabel verschijnt

### Figuren (indien aanwezig)
- [ ] Label `Figuur X` staat **onder** de figuur (niet erboven), in vet
- [ ] Bijschrift staat direct na het label op de volgende regel, eindigt met een punt
- [ ] Figuur wordt in de tekst benoemd **vóór** de figuur verschijnt: "(zie Figuur X)"
- [ ] Nummering doorlopend en consistent door het rapport (Figuur 1, Figuur 2, ...)
- [ ] Als figuur van elders afkomstig: bronvermelding als figuurvoetnoot - `Noot. Overgenomen van [Auteur] (jaar, p. X).`
- [ ] Figuur is inhoudelijk relevant op de plek waar hij staat (context van de omringende tekst klopt)
- [ ] Bijschrift beschrijft wat de figuur toont - geen louter generieke titel ("Figuur resultaten")
- [ ] Figuur benoemd in de hoofdtekst (niet alleen in bijlage zonder verwijzing)

### Bijlagen (indien aanwezig)
- [ ] Na de literatuurlijst
- [ ] Elke bijlage op nieuwe pagina
- [ ] Titel vet, gecentreerd (`Bijlage A`)
- [ ] Elke bijlage minimaal één keer vermeld in de **hoofdtekst** van het rapport (niet alleen in de bijlage zelf) - zoek actief naar "(zie Bijlage X)" of vergelijkbare verwijzing

**Beoordeling:**
- Noteer per punt: ✓ correct / ✗ ontbreekt of incorrect + correctie conform `apa_nl_gids.md`

---

## [VERPLICHT] Domein 3: Humaniseringsbeoordeling

*Raadpleeg `humanize_nl_gids.md` voor de volledige lijsten.*

**Roep de `tekst-analist` subagent aan [VERPLICHT]:**
Geef `.tmp/tekst.txt` als input. De agent voert `humanizer_nl.py --json` en `readability_nl.py --json` uit en rapporteert risicoscore, top-3 patronen met alternatieven, Oxford comma, anglicismen, MATTR en Flesch-Douma in één overzicht.

**Fallback:** Als de tekst-analist geen output geeft, voer de tools handmatig uit:
```bash
python3 tools/humanizer_nl.py --input .tmp/tekst.txt --suggest
python3 tools/readability_nl.py --input .tmp/tekst.txt
```

**Volledige gids toepassen [VERPLICHT]:**
`humanize_nl_gids.md` bevat meer dan wat de tools detecteren. Controleer handmatig op:
- Sectietype-specifieke regels (Cat. 9): passief beoordelen per sectietype
- Burstiness (Cat. 3): kort-lang afwisseling bewust toepassen
- Leesbaarheid vs. humanisering (Cat. 11): Flesch-Douma mag niet verslechteren
- Communicatievormen (Cat. 4): geen helper-taal, geen retorische vragen, geen meta-commentaar
- Whitelist (Cat. 10): geflagde termen controleren op vakterm-legitimiteit
- N-gram repetitie (Cat. 3): herhalende woordcombinaties over de hele tekst
- Voor/na-voorbeeld (onderaan gids): gebruik als ijkpunt

Verifieer alle bevindingen zelf.

### Niveau 1-woorden (altijd vervangen)
- [ ] Geen woorden uit de Niveau 1-lijst aanwezig
- Gevonden: lijst elk gevonden woord op met zin + suggestie voor vervanging

### Niveau 2-woorden (bij hoge dichtheid)
- [ ] Geen Niveau 2-woorden die meer dan 1x per 500 woorden voorkomen
- Gevonden: benoem de dichtheid

### Niveau 3-woorden (context-afhankelijk)
- [ ] Geen Niveau 3-woorden (belangrijk, effectief, uniek, waardevol, opmerkelijk, substantieel) die meer dan 3% van de tekst uitmaken
- Gevonden: benoem het percentage en suggereer concretere alternatieven

### Passief-dichtheid
- [ ] Niet meer dan 40% passieve zinnen - herschrijf passief naar actief waar mogelijk
- `tools/humanizer_nl.py` rapporteert het percentage automatisch

### Connector-dichtheid
- [ ] Niet meer dan 30% van de zinnen begint met een connector (bovendien, tevens, daarnaast, etc.)

### Formulaïsche structuren
- [ ] Geen verboden openingszinnen (Type 1, 2, 3 uit `humanize_nl_gids.md` § Categorie 2)
- [ ] Geen vullingszinnen (`humanize_nl_gids.md` § Categorie 5)

### Statistische indicatoren
- [ ] Zinslengtevariatie aanwezig (geen vijf opeenvolgende zinnen van gelijke lengte)
- [ ] Alinea's beginnen niet telkens met hetzelfde woord
- [ ] Woordenschat gevarieerd (niet hetzelfde zelfstandig naamwoord > 2x per alinea)
- [ ] Geen em dashes (—) aanwezig - vervang door komma, punt of gedachtestreepje ( - )
- [ ] Geen vage bronvermeldingen zonder citatie ("Uit onderzoek blijkt dat...", "Experts stellen dat..." e.d.)
- [ ] TTR ≥ 0.45 (Type-Token Ratio: unieke woorden ÷ totaal; automatisch gedetecteerd door humanizer_nl.py)

### Inhoudelijke authenticiteit
- [ ] Tekst bevat specifieke details, geen louter vage algemeenheden
- [ ] Tekst klinkt als iemand met een eigen standpunt en kennis van zaken
- [ ] Geen inhoudloze opvulzinnen

**Risicoscore:**
- **Laag** (0–2 patronen): kleine bijstellingen volstaan
- **Gemiddeld** (3–6 patronen): adviseer herschrijven van betreffende alinea's via `rapport_herschrijven.md` (humaniseren)
- **Hoog** (7+ patronen): dringend herschrijven aanbevolen

---

## [VERPLICHT] Domein 4: Structuurcheck

### Macrostructuur (rapportniveau)
- [ ] Vereiste secties aanwezig voor het rapporttype
- [ ] Logische volgorde van secties
- [ ] Proportionele lengte per sectie (inleiding ≠ helft van rapport)
- [ ] Rode draad: centrale vraag/these is herkenbaar door het rapport heen
- [ ] Conclusie beantwoordt de centrale vraag

### Mesostructuur (alineaniveau)
- [ ] Elke alinea behandelt één gedachte
- [ ] Alinea's beginnen met een topic sentence
- [ ] Duidelijke overgangen tussen alinea's
- [ ] Alinea's niet te lang (vuistregel: max 150–200 woorden)

### Terminologieconsistentie
- [ ] Dezelfde term wordt door het hele rapport voor hetzelfde concept gebruikt
- [ ] Geen onverklaard wisselen tussen synoniemen voor hetzelfde begrip
- [ ] Afkortingen worden bij eerste gebruik voluit geschreven

### Microstructuur (zinsniveau)
- [ ] Geen losse zinnen die nergens bij horen
- [ ] Geen plotselinge onderwerpwisselingen binnen een alinea
- [ ] Geen herhaling van eerder gezegde zonder nieuwe informatie

---

## Feedbackformaat

Geef de review als gestructureerd rapport:

```
## Reviewrapport

**Datum:** [datum]
**Beoordeeld onderdeel:** [naam/sectie]

---

### 1. Taalcorrectheid
Status: Correct / Kleine aandachtspunten / Structurele fouten

[Specifieke bevindingen - citeer de zin uit de tekst + correctie]

---

### 2. APA Compliance
Status: Volledig correct / Aanpassingen nodig / Meerdere fouten

[Per APA-onderdeel: ✓ correct of ✗ fout + correctie]

---

### 3. Humanisering
Risicoscore: Laag / Gemiddeld / Hoog

[Gevonden patronen met voorbeeldzin + suggestie voor vervanging]

---

### 4. Structuur
Status: Sterk / Aandachtspunten / Herstructurering aanbevolen

[Bevindingen per structuurniveau]

---

### Eindoordeel
Klaar voor inlevering / Kleine aanpassingen nodig / Herschrijven aanbevolen

**Volgende stap:** [concrete actie]
```

---

## Verificatiechecklist [VERPLICHT]

Bevestig dat ALLE stappen zijn uitgevoerd voordat het reviewrapport wordt aangeboden. Als een stap ontbreekt, ga terug en voer deze uit.

- [ ] Tekst beschikbaar als .tmp/tekst.txt
- [ ] Alle 5 gidsen gelezen (taal_gids, apa_nl_gids, humanize_nl_gids, academische_stijl_gids, schrijfstijl.md)
- [ ] Domein 1: grammar_check.py uitgevoerd
- [ ] Domein 2: apa_checker.py uitgevoerd
- [ ] Domein 3: tekst-analist subagent aangeroepen (of fallback tools bij falen)
- [ ] Domein 3: humanize_nl_gids.md handmatig geraadpleegd (sectietype-regels, burstiness, communicatievormen)
- [ ] Domein 4: structuurcheck handmatig uitgevoerd
- [ ] generate_review_chart.py uitgevoerd
- [ ] history_writer.py uitgevoerd
- [ ] generate_report_pdf.py uitgevoerd → .tmp/reviewen/<titel>.pdf
- [ ] Werkbestanden opgeruimd

---

## Randgevallen

| Situatie | Aanpak |
|----------|--------|
| Tekst te lang voor één review | Review per sectie; vraag gebruiker welke sectie prioriteit heeft |
| Gebruiker wil alleen een score | Geef beknopt rapport: status per domein (✓/⚠/✗) + korte toelichting |
| Conflicterende APA-versies | Gebruik altijd APA 7e editie tenzij docent expliciet anders voorschrijft |
| Onzekerheid over vakspecifieke terminologie | Benoem de twijfel, vraag gebruiker om te verifiëren |
| Feitelijke fouten gevonden | Markeer en vraag om verificatie - wijzig nooit feiten zelfstandig |

---

## Koppeling met Andere Workflows

- Herschrijven na review: `rapport_herschrijven.md`
- Nieuwe secties toevoegen: `rapport_schrijven.md`
- APA-details opzoeken: `apa_nl_gids.md`
- AI-patronen opzoeken: `humanize_nl_gids.md`
- Schrijfstijlregels opzoeken: `academische_stijl_gids.md`
- Taalregels opzoeken: `taal_gids.md`
- AI-tools citeren: `ai_gebruik_gids.md`

## Opslaan in geschiedenis [VERPLICHT]

**Genereer de reviewchart [VERPLICHT]:**
```bash
python3 tools/generate_review_chart.py \
 --flesch <flesch_douma_score> \
 --ttr <ttr_score> \
 --patronen <aantal_patronen_gevonden> \
 --risico <laag|gemiddeld|hoog>
```

**Let op:** Gebruik ALTIJD het `score` veld uit de `humanizer_nl.py --json` output als waarde voor `--patronen`. Dit getal bevat alle penalties al (inclusief Flesch-Douma < 30). Tel NOOIT handmatig een Flesch-Douma penalty bij de score op.

Sla de base64-output op als `chartImage` in de metadata.

**Sla op in geschiedenis [VERPLICHT]:**
```bash
python3 tools/history_writer.py \
 --type reviewen \
 --titel "<eerste 80 tekens van de gereviewde tekst of bestandsnaam>" \
 --metadata '{"reviewType":"<type>","niveau":"<niveau>","chartImage":"<base64>"}' \
 --output-file .tmp/tekst.txt
```

**Genereer review-PDF [VERPLICHT]:**
```bash
python3 tools/generate_report_pdf.py \
 --risico <laag|gemiddeld|hoog> \
 --patronen <n> \
 --flesch <score> \
 --ttr <score> \
 --bestandsnaam "<bestandsnaam van het beoordeelde rapport>" \
 --niveau1 "<patroon1>|<alt1>||<patroon2>|<alt2>" \
 --waarschuwingen "<domein1 bevindingen>|<domein2 bevindingen>" \
 --aanbevelingen "<aanbeveling1>|<aanbeveling2>" \
 --chart-file .tmp/review_chart.b64 \
 --output .tmp/reviewen/<titel>.pdf
```

**Werkbestanden opruimen:**
Verwijder tussenbestanden uit `.tmp/` root (bijv. `tekst.txt`, `review_output.txt`, `review_chart.b64`). Alleen het eindproduct in `.tmp/reviewen/` blijft bewaard.
