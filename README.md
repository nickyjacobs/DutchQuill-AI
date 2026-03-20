# DutchQuill AI

![DutchQuill AI](assets/DutchQuill-AI.png)

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

   INVOER             SKILL (Sonnet 4.6)             GIDSEN                          TOOLS + OUTPUT

 ┌──────────────┐   ┌──────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────────────┐
 │ Onderwerp    │   │ /schrijven               │   │ apa_nl_gids.md            │   │ grammar_check.py               │
 │ Invalshoek   │──▶│ rapport_schrijven.md     │──▶│ academische_stijl_gids.md │──▶│ apa_checker.py                 │
 │ Bronnen      │   │ [Stap 0–9]               │   │ taal_gids.md              │   │ humanizer_nl.py --suggest      │
 │ rapporten/   │   └──────────────────────────┘   │ humanize_nl_gids.md       │   │ readability_nl.py              │
 └──────────────┘                                  └───────────────────────────┘   │ tekst-analist + review chart   │
                                                                                   │ → .tmp/schrijven/<titel>.docx  │
                                                                                   └────────────────────────────────┘

 ┌──────────────┐   ┌──────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────────────┐
 │ Bestaande    │   │ /herschrijven            │   │ humanize_nl_gids.md       │   │ grammar_check.py               │
 │ tekst        │──▶│ rapport_herschrijven.md  │──▶│ apa_nl_gids.md            │──▶│ apa_checker.py                 │
 │ rapporten/   │   │ [Stap 0–9, 6 cat.]       │   │ taal_gids.md              │   │ humanizer_nl.py --suggest      │
 └──────────────┘   └──────────────────────────┘   │ academische_stijl_gids.md │   │ readability_nl.py              │
                                                   └───────────────────────────┘   │ diff_viewer.py + --compare     │
                                                                                   │ tekst-analist + review chart   │
                                                                                   │ → .tmp/herschrijven/<titel>.docx│
                                                                                   └────────────────────────────────┘

 ┌──────────────┐   ┌──────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────────────┐
 │ Afgerond     │   │ /reviewen                │   │ apa_nl_gids.md            │   │ grammar_check.py               │
 │ rapport      │──▶│ rapport_reviewen.md      │──▶│ humanize_nl_gids.md       │──▶│ apa_checker.py                 │
 │ rapporten/   │   │ [4 domeinen]             │   │ academische_stijl_gids.md │   │ humanizer_nl.py --suggest      │
 └──────────────┘   └──────────────────────────┘   │ taal_gids.md              │   │ readability_nl.py              │
                                                   └───────────────────────────┘   └────────────────┬───────────────┘
                                                                                                    │
                                                                                                    ▼
                                                                                   ┌────────────────────────────────┐
                                                                                   │ tekst-analist (Haiku 4.5)      │
                                                                                   │ review chart + report PDF      │
                                                                                   │ → samenvatting in chat         │
                                                                                   │ → .tmp/reviewen/<titel>.pdf    │
                                                                                   └────────────────────────────────┘

 ┌──────────────┐   ┌──────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────────────┐
 │ Geplakte     │   │ /humaniseer              │   │ humanize_nl_gids.md       │   │ humanizer_nl.py --suggest      │
 │ tekst        │──▶│ humaniseer/SKILL.md      │──▶│ (20 detectie-            │──▶│ readability_nl.py              │
 │              │   │ [snel, geen workflow]    │   │  categorieën)             │   │ tekst-analist agent            │
 └──────────────┘   │ Haiku 4.5                │   └───────────────────────────┘   │ review chart + report PDF      │
                    └──────────────────────────┘                                   │ → .tmp/humaniseer/<titel>.pdf  │
                                                                                   └────────────────────────────────┘

 ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
 Na elke response - Stop hook: check_verboden_woorden.py
 Verboden woord gevonden → exit 2 → Claude herformuleert automatisch
 ════════════════════════════════════════════════════════════════════════════════════════════════════════════════════
```

---

## Wat kan het?

- 4 skills: `/schrijven`, `/herschrijven`, `/reviewen`, `/humaniseer`
- Detecteert AI-patronen in 20 categorieën (typische woordkeuzes, Oxford comma, anglicismen, zinsritme)
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
git clone https://github.com/nickyjacobs/dutchquill-ai.git
cd dutchquill-ai
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

### `/schrijven` - Nieuwe academische tekst

| Stap | Actie | Tool |
|------|-------|------|
| 0 | Gebruikersprofiel laden (optioneel) | Read: `config/user_profile.json` |
| 1 | Invoer verzamelen (onderwerp, sectie, doelgroep, niveau) | Bij .docx: `docx_to_text.py` |
| 2 | 4 gidsen laden + outline opstellen | Read: `apa_nl_gids`, `academische_stijl_gids`, `taal_gids`, `humanize_nl_gids` |
| 3 | Tekst schrijven (APA-citaties inline) | - |
| 4 | Taal- en APA-check | `grammar_check.py` + `apa_checker.py` |
| 5 | Humaniseringscheck + risicobeoordeling | `humanizer_nl.py` + `readability_nl.py` + `tekst-analist` |
| 6 | Kwaliteitscheck + reviewchart | `generate_review_chart.py` |
| 7 | Tekst aanbieden + verificatiechecklist | - |
| 8 | (Optioneel) .docx export via payload | `word_export.py` |
| 9 | History + .docx genereren | `history_writer.py` + `md_to_docx.py` → `.tmp/schrijven/<titel>.docx` |

### `/herschrijven` - Bestaande tekst verbeteren

| Stap | Actie | Tool |
|------|-------|------|
| 0 | Gebruikersprofiel laden (optioneel) | Read: `config/user_profile.json` |
| 1 | Invoer + doel (humaniseren / formaliseren / APA / inkorten) | Bij .docx: `docx_to_text.py` |
| 2 | 4 gidsen laden + origineel analyseren (6 categorieën) | `grammar_check.py` + `humanizer_nl.py` op origineel |
| 3-4 | Aanpak bepalen + herschrijven | - |
| 5 | APA-check op herschreven versie | `apa_checker.py` |
| 6 | Humaniseringscheck herschreven versie | `humanizer_nl.py` + `readability_nl.py` + `tekst-analist` |
| 7 | Vergelijking origineel vs. herschreven | `diff_viewer.py` + `humanizer_nl.py --compare` + `generate_review_chart.py` |
| 8 | Beide versies aanbieden + verificatiechecklist | - |
| 9 | History + .docx genereren | `history_writer.py` + `md_to_docx.py` → `.tmp/herschrijven/<titel>.docx` |

### `/reviewen` - Rapport nakijken (4 domeinen)

| Stap | Actie | Tool |
|------|-------|------|
| 0 | Gebruikersprofiel + tekst voorbereiden | Bij .docx: `docx_to_text.py` |
| 1 | 4 gidsen laden | Read: alle 4 gidsen |
| D1 | Taalcorrectheid (d/t, samenstellingen, komma's) | `grammar_check.py` |
| D2 | APA 7 (citaties, koppen, literatuurlijst, figuren) | `apa_checker.py` |
| D3 | Humanisering (Niveau 1/2, anglicismen, zinsritme) | `tekst-analist` subagent (Haiku 4.5) |
| D4 | Structuur (macro / meso / micro) | Handmatig o.b.v. stijlgids |
| 5 | Reviewchart genereren | `generate_review_chart.py` |
| 6 | History + PDF genereren | `history_writer.py` + `generate_report_pdf.py` → `.tmp/reviewen/<titel>.pdf` |

> Output: korte samenvatting in de chat + volledig reviewrapport als PDF

### `/humaniseer` - Snelle AI-detectiecheck

| Stap | Actie | Tool |
|------|-------|------|
| 1 | Tekst ontvangen (< 100 woorden = waarschuwing) | - |
| 2 | Tekst opslaan + gids laden | Read: `humanize_nl_gids` |
| 3 | Analyse: risicoscore, patronen, anglicismen | `tekst-analist` subagent (Haiku 4.5) |
| 4 | Resultaten + aanbeveling (laag / gemiddeld / hoog) | `generate_review_chart.py` |
| 5 | History + PDF genereren | `history_writer.py` + `generate_report_pdf.py` → `.tmp/humaniseer/<titel>.pdf` |

---

## Alle Tools

| Tool | Functie | Aanroep |
|------|---------|---------|
| `humanizer_nl.py` | AI-patroondetectie (20 categorieën), risicoscore | `python3 tools/humanizer_nl.py --input <bestand> --suggest` |
| `readability_nl.py` | Flesch-Douma leesbaarheidsindex | `python3 tools/readability_nl.py --input <bestand>` |
| `apa_checker.py` | APA 7 validatie (citaties, literatuurlijst) | `python3 tools/apa_checker.py --input <bestand>` |
| `grammar_check.py` | Grammaticacheck via LanguageTool API | `python3 tools/grammar_check.py --input <bestand>` |
| `word_export.py` | APA 7-conforme .docx generatie | `python3 tools/word_export.py --input <payload.json>` |
| `md_to_docx.py` | Markdown/tekst → APA .docx conversie | `python3 tools/md_to_docx.py --input <bestand> --output <output.docx>` |
| `diff_viewer.py` | Woorddiff: origineel vs. herschreven | `python3 tools/diff_viewer.py --original <orig> --rewritten <nieuw>` |
| `source_formatter.py` | Ruwe brondata → APA 7-referentie | `python3 tools/source_formatter.py --input <bronnen.json>` |
| `docx_to_text.py` | Tekst extraheren uit .docx bestanden | `python3 tools/docx_to_text.py --input <bestand.docx>` |
| `generate_review_chart.py` | Visueel reviewdashboard (PNG) | `python3 tools/generate_review_chart.py --flesch <score> --ttr <score> --patronen <n> --risico <niveau>` |
| `generate_report_pdf.py` | PDF-analyserapport genereren | `python3 tools/generate_report_pdf.py --risico <niveau> --patronen <n> --flesch <score> --ttr <score> --output <bestand.pdf>` |
| `history_writer.py` | Verwerking opslaan in history.json | `python3 tools/history_writer.py --type <type> --titel <titel>` |
| `check_verboden_woorden.py` | Stop-hook: verboden AI-woorden detecteren | Automatisch na elke Claude-response |

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

Bijdragen zijn welkom. Een paar dingen om rekening mee te houden:

1. **Workflows:** pas bestaande workflows niet aan zonder overleg. Ze zijn zorgvuldig afgestemd.
2. **Tools:** nieuwe tools volgen het patroon `tools/<functie>.py` met `argparse` en `--help`.
3. **Skills:** elke skill markeert tools als `[VERPLICHT]` en sluit af met een verificatiechecklist.
4. **Testen:** draai `python3 tools/<tool>.py --help` om te controleren of het script correct laadt.

---

## Licentie

Dit project is gelicenseerd onder de [MIT License](LICENSE).
