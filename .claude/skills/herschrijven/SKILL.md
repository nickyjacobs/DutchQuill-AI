---
name: herschrijven
description: Start de rapport_herschrijven workflow. Gebruik dit wanneer de gebruiker bestaande tekst wil verbeteren, humaniseren, parafraseren, formaliseren of inkorten. Activeer proactief bij vragen als "verbeter deze tekst", "herschrijf...", "maak dit academischer", "parafraseer...".
model: sonnet
---

Je voert de `rapport_herschrijven.md` workflow uit. Volg onderstaande stappen in volgorde — sla GEEN stap over.

## Stap 0 — Gebruikersprofiel laden [OPTIONEEL]

Controleer of `config/user_profile.json` bestaat. Zo ja:
- Lees het bestand met de Read tool
- Gebruik de gegevens als context voor de herschrijving (bijv. instelling, opleiding, vak)
- Stel een bevestigingsvraag als de gegevens relevant zijn voor de titelpagina

Zo nee: ga gewoon door — het profiel is optioneel.

## Stap 1 — Invoer verzamelen

| Veld | Verplicht? |
|------|-----------|
| Originele tekst | Ja |
| Doel (verbeteren / parafraseren / humaniseren / APA-correctie / formaliseren / inkorten) | Ja |
| Intentie behouden? | Ja |
| Doelgroep | Nee |
| Specifieke instructies | Nee |

**Als de invoer een .docx bestand is, converteer dit ALTIJD eerst [VERPLICHT]:**
```bash
python3 tools/docx_to_text.py --input <pad naar .docx>
```
Sla het resultaat op als `.tmp/origineel.txt`.

## Stap 2 — Gidsen laden + tekst analyseren [VERPLICHT]

**Lees de volgende gidsen met de Read tool [VERPLICHT]:**
- `workflows/taal_gids.md` — taalfouten, afkortingen, samenstellingen, kommaregels
- `workflows/humanize_nl_gids.md` — AI-patronen, Niveau 1/2-woorden, formulaische openers
- `workflows/apa_nl_gids.md` — citaties, koppen, literatuurlijst
- `workflows/academische_stijl_gids.md` — schrijfstijl, registers, naamwoordstijl

**Voer analysetools uit op het origineel [VERPLICHT]:**
```bash
python3 tools/grammar_check.py --input .tmp/origineel.txt
python3 tools/humanizer_nl.py --input .tmp/origineel.txt --suggest
```

Loop systematisch door zes categorieen — gebruik de mini-checklists als minimum:

**Taalfouten** (op basis van `taal_gids.md`):
- [ ] Samenstellingen die los of met koppelteken staan maar aaneengeschreven moeten worden (`brute force aanval` → `brute-force-aanval`, `pen tester` → `pentester`)
- [ ] Trema's op ge-/be-/ver-werkwoorden (`geüpload`, `geïdentificeerd`, `geïnstalleerd`)
- [ ] D/T-fouten in werkwoorden (voltooid deelwoord, persoonsvorm)
- [ ] Afkortingen niet geïntroduceerd bij eerste gebruik (bijv. CTF, SSH, SUID)

**AI-patronen** (op basis van `humanize_nl_gids.md`):
- [ ] Niveau 1-woorden aanwezig? → run humanizer, lijst locaties op, vervang
- [ ] Formulaïsche opener? ("In de huidige samenleving...", "Het is belangrijk dat...", "Zoals eerder beschreven...")
- [ ] Lezeraanspraak of helper-taal? ("Denk aan...", "Je kunt je voorstellen...", "Kortom...")
- [ ] Uniform zinsritme? (vijf of meer zinnen van gelijke lengte op rij → wissel af)
- [ ] Passief overgebruikt voor dit sectietype? (zie `humanize_nl_gids.md` Cat. 9 voor drempelwaarden per sectietype)

**APA** (op basis van `apa_nl_gids.md`):
- [ ] Dezelfde auteur met 2+ bronnen en `z.d.` zonder letter-suffix? → moeten `z.d.-a`, `z.d.-b`, `z.d.-c` worden
- [ ] Voornamen in parenthetische of narratieve citaties? → alleen achternaam
- [ ] Directe citaten (tussen aanhalingstekens) zonder paginanummer? → voeg `p. X` toe
- [ ] Sectie heet "Bronnenlijst" of "Bibliografie"? → hernoem naar "Literatuurlijst"
- [ ] Claims zonder bron? → markeer `[BRON NODIG - <reden>]`

**Schrijfstijl** (op basis van `academische_stijl_gids.md`):
- [ ] Spreektaal of informele uitdrukkingen? (`best wel`, `eigenlijk`, `best sterk`, `zeg maar`)
- [ ] Naamwoordstijl? (`het uitvoeren van` → `uitvoeren`, `in het kader van` → weglaten)
- [ ] Persoonlijke voornaamwoorden in hoofdtekst? (`je`, `jij`, `we` — wel toegestaan in reflectiesectie)
- [ ] Em dashes (`—`)? → vervang door komma, punt of koppelteken met spaties (` - `)

**Structuur**:
- [ ] Herhaling van dezelfde gedachte binnen één alinea?
- [ ] Alinea behandelt meer dan één onderwerp?
- [ ] Ontbreekt een duidelijke topic sentence?
- [ ] Logische gaten tussen zinnen (redenering niet zichtbaar)?

**Figuren**:
- [ ] Label + caption APA-conform? (Figuur X. *Titel.* Noot. Bron: ...)
- [ ] In-tekst verwijzing vóór de figuur? ("zie Figuur X" moet altijd vóór de figuur staan)

## Stap 3 — Bepaal de aanpak

| Probleem | Aanpak |
|----------|--------|
| AI-patronen maar verder goed | Gerichte woord- en zinsvervangingen |
| Inhoudelijk sterk maar slecht geformuleerd | Herschrijven per alinea, behoud structuur |
| Verkeerde toon | Volledige herformulering |
| Feitelijke fouten | Markeer, vraag gebruiker — wijzig nooit feiten zelfstandig |
| Tekst bijna volledig incorrect | Vraag of nieuw schrijven via /schrijven beter is |

## Stap 4 — Herschrijf

Behoud altijd: kernboodschap, feitelijke informatie, correcte bronvermeldingen.
Verbeter altijd: zinsbouw, AI-woordkeuze, APA-opmaak, onnodig passief.

**Sleutelwoorden:** Als het rapport een samenvatting bevat, voeg dan een regel `*Sleutelwoorden:* trefwoord1, trefwoord2, ...` toe na de samenvattingstekst. Dit wordt automatisch herkend door md_to_docx.py en correct gerenderd in de .docx.

## Stap 5 — APA-check [VERPLICHT]

Controleer alle bronvermeldingen, directe citaten en koppen na herschrijven. Markeer [BRON NODIG] expliciet.

**Voer apa_checker.py uit [VERPLICHT]:**
```bash
python3 tools/apa_checker.py --input .tmp/herschreven.txt
```

**Bronformattering [ALLEEN als ruwe brondata beschikbaar is]:**
```bash
python3 tools/source_formatter.py --input .tmp/bronnen.json
```

## Stap 6 — Humaniseringscheck [VERPLICHT]

**Voer deze tools uit [VERPLICHT]:**
```bash
python3 tools/humanizer_nl.py --input .tmp/herschreven.txt --suggest
python3 tools/readability_nl.py --input .tmp/herschreven.txt
```

**Roep de `tekst-analist` subagent aan [VERPLICHT]:**
Geef `.tmp/herschreven.txt` als input. De agent voert `humanizer_nl.py --json` en `readability_nl.py --json` uit en rapporteert risicoscore, top-3 patronen met alternatieven, Oxford comma, anglicismen, MATTR en Flesch-Douma.

**Fallback:** Als de tekst-analist geen output geeft, gebruik de handmatige tool-output hierboven.

**Volledige gids toepassen [VERPLICHT]:**
Na de tools en tekst-analist, raadpleeg `workflows/humanize_nl_gids.md` handmatig op:
- Sectietype-specifieke regels (Cat. 9): passief beoordelen per sectietype
- Burstiness (Cat. 3): kort-lang afwisseling bewust toepassen
- Leesbaarheid vs. humanisering (Cat. 11): Flesch-Douma mag niet verslechteren
- Communicatievormen (Cat. 4): geen helper-taal, geen retorische vragen
- Whitelist (Cat. 10): geflagde termen controleren op vakterm-legitimiteit

Controleer op Niveau 1-woorden, formulaische structuren, zinslengtevariatie en nieuwe AI-patronen die eventueel geintroduceerd zijn.

## Stap 7 — Vergelijkingscheck [VERPLICHT]

**Voer deze tools uit [VERPLICHT]:**
```bash
python3 tools/diff_viewer.py --original .tmp/origineel.txt --rewritten .tmp/herschreven.txt
python3 tools/humanizer_nl.py --compare .tmp/origineel.txt .tmp/herschreven.txt --json
```

**Genereer de reviewchart [VERPLICHT]:**
```bash
python3 tools/generate_review_chart.py --flesch <score> --ttr <score> --patronen <n> --risico <laag|gemiddeld|hoog>
```

Intern checken: kernboodschap bewaard? Geen nieuwe fouten? APA correct? Toon consistent?

## Stap 8 — Aanbieden

Bied beide versies aan (origineel + herschreven). Geef korte toelichting van belangrijkste wijzigingen. Benoem wat je niet hebt gewijzigd en waarom.

## Stap 8b — Verificatiechecklist [VERPLICHT]

Bevestig intern dat ALLE stappen zijn uitgevoerd. Als een stap ontbreekt, ga terug en voer deze uit.

- [ ] Stap 2: Alle 4 gidsen gelezen met Read tool (taal_gids, humanize_nl_gids, apa_nl_gids, academische_stijl_gids)
- [ ] Stap 2: grammar_check.py + humanizer_nl.py op origineel uitgevoerd
- [ ] Stap 5: apa_checker.py op herschreven tekst uitgevoerd
- [ ] Stap 6: humanizer_nl.py + readability_nl.py op herschreven tekst uitgevoerd
- [ ] Stap 6: tekst-analist subagent aangeroepen (of fallback tools bij falen)
- [ ] Stap 6: humanize_nl_gids.md handmatig geraadpleegd (sectietype-regels, burstiness, communicatievormen)
- [ ] Stap 7: diff_viewer.py + humanizer compare + generate_review_chart.py uitgevoerd
- [ ] Risicobeoordeling laag of tekst aangepast

## Stap 9 — History opslaan + .docx genereren [VERPLICHT]

Voer dit altijd uit na Stap 8, ook als de gebruiker er niet om vraagt.

**Stap 9a — Schrijf de herschreven output naar .tmp/herschreven.txt** (als dat nog niet gedaan is).

**Stap 9b — Sla op in geschiedenis:**
```bash
python3 tools/history_writer.py \
  --type herschrijven \
  --titel "<eerste 80 chars van de originele invoertekst of bestandsnaam>" \
  --metadata '{"doelen":["<doel1>","<doel2>"],"doelgroep":"<doelgroep>"}' \
  --output-file .tmp/herschreven.txt
```

**Stap 9c — Genereer .docx [VERPLICHT]:**
```bash
python3 tools/md_to_docx.py \
  --input .tmp/herschreven.txt \
  --output .tmp/herschrijven/<titel>.docx
```

**Vereist formaat voor .tmp/herschreven.txt (kritiek voor correcte .docx-output):**

| Element | Vereiste opmaak | Fout bij afwijking |
|---------|-----------------|-------------------|
| Titelpagina-metadata | Platte tekst vóór eerste `#` heading | Metadata niet herkend |
| Datum | `Datum: 12 maart 2026` (gelabeld) of bare NL-datum `12 maart 2026` | Datum ontbreekt in docx |
| Vak | `Vak: Systems Security` (gelabeld met `Vak:`) | Vak wordt als ondertitel behandeld |
| Begeleider | `Begeleider: Naam Docent` (gelabeld met `Begeleider:`) | Begeleider wordt genegeerd |
| APA 7 titelpagina-volgorde | Titel (vet) → Auteur → Studentnummer → Instelling → Opleiding → Vak → Begeleider → Datum | Verkeerde volgorde op titelblad |
| Vetgedrukte tekst | `**tekst**` is toegestaan in bodytekst | Literal `**` in output |
| Inleiding-kop | `# Inleiding` MOET aanwezig zijn | Inleidingtekst belandt in body |
| Afkortingenlijst | Markdown-tabel: `\| Afkorting \| Definitie \|` | Alles samengeperst in één alinea |
| Figuren/afbeeldingen | `docx_to_text.py` extraheert afbeeldingen automatisch naar `.tmp/images/` en schrijft `![caption](pad)` placeholders. `md_to_docx.py` plaatst ze terug. Afbeeldingen blijven bewaard in de herschreven .docx. | Afbeeldingen ontbreken als `--no-images` gebruikt is |
| Bronnenlijst-kop | `# Literatuurlijst` (exact, of varianten: Bronnen, Referentielijst) | Bronnen niet herkend |

**Stap 9d — Werkbestanden opruimen:**
Verwijder tussenbestanden uit `.tmp/` root die voor deze sessie zijn aangemaakt (bijv. `origineel.txt`, `herschreven.txt`, `bronnen.json`). Verwijder ook `.tmp/images/` als deze map tijdens de sessie is aangemaakt. Alleen het eindproduct in `.tmp/herschrijven/` blijft bewaard.

Meld daarna aan de gebruiker: "Opgeslagen in geschiedenis. Herschreven versie beschikbaar als `.tmp/herschrijven/<titel>.docx`"
