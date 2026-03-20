# Bijdragen aan DutchQuill AI

Bijdragen zijn welkom. Dit document legt uit hoe het project is opgebouwd en wat de spelregels zijn.

## Architectuur (WAT-framework)

DutchQuill AI werkt in drie lagen:

- **Workflows** (`workflows/`) — Markdown-SOP's die beschrijven wat er moet gebeuren en hoe. Dit zijn de instructies voor Claude.
- **Agent** — Claude leest de workflow, voert tools uit in de juiste volgorde en handelt fouten af.
- **Tools** (`tools/`) — Python-scripts die het rekenwerk doen: APA-checks, grammatica, AI-detectie, exports.

Claude Code laadt `CLAUDE.md` automatisch bij het openen van het project. Lees dit bestand voor de volledige architectuurbeschrijving.

## Ontwikkelomgeving opzetten

```bash
git clone https://github.com/nickyjacobs/DutchQuill-AI.git
cd DutchQuill-AI
pip install -r requirements.txt
```

Vereisten: Python 3.10+, Claude Code CLI met actief Pro- of Max-abonnement.

## Spelregels per bijdragegebied

### Tools (`tools/`)
- Volg het patroon: `argparse` met `--help` en `--input`
- Elke tool moet zelfstandig te testen zijn zonder API-aanroepen
- Controleer: `python3 tools/<tool>.py --help`

### Workflows (`workflows/`)
- Pas bestaande workflows niet aan zonder overleg — ze zijn zorgvuldig afgestemd
- Open een issue om wijzigingen te bespreken voordat je een PR indient

### Skills (`.claude/skills/`)
- Elke skill markeert verplichte tools als `[VERPLICHT]`
- Elke skill sluit af met een verificatiechecklist
- Exportconventies uit `CLAUDE.md` zijn altijd van kracht

### CLAUDE.md
- Niet wijzigen zonder overleg — dit zijn de kernafspraken van het systeem

## Commitconventie

Gebruik een korte Engelse onderwerpregel (imperatief, max 72 tekens):

```
fix: grammar_check.py crash on empty input
feat: add --compare flag to humanizer_nl.py
docs: update contributing guide
```

Een beschrijving in het Nederlands in de body mag.

## Pull request indienen

1. Fork de repo en maak een feature branch aan (`git checkout -b fix/naam-van-fix`)
2. Maak je wijzigingen en controleer alle betrokken tools met `--help`
3. Commit met een duidelijke boodschap
4. Open een PR — het PR-template helpt je de juiste informatie aan te leveren
5. Een review volgt zo snel mogelijk

## Vragen?

Gebruik [GitHub Discussions](https://github.com/nickyjacobs/DutchQuill-AI/discussions) voor vragen die geen bug of feature request zijn.
