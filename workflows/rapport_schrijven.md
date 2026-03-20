# Workflow: Rapport Schrijven

## Doel
Stel een nieuw academisch rapport of sectie op in correct Nederlands, conform APA 7e editie,
met een menselijk klinkende schrijfstijl geschikt voor hogeschoolniveau.

## Wanneer gebruik je deze workflow?
- Je begint een rapport of sectie **vanaf nul**
- Er is nog geen bestaande tekst om op voort te bouwen
- De gebruiker vraagt om een eerste opzet of volledige tekst

Gebruik in plaats hiervan `rapport_herschrijven.md` als er al bestaande tekst is.

---

## Stap 1: Invoer Verzamelen

Verzamel de volgende informatie voordat je begint. Vraag actief naar ontbrekende verplichte punten.

**Word-bestand als invoer:** Als de gebruiker een `.docx` bestandspad opgeeft (bijv. als bestaande structuur of referentiedocument), lees de inhoud eerst uit:
```bash
python3 tools/docx_to_text.py --input <pad naar .docx>
```
De geëxtraheerde tekst is daarna beschikbaar als context voor het schrijven.

**Rapporten-map als invoer:** De map `rapporten/` bevat eerder aangeleverde rapportbestanden (.docx). Als de gebruiker verwijst naar een bestaand rapport zonder volledig pad, zoek in `rapporten/`. Converteer met `docx_to_text.py`.

| Invoer | Beschrijving | Verplicht? |
|--------|-------------|-----------|
| Onderwerp | Waar gaat het rapport over? | **Ja** |
| Sectie | Welk deel? (inleiding, methode, resultaten, discussie, conclusie, volledig rapport) | **Ja** |
| Doelgroep | Voor wie? (docent, opdrachtgever, examencommissie) | **Ja** |
| Opleidingsniveau | HBO bachelor / HBO master / MBO | **Ja** |
| Woordenaantal | Gewenst aantal woorden voor de sectie | Nee - schat op basis van sectie |
| Bronnen | Beschikbare bronnen om te verwerken | Nee |
| Invalshoek | Specifieke these, probleemstelling of centrale vraag | Nee |
| Bestaande structuur | Is er al een inhoudsopgave of outline? | Nee |
| Stijlvoorkeur | Formeel, semi-formeel, analytisch, beschrijvend | Nee - standaard: formeel academisch |
| Figuren | Screenshots of grafieken (.jpg, .jpeg, .png) om in de tekst op te nemen | Nee |

---

## Stap 2: Plan Maken

Voordat je schrijft:
1. Raadpleeg `apa_nl_gids.md` voor de vereiste structuur van de gevraagde sectie
2. Raadpleeg `academische_stijl_gids.md` voor schrijfstijlregels (werkwoordstijden, persoonlijke voornaamwoorden, naamwoordstijl, getallen)
3. Raadpleeg `taal_gids.md` voor taalregels (d/t, samenstellingen, signaalwoorden, verbindingswoorden)
4. Stel intern een outline op: wat komt er, in welke volgorde?
5. Bepaal het beoogde woordenaantal per subsectie
6. Noteer welke bronnen op welke plek worden verwerkt

---

## Stap 3: Tekst Schrijven

Schrijf de eerste versie met de volgende principes:

**Inhoud:**
- Begin met de kern - geen aanloopzinnen
- Gebruik concrete voorbeelden en specifieke informatie
- Vermijd aankondigingen: geen "In dit hoofdstuk wordt..." of "Hieronder volgt..."
- Sluit elke alinea af met een conclusie of brug naar de volgende gedachte

**Taal:**
- Schrijf in correct, formeel Nederlands
- Geen spreektaal, geen Anglicismen
- Actieve constructies zijn standaard - passief alleen als inhoudelijk sterker
- Elke alinea behandelt één gedachte
- Gebruik APA-koppen conform `apa_nl_gids.md`

**Structuurregels:**
- Geen opsommingen tenzij inhoudelijk noodzakelijk
- Geen koppen als er maar één subsectie is
- De tekst begint direct - geen kop "Inleiding" (zie APA-gids)

**Koppen [ALTIJD van kracht - nooit nummers in kopnamen]:**
- Schrijf `## Inleiding`, NOOIT `## 1. Inleiding`
- Dit geldt voor alle heading-niveaus
- De tool strip geen nummers als ze in de bronmarkdown staan → schrijf ze er dus nooit in

**Titelpagina-metadata [VERPLICHT formaat voor md_to_docx.py]:**
Zet naam, studentnummer, opleiding, instelling en datum als platte tekst VÓÓR de eerste markdown heading - nooit als headings zelf:
```
Rapporttitel
Ondertitel (indien van toepassing)
Naam Student
Studentnummer: 123456
Opleiding: Naam opleiding
Naam Instelling
Datum: 21 februari 2026

# Documenttitel (dit is de eerste heading)
```

**Samenvatting [VERPLICHT bij volledig rapport]:**
- Schrijf direct na de documenttitel: `## Samenvatting`
- Lengte: 150–250 woorden
- Sluit af met: `Sleutelwoorden: term1, term2, term3`
- md_to_docx.py herkent `## Samenvatting` automatisch en plaatst het als APA-abstract

---

## Stap 3b: Figuurverwerking (alleen indien figuren aangeleverd)

Voor elke aangeleverde afbeelding (.jpg, .jpeg of .png):

1. **Analyseer de afbeelding:** wat is de inhoudelijke boodschap? (Claude leest de afbeelding direct)
2. **Bepaal de plaatsingsplek:** na welke zin of alinea in de tekst past de figuur inhoudelijk het best?
3. **Schrijf een in-tekst verwijzing** vóór de figuur: "(zie Figuur X)" - de verwijzing moet altijd vóór de figuur staan
4. **Sla de afbeelding op** in `.tmp/` (bijv. `.tmp/figuur_1.jpg`) zodat word_export.py hem kan inladen
5. **Schrijf een APA-conforme caption** (zie `apa_nl_gids.md` § 10):
  - Label vet, direct onder de afbeelding: `Figuur 1`
  - Caption op de volgende regel, eindigt met een punt
  - Als de figuur van elders komt: bronvermelding als figuurvoetnoot: `Noot. Overgenomen van [Auteur] (jaar, p. X).`
6. **Noteer het bestandspad** voor de .docx export - vul `image_path` in de JSON-payload in (zie Stap 8)

---

### Specifieke sectiebegeleiding

**Voorwoord (indien gevraagd):**
- Persoonlijk van aard - eerste persoon enkelvoud is toegestaan
- Bedank betrokkenen (begeleider, opdrachtgever, medestudenten)
- Geen inhoudelijke vooruitblik - dat hoort in de inleiding
- Maximaal 1 pagina
- Geen bronvermeldingen nodig

**Reflectie (indien gevraagd):**
- Persoonlijk - eerste persoon enkelvoud
- Focus op het leerproces, niet op de rapportinhoud
- Structuur: wat ging goed, wat was moeilijk, wat zou je anders doen
- Geen bronvermeldingen nodig

**Methode (indien gevraagd):**
- Onderzoeksdesign (kwalitatief / kwantitatief / mixed methods)
- Steekproef of onderzoekspopulatie (wie, hoeveel, hoe geselecteerd)
- Dataverzameling (interviews, enquêtes, observaties, documenten)
- Data-analyse (codering, statistische methoden, software)
- Ethische overwegingen (informed consent, anonimiteit, AVG)
- Betrouwbaarheid en validiteit

**Begrippenlijst / Afkortingenlijst (indien gevraagd):**
- Alfabetische volgorde
- Afkorting of begrip links, definitie rechts
- Alleen termen die niet als algemeen bekend mogen worden beschouwd
- Plaats vóór de inleiding (na inhoudsopgave)

---

## Stap 4: [VERPLICHT] APA-Integratie

Dit stap mag niet worden overgeslagen of uitgesteld.

1. Verwerk bronvermelding **direct tijdens het schrijven**, niet achteraf
2. Gebruik `apa_nl_gids.md` § 5 voor het juiste format per auteurssituatie
3. Bij directe citaten: controleer pagina-/paragraafnummer (zie `apa_nl_gids.md` § 6)
4. Controleer na het schrijven of alle in-text citaties een overeenkomstige vermelding in de literatuurlijst krijgen
5. Controleer of koppen correct zijn opgemaakt (zie `apa_nl_gids.md` § 3)
6. Controleer paginaopmaak als het een volledig rapport betreft (zie `apa_nl_gids.md` § 4)

**Ontbrekende bronnen:**
Als de gebruiker geen bronnen heeft aangeleverd, schrijf de tekst zonder bronvermelding en markeer plaatsen waar een bron nodig is:
> [BRON NODIG: onderbouwen dat X...]

**Voer de volgende tools uit [VERPLICHT]:**
```bash
# Grammatica- en spellingcheck (LanguageTool):
python3 tools/grammar_check.py --input .tmp/tekst.txt

# APA-opmaakcheck - detecteert citatieopmaak, &-gebruik, paginanummers:
python3 tools/apa_checker.py --input .tmp/tekst.txt
```

**Bronformattering [ALLEEN als ruwe brondata beschikbaar is]:**
```bash
python3 tools/source_formatter.py --input .tmp/bronnen.json
```

---

## Stap 5: [VERPLICHT] Humaniseringscheck

Dit stap mag niet worden overgeslagen. Voer hem uit op de volledige tekst.

1. Loop door elke alinea en zoek naar Niveau 1-woorden uit `humanize_nl_gids.md` § Categorie 1 → vervang ze altijd
2. Controleer op formulaïsche structuren uit `humanize_nl_gids.md` § Categorie 2 → verwijder of herschrijf
3. Controleer zinslengtevariatie: zijn er vijf of meer opeenvolgende zinnen van gelijke lengte? → varieer
4. Controleer of alinea's telkens met hetzelfde woord beginnen → varieer
5. Controleer op vullingszinnen (`humanize_nl_gids.md` § Categorie 5) → verwijder

**Voer de volgende tools uit [VERPLICHT]:**
```bash
# Humanizer met alternatieven per gevonden patroon:
python3 tools/humanizer_nl.py --input .tmp/tekst.txt --suggest

# Leesbaarheidsindex (Flesch-Douma, gemiddelde zinslengte, lettergrepen):
python3 tools/readability_nl.py --input .tmp/tekst.txt
```

**Roep de `tekst-analist` subagent aan [VERPLICHT]:**
Geef `.tmp/tekst.txt` als input. De agent voert `humanizer_nl.py --json` en `readability_nl.py --json` uit en rapporteert risicoscore, top-3 patronen met alternatieven, Oxford comma, anglicismen, MATTR en Flesch-Douma in één overzicht.

**Fallback:** Als de tekst-analist geen output geeft, gebruik de handmatige tool-output hierboven.

**Volledige gids toepassen [VERPLICHT]:**
`humanize_nl_gids.md` bevat meer dan wat de tools detecteren. Controleer handmatig op:
- Sectietype-specifieke regels (Cat. 9): passief beoordelen per sectietype
- Burstiness (Cat. 3): kort-lang afwisseling bewust toepassen
- Leesbaarheid vs. humanisering (Cat. 11): Flesch-Douma mag niet verslechteren
- Communicatievormen (Cat. 4): geen helper-taal, geen retorische vragen, geen meta-commentaar
- Whitelist (Cat. 10): geflagde termen controleren op vakterm-legitimiteit
- N-gram repetitie (Cat. 3): herhalende woordcombinaties over de hele tekst
- Voor/na-voorbeeld (onderaan gids): gebruik als ijkpunt

**Risicobeoordeling:**
- 0–2 gevonden patronen: laag risico - klein bijstellen
- 3–6 gevonden patronen: gemiddeld risico - herschrijf de betreffende alinea's voor aanbieden
- 7+ gevonden patronen: hoog risico - herschrijf de volledige tekst voor aanbieden

De tekst mag **niet worden aangeboden bij gemiddeld of hoog risico** zonder eerst te herschrijven.

---

## Stap 6: Kwaliteitscheck

**Genereer de reviewchart [VERPLICHT]:**
```bash
python3 tools/generate_review_chart.py \
 --flesch <flesch_douma_score> \
 --ttr <ttr_score> \
 --patronen <aantal_gevonden_patronen> \
 --risico <laag|gemiddeld|hoog>
```

Beantwoord intern de volgende vragen voor je de tekst aanbiedt:

- [ ] Is de centrale vraag of these beantwoord?
- [ ] Zijn alle APA-regels correct toegepast?
- [ ] Zijn er geen Niveau 1 AI-patronen aanwezig?
- [ ] Is de zinslengte gevarieerd?
- [ ] Bevat de tekst specifieke details (geen vage algemeenheden)?
- [ ] Is het woordenaantal in lijn met de verwachting?
- [ ] Geen overmatig passief (actieve constructies waar mogelijk)?
- [ ] Niveau 2-woorden niet te dicht op elkaar?
- [ ] Alinea's beginnen niet telkens met hetzelfde woord?
- [ ] Tekst eindigt concreet (geen platitude)?

---

## Stap 7: Aanbieden aan Gebruiker

- Bied de tekst aan met een korte toelichting: wat is geschreven, welke keuzes zijn gemaakt
- Noem expliciet als je aannames hebt moeten maken (bijv. over bronnen of invalshoek)
- Als er [BRON NODIG]-markeringen zijn: benoem dit prominent
- Vraag of aanpassingen nodig zijn in toon, diepgang of structuur

---

## Stap 8: .docx Export

Exporteer het rapport als Word-bestand.

**Bewaker:** Voer deze stap alleen uit nadat Stap 5 (humaniseringscheck) en Stap 6 (kwaliteitscheck) zijn afgerond. Exporteer nooit een concept.

**Procedure:**

1. Schrijf de volledige output naar `.tmp/tekst.txt`
2. Genereer het .docx bestand:
   ```bash
   python3 tools/md_to_docx.py --input .tmp/tekst.txt --output .tmp/<rapportnaam>.docx
   ```
3. Deel het bestandspad met de gebruiker

**Geavanceerde export (alleen bij volledige rapporten met figuren of specifiek titelblad-data):**
Gebruik `tools/word_export.py` met JSON-payload voor volledige controle over titelblad, figuurplaatsing en sectiestructuur. Zie het JSON-schema in het script.

**Randgeval - tussentijdse export:** Als de gebruiker een Word-bestand wil van een nog niet volledig rapport, maak dan duidelijk dat de inhoudsopgave en bijlagen leeg of incompleet zijn. Exporteer alleen als de gebruiker dit bevestigt.

---

## Stap 9: Verificatiechecklist [VERPLICHT]

Bevestig dat ALLE stappen zijn uitgevoerd voordat de tekst wordt aangeboden. Als een stap ontbreekt, ga terug en voer deze uit.

- [ ] Stap 2: Alle 4 gidsen gelezen (apa_nl_gids, academische_stijl_gids, taal_gids, humanize_nl_gids)
- [ ] Stap 4: grammar_check.py en apa_checker.py uitgevoerd
- [ ] Stap 5: humanizer_nl.py --suggest en readability_nl.py uitgevoerd
- [ ] Stap 5: tekst-analist subagent aangeroepen (of fallback tools bij falen)
- [ ] Stap 5: humanize_nl_gids.md handmatig geraadpleegd (sectietype-regels, burstiness, communicatievormen)
- [ ] Stap 6: generate_review_chart.py uitgevoerd
- [ ] Risicobeoordeling laag, of tekst herschreven bij gemiddeld/hoog
- [ ] history_writer.py uitgevoerd
- [ ] md_to_docx.py uitgevoerd

---

## Randgevallen

| Situatie | Aanpak |
|----------|--------|
| Gebruiker geeft geen bronnen | Schrijf tekst, markeer bronplaatsen met [BRON NODIG] |
| Sectie is onduidelijk | Vraag eerst welke sectie bedoeld is |
| Tegenstrijdige instructies | Volg APA boven persoonlijke voorkeur - tenzij docent afwijkende instructies heeft gegeven |
| Volledig rapport gevraagd | Verdeel in meerdere stappen; schrijf en controleer per sectie |
| Woordenaantal onbekend | Gebruik als vuistregel: inleiding 10–15% van totaal, conclusie 10%, methode 20–25%, resultaten 25–30%, discussie 15–20% |

---

## Koppeling met Andere Workflows

- Na schrijven - eindcontrole: `rapport_reviewen.md`
- Bestaande tekst verbeteren: `rapport_herschrijven.md`
- APA-details opzoeken: `apa_nl_gids.md`
- AI-patronen opzoeken: `humanize_nl_gids.md`
- Schrijfstijlregels opzoeken: `academische_stijl_gids.md`
- Taalregels opzoeken: `taal_gids.md`
- AI-tools citeren: `ai_gebruik_gids.md`

## Opslaan in geschiedenis [VERPLICHT]

Na het voltooien van de output, sla het resultaat op in de webapp-geschiedenis:

```bash
python3 tools/history_writer.py \
 --type schrijven \
 --titel "<eerste 80 tekens van de gebruikersinvoer of hoofdvraag>" \
 --metadata '{"sectie":"<sectie>","niveau":"<niveau>","doelgroep":"<doelgroep>"}' \
 --output-file .tmp/tekst.txt
```
