# DutchQuill AI

![DutchQuill AI](assets/DutchQuill-AI.png)

![Dutch Quill AI](https://img.shields.io/badge/Dutch%20Quill%20AI-v1.0-brightgreen) ![Claude Code](https://img.shields.io/badge/Claude%20Code-required-blueviolet) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![JSON](https://img.shields.io/badge/config-JSON-lightgrey) ![Markdown](https://img.shields.io/badge/workflows-Markdown-lightgrey) ![APA 7](https://img.shields.io/badge/APA-7e%20editie-orange) ![AI Detectie](https://img.shields.io/badge/AI%20Detectie-20%20categorie%C3%ABn-red) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Schrijfassistent voor Nederlandse academische rapporten op HBO-niveau. Gebouwd op het WAT-framework (Workflows, Agent, Tools) en draait als CLI via [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

**Doelgroep:** HBO-studenten
**Schrijfstijl:** Formeel academisch Nederlands, APA 7e editie
**Licentie:** MIT

---

## Procesoverzicht

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                  DutchQuill AI                                                   │
│                                    WAT-framework (Workflows · Agent · Tools)                                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

       /schrijven               /herschrijven             /reviewen                /humaniseer
      (Sonnet 4.6)              (Sonnet 4.6)              (Sonnet 4.6)             (Haiku 4.5)

  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ INVOER           │    │ INVOER           │    │ INVOER           │    │ INVOER           │
  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤    ├──────────────────┤
  │ Onderwerp        │    │ Bestaande tekst  │    │ Afgerond rapport │    │ Geplakte tekst   │
  │ Invalshoek       │    │ rapporten/       │    │ rapporten/       │    │                  │
  │ Bronnen          │    │                  │    │                  │    │                  │
  │ rapporten/       │    │                  │    │                  │    │                  │
  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
           │                       │                        │                        │
           ▼                       ▼                        ▼                        ▼
  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ SKILL            │    │ SKILL            │    │ SKILL            │    │ SKILL            │
  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤    ├──────────────────┤
  │ /schrijven       │    │ /herschrijven    │    │ /reviewen        │    │ /humaniseer      │
  │ rapport_         │    │ rapport_         │    │ rapport_         │    │ humaniseer/      │
  │   schrijven.md   │    │   herschrijven   │    │   reviewen.md    │    │   SKILL.md       │
  │ [Stap 0–9]       │    │   .md            │    │ [4 domeinen]     │    │ [snel, geen      │
  │                  │    │ [Stap 0–9, 6c.]  │    │                  │    │  workflow]       │
  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
           │                       │                        │                        │
           ▼                       ▼                        ▼                        ▼
  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ GIDSEN           │    │ GIDSEN           │    │ GIDSEN           │    │ GIDSEN           │
  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤    ├──────────────────┤
  │ apa_nl_gids      │    │ humanize_nl_gids │    │ apa_nl_gids      │    │ humanize_nl_gids │
  │ academische_     │    │ apa_nl_gids      │    │ humanize_nl_gids │    │ (20 detectie-    │
  │   stijl_gids     │    │ taal_gids        │    │ academische_     │    │  categorieën)    │
  │ taal_gids        │    │ academische_     │    │   stijl_gids     │    │                  │
  │ humanize_nl_gids │    │   stijl_gids     │    │ taal_gids        │    │                  │
  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
           │                       │                        │                        │
           ▼                       ▼                        ▼                        ▼
  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
  │ TOOLS            │    │ TOOLS            │    │ TOOLS            │    │ TOOLS            │
  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤    ├──────────────────┤
  │ grammar_check    │    │ grammar_check    │    │ grammar_check    │    │ humanizer_nl     │
  │ apa_checker      │    │ apa_checker      │    │ apa_checker      │    │   --suggest      │
  │ humanizer_nl     │    │ humanizer_nl     │    │ humanizer_nl     │    │ readability_nl   │
  │   --suggest      │    │   --suggest      │    │   --suggest      │    │ tekst-analist    │
  │ readability_nl   │    │ readability_nl   │    │ readability_nl   │    │ review chart     │
  │ tekst-analist    │    │ diff_viewer      │    │ tekst-analist    │    │                  │
  │ review chart     │    │ tekst-analist    │    │   (Haiku 4.5)    │    │                  │
  │                  │    │ review chart     │    │ review chart     │    │                  │
  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
           │                       │                        │                        │
           ▼                       ▼                        ▼                        ▼
  .tmp/schrijven/        .tmp/herschrijven/       .tmp/reviewen/           .tmp/humaniseer/
  <titel>.docx           <titel>.docx             <titel>.pdf              <titel>.pdf

════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
Na elke response - Stop hook: check_verboden_woorden.py
Verboden woord gevonden → exit 2 → Claude herformuleert automatisch
════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## Wat kan het?

- 4 skills: `/schrijven`, `/herschrijven`, `/reviewen`, `/humaniseer`
- Detecteert AI-patronen in 20 categorieën (typische woordkeuzes, Oxford comma, anglicismen, zinsritme) — zie [docs/ai-detectie.md](docs/ai-detectie.md)
- Controleert APA 7e editie (citaties, koppen, literatuurlijst, figuren)
- Grammaticacheck via LanguageTool
- Leesbaarheid meten met de Flesch-Douma index
- Exporteert naar APA-conforme .docx met titelpagina
- Genereert een PDF-analyserapport met reviewchart
- Stop-hook die automatisch verboden AI-woorden onderschept
- Optioneel gebruikersprofiel zodat je naam, instelling en vak niet steeds opnieuw hoeft in te vullen

---

## Vereisten

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (CLI) met een actief Claude Pro- of Max-abonnement
- Python 3.10+

---

## Quick Start

### 1. Repository klonen

```bash
git clone https://github.com/nickyjacobs/DutchQuill-AI.git
cd DutchQuill-AI
```

### 2. Dependencies installeren

```bash
pip install -r requirements.txt
```

### 3. (Optioneel) Gebruikersprofiel instellen

Kopieer het voorbeeldprofiel en vul je gegevens in:

```bash
cp config/user_profile.example.json config/user_profile.json
```

Zie [Configuratie](docs/configuratie.md) voor alle velden.

### 4. Project openen in Claude Code

```bash
claude
```

Claude leest automatisch `CLAUDE.md` en laadt de skills, workflows en tools.

### 5. Een skill gebruiken

```
/schrijven          Schrijf een nieuwe rapportsectie
/herschrijven       Verbeter bestaande tekst
/reviewen           Laat een rapport nakijken
/humaniseer         Snelle AI-detectiecheck
```

---

## Configuratie

Het gebruikersprofiel (`config/user_profile.json`) is niet verplicht, maar scheelt je wel tijd. Wanneer het bestand bestaat, vult het systeem je naam, instelling en andere metadata automatisch in bij het aanmaken van titelpagina's.

```json
{
  "voornaam": "Jan",
  "tussenvoegsel": "van",
  "achternaam": "Dijk",
  "studentnummer": "900123456",
  "instelling": "Hogeschool Amsterdam",
  "faculteit": "Faculteit Techniek",
  "opleiding": "Software Engineering",
  "docenten": [{ "naam": "Dr. P. de Vries", "rol": "begeleider", "vak": "Afstuderen" }],
  "vakken": [{ "naam": "Onderzoeksmethoden", "code": "OZM301" }]
}
```

Het bestand staat in `.gitignore`, dus je persoonlijke gegevens worden nooit gecommit. Zie [docs/configuratie.md](docs/configuratie.md) voor meer toelichting.

---

## Skills

DutchQuill AI heeft vier skills. Je typt ze als slash-commando in Claude Code.

| Skill | Wanneer | Output |
|-------|---------|--------|
| `/schrijven` | Nieuwe rapporttekst schrijven | `.docx` in `.tmp/schrijven/` |
| `/herschrijven` | Bestaande tekst verbeteren (6 doelen) | `.docx` in `.tmp/herschrijven/` |
| `/reviewen` | Rapport nakijken op 4 domeinen | `.pdf` in `.tmp/reviewen/` |
| `/humaniseer` | Snelle AI-detectiecheck | `.pdf` in `.tmp/humaniseer/` |

Volledige uitleg per skill — invoer, opties, subtypes en output: [docs/skills.md](docs/skills.md)

---

## Alle Tools

12 Python-scripts in `tools/` plus één stop-hook in `.claude/hooks/`. Ze worden automatisch aangeroepen door de skills, maar je kunt ze ook los draaien via de terminal.

Volledige referentie met alle vlaggen, invoer- en uitvoerformaten en voorbeeldaanroepen: [docs/tools.md](docs/tools.md)

---

## Mappenstructuur

```
config/             Gebruikersconfiguratie
  user_profile.example.json   Voorbeeldprofiel (commit-safe)
  user_profile.json           Jouw profiel (gitignored)
workflows/          Markdown-workflows en referentiegidsen (9 bestanden)
tools/              Python-scripts voor deterministische uitvoering (12 tools)
docs/               Projectdocumentatie
rapporten/          Invoermap voor .docx bestanden
.claude/            Claude Code configuratie
  skills/           /schrijven · /herschrijven · /reviewen (Sonnet 4.6) · /humaniseer (Haiku 4.5)
  agents/           tekst-analist subagent (Haiku 4.5)
  hooks/            check_verboden_woorden.py (Stop hook)
  rules/            schrijfstijl.md (aanvullende schrijfregels)
  settings.json     Permissies voor alle tools + Write(.tmp/*)
.github/            GitHub-configuratie
  ISSUE_TEMPLATE/   Templates voor bugrapporten en feature requests
  PULL_REQUEST_TEMPLATE.md    Checklist voor pull requests
  workflows/        GitHub Actions CI (tool validation)
.tmp/               Tijdelijke werkbestanden
  schrijven/        Output van /schrijven (.docx)
  herschrijven/     Output van /herschrijven (.docx)
  reviewen/         Output van /reviewen (.pdf)
  humaniseer/       Output van /humaniseer (.pdf)
.env                Omgevingsvariabelen (optioneel, nooit committen)
```

---

## WAT-framework

**W**orkflows: Markdown-SOP's in `workflows/` die het proces en de kwaliteitseisen beschrijven.
**A**gent: Claude leest de workflow, voert de stappen uit en handelt fouten af.
**T**ools: Python-scripts in `tools/` die het rekenwerk doen.

Waarom die scheiding? Wanneer AI elke stap zelf uitvoert en elke stap 90% nauwkeurig is, zakt de slagingskans na vijf stappen al naar 59%. De scripts zijn deterministisch en dus 100% voorspelbaar. Claude kan zich daardoor richten op waar het goed in is: redeneren en beslissingen nemen.

```
   Gebruiker
       │
       ▼
   ┌───────┐     leest      ┌───────────┐
   │ Agent │ ◀──────────── │ Workflow  │
   └───┬───┘               └───────────┘
       │ voert uit
       ▼
   ┌───────┐     resultaat
   │ Tools │ ──────────────▶ Output
   └───────┘
```

Meer over de architectuur: zie `CLAUDE.md`.

---

## CLAUDE.md & Memory

DutchQuill AI leunt op twee ingebouwde mechanismen van Claude Code:

### CLAUDE.md

`CLAUDE.md` in de root vertelt Claude hoe het project werkt. Hier staan de WAT-architectuur, beschikbare workflows en tools, exportregels en schrijfstijlafspraken. Claude leest dit bestand vanzelf zodra je het project opent.

### Memory

Claude Code onthoudt dingen tussen sessies. Het leert na verloop van tijd je voorkeuren, terugkerende fouten en projectspecifieke patronen. Die memory-bestanden staan buiten de repository (in `~/.claude/`) en zijn persoonlijk per gebruiker, ze worden dus niet meegecommit.

Zie [docs/claude-code-setup.md](docs/claude-code-setup.md) voor meer toelichting.

---

## Referentiegidsen

| Gids | Inhoud | Bron |
|------|--------|------|
| `apa_nl_gids.md` | APA 7e editie, volledige referentie (18 secties) | Scribbr NL |
| `humanize_nl_gids.md` | AI-patroondetectie voor Nederlands (20 detectiecategorieën) | DutchQuill AI |
| `academische_stijl_gids.md` | Schrijfstijlregels: werkwoordstijden, registers, naamwoordstijl | Scribbr NL |
| `taal_gids.md` | Taalregels: d/t, samenstellingen, komma's, signaalwoorden | Scribbr NL |
| `ai_gebruik_gids.md` | AI-tools citeren in APA-format, transparantie-eisen | Scribbr NL |
| `claude_bouwen.md` | Instructies voor het bouwen van Claude-specifieke componenten | Claude Code Docs |

---

## Bijdragen

Bijdragen zijn welkom. Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor spelregels, de ontwikkelomgeving en hoe je een PR indient.

Kort samengevat:

1. **Workflows:** niet aanpassen zonder overleg. Ze zijn zorgvuldig afgestemd.
2. **Tools:** nieuwe tools volgen het patroon `tools/<functie>.py` met `argparse` en `--help`.
3. **Skills:** elke skill markeert tools als `[VERPLICHT]` en sluit af met een verificatiechecklist.
4. **Testen:** draai `python3 tools/<tool>.py --help` om te controleren of het script correct laadt.

Bugs melden of een feature voorstellen? Gebruik de [issue templates](https://github.com/nickyjacobs/DutchQuill-AI/issues/new/choose).

---

## Disclaimer

DutchQuill AI is in actieve ontwikkeling en wordt continu getest en verbeterd; de output kan fouten bevatten en is geen vervanging voor eigen controle.

---

## Licentie

Dit project is gelicenseerd onder de [MIT License](LICENSE).
