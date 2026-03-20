---
name: schrijven
description: Start de rapport_schrijven workflow. Gebruik dit wanneer de gebruiker nieuwe academische tekst wil schrijven (inleiding, methode, resultaten, discussie, conclusie of volledig rapport). Activeer proactief bij vragen als "schrijf een...", "maak een sectie over...", "stel een inleiding op...".
model: sonnet
---

Je voert de `rapport_schrijven.md` workflow uit. Volg onderstaande stappen in volgorde — sla GEEN stap over.

## Stap 0 — Gebruikersprofiel laden [OPTIONEEL]

Controleer of `config/user_profile.json` bestaat. Zo ja:
- Lees het bestand met de Read tool
- Gebruik de gegevens (naam, studentnummer, instelling, opleiding, docent, vak) als standaardwaarden voor de titelpagina-metadata
- Stel een bevestigingsvraag: "Ik gebruik de volgende gegevens uit je profiel: [overzicht]. Klopt dit voor dit rapport, of wil je iets aanpassen?"
- Als de gebruiker een specifiek vak of docent noemt, gebruik die in plaats van de standaard

Zo nee: ga gewoon door — het profiel is optioneel.

## Stap 1 — Invoer verzamelen

Vraag actief naar ontbrekende verplichte punten:

| Veld | Verplicht? |
|------|-----------|
| Onderwerp | Ja |
| Sectie (inleiding / methode / resultaten / discussie / conclusie / volledig) | Ja |
| Doelgroep (docent / opdrachtgever / examencommissie) | Ja |
| Opleidingsniveau (HBO bachelor / HBO master / MBO) | Ja |
| Woordenaantal | Nee — schat op basis van sectie |
| Beschikbare bronnen | Nee |
| Invalshoek of centrale vraag | Nee |
| Figuren (.jpg/.jpeg/.png) | Nee |

**Als de invoer een .docx bestand bevat, converteer dit ALTIJD eerst [VERPLICHT]:**
```bash
python3 tools/docx_to_text.py --input <pad naar .docx>
```

## Stap 2 — Plan maken + gidsen laden [VERPLICHT]

**Lees de volgende gidsen met de Read tool [VERPLICHT]:**
- `workflows/apa_nl_gids.md` — structuur van de gevraagde sectie
- `workflows/academische_stijl_gids.md` — werkwoordstijden, persoonlijke voornaamwoorden, naamwoordstijl
- `workflows/taal_gids.md` — d/t-regels, samenstellingen, signaalwoorden
- `workflows/humanize_nl_gids.md` — Niveau 1/2-woorden om te vermijden tijdens het schrijven

Stel intern een outline op: volgorde van gedachten, woordenaantal per subsectie, bronplaatsing.

## Stap 3 — Tekst schrijven

Principes:
- Begin met de kern — geen aanloopzinnen
- Concrete voorbeelden en specifieke informatie
- Geen aankondigingen ("In dit hoofdstuk wordt...")
- Elke alinea behandelt een gedachte
- Actieve constructies standaard

**Koppen en documentstructuur [ALTIJD van kracht]:**
- Gebruik GEEN nummers in kopnamen — schrijf `## Inleiding`, NOOIT `## 1. Inleiding`
- Dit geldt voor alle heading-niveaus (##, ###, ####)
- De md_to_docx.py tool strip nummers automatisch, maar in de markdown-bron staan ze nooit
- **Samenvatting:** bij een volledig rapport is een samenvatting (150-250 woorden) ALTIJD verplicht
  - Schrijf een `## Samenvatting` sectie direct na de documenttitel (vóór `## Inleiding`)
  - Sluit af met een `Sleutelwoorden:` regel: `Sleutelwoorden: term1, term2, term3`
- **Titelpagina-metadata:** zet naam, studentnummer, opleiding, instelling en datum als platte tekst VÓÓR de eerste markdown heading (`#`), niet als headings zelf
  - Correct format:
    ```
    Titel van het rapport
    Ondertitel (indien van toepassing)
    Naam Student
    Studentnummer: 123456
    Opleiding: Naam opleiding
    Naam Instelling
    Datum: 21 februari 2026

    # Documenttitel
    ```

## Stap 3b — Figuurverwerking [ALLEEN als figuren aangeleverd]

Voor elke afbeelding:
1. Analyseer de inhoud van de afbeelding
2. Bepaal plaatsingsplek in de tekst
3. Schrijf in-tekst verwijzing voor de figuur: "(zie Figuur X)"
4. Sla de afbeelding op in `.tmp/` als dat nog niet gedaan is
5. Schrijf APA-conforme caption: label vet direct onder figuur (`Figuur 1`), caption op volgende regel eindigend met punt
6. Noteer het pad voor de JSON-payload (Stap 8)

## Stap 4 — APA-integratie en taalcheck [VERPLICHT]

Verwerk bronvermelding tijdens het schrijven, niet achteraf. Gebruik `workflows/apa_nl_gids.md` sectie 5.
Ontbrekende bronnen markeren als `[BRON NODIG: onderbouwen dat X...]`.

**Voer deze tools uit na het schrijven [VERPLICHT]:**
```bash
python3 tools/grammar_check.py --input .tmp/tekst.txt
python3 tools/apa_checker.py --input .tmp/tekst.txt
```

**Bronformattering [ALLEEN als ruwe brondata beschikbaar is]:**
```bash
python3 tools/source_formatter.py --input .tmp/bronnen.json
```

Verwerk eventuele bevindingen in de tekst voordat je doorgaat naar Stap 5.

## Stap 5 — Humaniseringscheck [VERPLICHT]

Loop door elke alinea. Vervang alle Niveau 1-woorden. Verwijder formulaische structuren. Varieer zinslengte.

**Voer deze tools uit [VERPLICHT]:**
```bash
python3 tools/humanizer_nl.py --input .tmp/tekst.txt --suggest
python3 tools/readability_nl.py --input .tmp/tekst.txt
```

**Roep de `tekst-analist` subagent aan [VERPLICHT]:**
Geef `.tmp/tekst.txt` als input. De agent voert `humanizer_nl.py --json` en `readability_nl.py --json` uit en rapporteert risicoscore, top-3 patronen met alternatieven, Oxford comma, anglicismen, MATTR en Flesch-Douma.

**Fallback:** Als de tekst-analist geen output geeft, gebruik de handmatige tool-output hierboven.

**Volledige gids toepassen [VERPLICHT]:**
Na de tools en tekst-analist, raadpleeg `workflows/humanize_nl_gids.md` handmatig op:
- Sectietype-specifieke regels (Cat. 9): passief beoordelen per sectietype
- Burstiness (Cat. 3): kort-lang afwisseling bewust toepassen
- Leesbaarheid vs. humanisering (Cat. 11): Flesch-Douma mag niet verslechteren
- Communicatievormen (Cat. 4): geen helper-taal, geen retorische vragen
- Whitelist (Cat. 10): geflagde termen controleren op vakterm-legitimiteit

Risicobeoordeling:
- 0-2 patronen: laag — klein bijstellen
- 3-6 patronen: gemiddeld — herschrijf betreffende alinea's voor aanbieden
- 7+ patronen: hoog — herschrijf volledige tekst voor aanbieden

De tekst mag **niet** worden aangeboden bij gemiddeld of hoog risico.

## Stap 6 — Kwaliteitscheck [VERPLICHT]

**Genereer de reviewchart [VERPLICHT]:**
```bash
python3 tools/generate_review_chart.py --flesch <score> --ttr <score> --patronen <n> --risico <laag|gemiddeld|hoog>
```

Beantwoord intern:
- [ ] Centrale vraag beantwoord?
- [ ] APA correct toegepast?
- [ ] Geen Niveau 1-woorden?
- [ ] Zinslengte gevarieerd?
- [ ] Specifieke details (geen vage algemeenheden)?

## Stap 7 — Aanbieden

Bied de tekst aan met korte toelichting. Benoem gemaakte aannames en [BRON NODIG]-markeringen prominent.

## Stap 7b — Verificatiechecklist [VERPLICHT]

Bevestig intern dat ALLE stappen zijn uitgevoerd voordat je de tekst aanbiedt. Als een stap ontbreekt, ga terug en voer deze uit.

- [ ] Stap 2: Alle 4 gidsen gelezen met Read tool (apa_nl_gids, academische_stijl_gids, taal_gids, humanize_nl_gids)
- [ ] Stap 4: grammar_check.py en apa_checker.py uitgevoerd
- [ ] Stap 5: humanizer_nl.py en readability_nl.py uitgevoerd
- [ ] Stap 5: tekst-analist subagent aangeroepen (of fallback tools bij falen)
- [ ] Stap 5: humanize_nl_gids.md handmatig geraadpleegd (sectietype-regels, burstiness, communicatievormen)
- [ ] Stap 6: generate_review_chart.py uitgevoerd
- [ ] Tekst voldoet aan risicobeoordeling (laag of aangepast)

## Stap 8 — .docx export [ALLEEN als gebruiker payload-export wil]

Alleen na Stap 5 en 6. Stel JSON-payload samen conform het schema in `tools/word_export.py`. Figuren: gebruik `figure_placeholder` blok met `image_path`.

```bash
python3 tools/word_export.py --input .tmp/export_payload.json --output .tmp/<naam>.docx
```

## Stap 9 — History opslaan + .docx via md_to_docx.py [VERPLICHT]

Voer dit altijd uit na Stap 7, ook als de gebruiker er niet om vraagt.

**Stap 9a — Schrijf de volledige output naar .tmp/tekst.txt** (als dat nog niet gedaan is via Stap 8).

**Stap 9b — Sla op in geschiedenis:**
```bash
python3 tools/history_writer.py \
  --type schrijven \
  --titel "<sectienaam of eerste 80 chars van de instructie>" \
  --metadata '{"sectie":"<sectie>","niveau":"<niveau>","doelgroep":"<doelgroep>"}' \
  --output-file .tmp/tekst.txt
```

**Stap 9c — Genereer .docx [VERPLICHT als Stap 8 niet is uitgevoerd]:**
```bash
python3 tools/md_to_docx.py \
  --input .tmp/tekst.txt \
  --output .tmp/schrijven/<titel>.docx
```

**Stap 9d — Werkbestanden opruimen:**
Verwijder tussenbestanden uit `.tmp/` root die voor deze sessie zijn aangemaakt (bijv. `tekst.txt`, `bronnen.json`). Alleen het eindproduct in `.tmp/schrijven/` blijft bewaard.

Meld daarna aan de gebruiker: "Opgeslagen in geschiedenis. Tekst beschikbaar als `.tmp/schrijven/<titel>.docx`"
