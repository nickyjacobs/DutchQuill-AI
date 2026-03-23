# Agentinstructies

Je werkt binnen het **WAT-framework** (Workflows, Agents, Tools). Deze architectuur scheidt verantwoordelijkheden, zodat probabilistische AI het redeneren afhandelt en deterministische code de uitvoering verzorgt. Juist die scheiding maakt dit systeem betrouwbaar.

## De WAT-architectuur

**Laag 1: Workflows (de instructies)**
- Markdown-SOP’s opgeslagen in `workflows/`
- Elke workflow definieert het doel, de vereiste invoer, welke tools gebruikt moeten worden, de verwachte output en hoe randgevallen moeten worden afgehandeld
- Geschreven in gewone taal, op dezelfde manier waarop je iemand in je team zou briefen

**Laag 2: Agents (de beslisser)**
- Dit is jouw rol. Jij bent verantwoordelijk voor intelligente coördinatie.
- Lees de relevante workflow, voer tools in de juiste volgorde uit, handel fouten zorgvuldig af en stel verduidelijkende vragen wanneer dat nodig is
- Jij verbindt intentie met uitvoering zonder alles zelf te proberen doen
- Voorbeeld: Als je een rapport moet schrijven, probeer dat dan niet direct zelf. Lees `workflows/rapport_schrijven.md`, bepaal welke invoer nodig is en voer vervolgens de stappen uit met de juiste tools zoals `tools/humanizer_nl.py` en `tools/apa_checker.py`

**Laag 3: Tools (de uitvoering)**
- Python-scripts in `tools/` die het daadwerkelijke werk doen
- API-calls, datatransformaties, bestandsbewerkingen, databasequeries
- Eventuele omgevingsvariabelen worden opgeslagen in `.env`
- Deze scripts zijn consistent, testbaar en snel

**Waarom dit belangrijk is:** Wanneer AI elke stap direct zelf probeert af te handelen, neemt de nauwkeurigheid snel af. Als elke stap 90% nauwkeurig is, daalt je slagingskans na slechts vijf stappen al naar 59%. Door de uitvoering uit te besteden aan deterministische scripts, kun jij je blijven richten op orkestratie en besluitvorming - precies waar je in uitblinkt.

## Hoe je moet werken

**1. Kijk eerst of er al bestaande tools zijn**
Voordat je iets nieuws bouwt, controleer je `tools/` op basis van wat je workflow vereist. Maak alleen nieuwe scripts aan als er nog niets bestaat voor die taak.

**2. Leer en pas je aan wanneer dingen misgaan**
Wanneer je een fout tegenkomt:
- Lees de volledige foutmelding en stack trace
- Herstel het script en test opnieuw (als het betaalde API-calls of credits gebruikt, overleg dan eerst met mij voordat je het opnieuw uitvoert)
- Documenteer wat je hebt geleerd in de workflow (rate limits, timing-eigenaardigheden, onverwacht gedrag)
- Voorbeeld: Je loopt tegen een rate limit van een API aan, dus je duikt in de documentatie, ontdekt een batch-endpoint, past de tool aan zodat die daarvan gebruikmaakt, controleert of het werkt en werkt daarna de workflow bij zodat dit niet opnieuw gebeurt

**3. Houd workflows actueel**
Workflows moeten meegroeien met wat je leert. Wanneer je betere methoden vindt, beperkingen ontdekt of terugkerende problemen tegenkomt, werk je de workflow bij. Maak of overschrijf workflows echter niet zonder het te vragen, tenzij ik dat expliciet aangeef. Dit zijn jouw instructies en die moeten behouden en verfijnd worden, niet na één keer gebruik worden weggegooid.

## De zelfverbeteringslus

Elke fout is een kans om het systeem sterker te maken:
1. Bepaal wat er misging
2. Herstel de tool
3. Controleer of de oplossing werkt
4. Werk de workflow bij met de nieuwe aanpak
5. Ga verder met een robuuster systeem

Deze lus is hoe het framework in de loop van de tijd verbetert.

## Bestandsstructuur

**Wat hoort waar:**
- **Deliverables**: Eindproducten in de skill-submappen van `.tmp/` (schrijven/, herschrijven/, reviewen/, humaniseer/)
- **Tussenresultaten**: Tijdelijke werkbestanden in `.tmp/` root - worden na afloop opgeruimd

**Mappenstructuur:**
```text
config/         # Gebruikersconfiguratie: user_profile.json (optioneel, persoonlijke gegevens voor titelpagina)
.tmp/           # Tijdelijke bestanden + output-submappen per skill
  schrijven/    # .docx output van /schrijven
  herschrijven/ # .docx output van /herschrijven
  reviewen/     # .pdf output van /reviewen
  humaniseer/   # .pdf output van /humaniseer
tools/          # Python-scripts voor deterministische uitvoering (13 tools; humanizer_nl.py: 20 detectiecategorieën)
workflows/      # Markdown-SOP’s die definiëren wat er moet gebeuren en hoe (9 bestanden)
docs/           # Projectdocumentatie (configuratie, claude-code-setup, usage_kosten)
rapporten/      # Invoermap voor aangeleverde .docx bestanden
.claude/        # Claude Code configuratie: settings.json, skills/ (4), agents/, hooks/, rules/
.env            # Omgevingsvariabelen (optioneel, sla geheimen NOOIT ergens anders op)
```

## Bij het bouwen met Claude-features

Wanneer je iets bouwt of aanpast dat Claude-specifiek is (CLAUDE.md, hooks, subagents, skills, tools die Claude aanroepen, MCP, agent teams, settings), lees je altijd eerst `workflows/claude_bouwen.md` en fetch je de relevante documentatie voordat je begint.

## Projectcontext: DutchQuill AI

Dit project is een schrijfassistent voor Nederlandse academische rapporten (hogeschool, APA 7e editie).

**Workflow-routering:**
- Nieuwe tekst schrijven → `workflows/rapport_schrijven.md`
- Bestaande tekst verbeteren of herschrijven → `workflows/rapport_herschrijven.md`
- Rapport nakijken of reviewen → `workflows/rapport_reviewen.md`
- Snelle AI-detectiecheck zonder volledige workflow → `/humaniseer` skill

## Output- en exportconventies (altijd van kracht)

**CLI-skills - verplicht eindgedrag (nooit overslaan):**
- Elke skill slaat de output ALTIJD op in `.tmp/history.json` als laatste stap via `tools/history_writer.py`
- Schrijven + herschrijven: produceren een `.docx` bestand via `tools/md_to_docx.py`
- Humaniseer: produceert een `.pdf` analyserapport via `tools/generate_report_pdf.py`
- Reviewen: produceert een `.pdf` reviewrapport via `tools/generate_report_pdf.py` + korte samenvatting in de chat
- Na succesvolle output worden werkbestanden in `.tmp/` root opgeruimd

**Exportmatrix (altijd van kracht):**
| Skill | Bestandsoutput | Pad | Tool |
|-------|---------------|-----|------|
| schrijven | `.docx` | `.tmp/schrijven/<titel>.docx` | `md_to_docx.py` |
| herschrijven | `.docx` | `.tmp/herschrijven/<titel>.docx` | `md_to_docx.py` |
| humaniseer | `.pdf` | `.tmp/humaniseer/<titel>.pdf` | `generate_report_pdf.py` |
| reviewen | `.pdf` | `.tmp/reviewen/<titel>.pdf` | `generate_report_pdf.py` |

**history_writer.py aanroepen is even verplicht als de APA-check.** Doe het altijd, ook als de gebruiker er niet om vraagt.

**Markdown-structuur voor .docx export (altijd van kracht):**
- `# Inleiding` MOET altijd aanwezig zijn in de markdown. `word_export.py` vervangt deze kop automatisch door de documenttitel (APA 7). Zonder `# Inleiding` wordt de introductiesectie niet herkend en belandt de tekst in de body.
- Afkortingenlijst: markdown-tabel (`| Afkorting | Definitie |`) OF bold+tab formaat (`**ABBR**\tDefinitie`). Beide worden herkend door `md_to_docx.py`.

## Skill-uitvoering (altijd van kracht)

**Gidsen lezen is VERPLICHT:**
- Bij het uitvoeren van een skill: lees ALLE gidsen die in de SKILL.md worden genoemd met de Read tool
- "Raadpleeg" of "intern checken" is NIET voldoende - de gids moet daadwerkelijk gelezen worden
- Bij twijfel: lees de gids. Context window is geen excuus om een gids over te slaan.

**Tools draaien is VERPLICHT:**
- Elke tool die in de SKILL.md als [VERPLICHT] staat, MOET gedraaid worden via Bash
- Een tool die een fout geeft: rapporteer de fout in de output, maar sla de tool NIET over
- De verificatiechecklist aan het einde van elke skill bevestigt dat alle tools zijn uitgevoerd

**.docx invoer:**
- Als de gebruiker een .docx bestand aanlevert, converteer dit ALTIJD eerst: `python3 tools/docx_to_text.py --input <pad>`
- Sla het resultaat op in .tmp/ voordat je verdergaat met de workflow

**rapporten/ als invoerbron:**
- De map `rapporten/` is de invoermap voor .docx bestanden die de gebruiker wil laten verwerken
- Als de gebruiker verwijst naar een bestaand rapport zonder volledig pad, zoek in `rapporten/`
- Converteer altijd met `docx_to_text.py` voordat je verdergaat met de workflow

**Gebruikersprofiel (optioneel):**
- Als `config/user_profile.json` bestaat, gebruik de gegevens als standaardwaarden voor titelpagina-metadata
- Stel een bevestigingsvraag bij het gebruik van profielgegevens
- Het profiel is NOOIT verplicht - de skills werken volledig zonder

**Gidsen VOLLEDIG toepassen:**
- Na het uitvoeren van tools (humanizer_nl.py, readability_nl.py), raadpleeg de bijbehorende gids handmatig op onderdelen die de tools niet automatiseren
- `humanize_nl_gids.md` bevat meer dan de 20 detectiecategorieën: sectietype-specifieke regels, burstiness-advies, leesbaarheid-vs-humanisering tradeoff, communicatievormen, whitelist-uitzonderingen, n-gram repetitie, risicoscore drempelwaarden (0–2 laag / 3–6 gemiddeld / 7+ hoog)
- Alleen de script-output gebruiken is NIET voldoende - de volledige gids moet worden geraadpleegd

**tekst-analist subagent:**
- De tekst-analist is VERPLICHT bij elke workflow waar humaniseringsanalyse plaatsvindt (schrijven, herschrijven, reviewen, humaniseer)
- Fallback: als de tekst-analist geen output geeft, voer humanizer_nl.py en readability_nl.py handmatig uit

**Deliverables:** eindproducten in `.tmp/<skill>/` submappen. Reviewen toont ook een korte samenvatting in de chat.
**APA-kennis:** `workflows/apa_nl_gids.md` (bron: Scribbr NL, APA 7e editie)
**Humanisering:** `workflows/humanize_nl_gids.md` (bron: Humanizer-repo, aangepast voor NL)
**Academische stijl:** `workflows/academische_stijl_gids.md` (bron: Scribbr NL)
**Taalregels:** `workflows/taal_gids.md` (bron: Scribbr NL)
**AI-gebruik citeren:** `workflows/ai_gebruik_gids.md` (bron: Scribbr NL)

## Schrijfstijl bij het genereren van inhoud

Wanneer je Nederlandse rapporttekst schrijft, volg je altijd `.claude/rules/schrijfstijl.md`. Dat bestand bevat de volledige lijst verboden woorden (26), verboden openers (6) en schrijfregels. De stop-hook handhaaft deze regels automatisch na elke respons.