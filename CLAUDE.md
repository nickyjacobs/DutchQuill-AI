# DutchQuill AI: ontwikkelen aan de plugin

Dit is de repo van de Claude Code-plugin `dutchquill` (en tegelijk zijn eigen marketplace). Deze CLAUDE.md is
voor wie áán de plugin werkt; gebruikers krijgen hem niet (een plugin laadt geen CLAUDE.md). Wat de plugin bij
gebruikers doet, staat in de skills.

## Opbouw

```text
.claude-plugin/   plugin.json (versie, icoon, netwerkhosts) en marketplace.json (source: ./)
skills/           schrijven, herschrijven, reviewen, humaniseren, instellen, bijwerken  → /dutchquill:<naam>
agents/           subagents: tekst-analist, bronnen-lezer, stem-analist
hooks/            alleen SessionStart (sessie_start.py, stdlib): "nog niet ingesteld" en de maandmelding
scripts/dq        wrapper: venv in ${CLAUDE_PLUGIN_DATA}; lichte commando's alleen requirements-basis.txt
scripts/dutchquill/  Python-pakket; eigen commando's (config, werkmap, versie, historie, doctor) en tools
config/           schema.json (bron van waarheid voor config, Studio en skill), profielen.yaml, voorbeeldconfig
gidsen/           referentiegidsen met bronnen; stand.json = datum van de laatste controle
templates/        docx-templates, genre-sjablonen, studentvoorbeelden, visuals-stijlgids
tests/            pytest
```

## Regels

- **Skills roepen scripts aan met** `CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" ...`.
  De plugin-variabelen worden in de skilltekst vervangen, maar bestaan niet als omgevingsvariabele in Bash.
- **Nooit schrijven in de pluginmap.** Gebruikersdata staat in de werkmap, plugindata in `${CLAUDE_PLUGIN_DATA}`.
- **Nieuwe instelling:** eerst in `config/schema.json` (met `x-label` en `x-uitleg` in NL en EN), dan pas gebruiken.
- **Geen klantdata, geen werkgeverdata, geen persoonlijke gegevens** in deze publieke repo.
- **Humaniseren** is gericht op beter en eigen schrijven. Geen verzonnen metadata (bewerkingstijd, revisies,
  teruggedateerde tijdstempels), geen optimalisatie op detectorscores, geen "undetectable"-claims.

## Checks

```bash
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
uvx ruff check scripts hooks tests
claude plugin validate .
claude -p --plugin-dir . "/dutchquill:instellen ..."   # proefrun; data komt in ~/.claude/plugins/data/dutchquill-inline
```

Lokaal draaien zonder plugin: `scripts/dq <commando>` gebruikt dan `.dev-data/` in de repo (gitignored).

## Status v2

Roadmap: `docs/roadmap-v2.md`. Ontwikkelen: `docs/ontwikkelen.md`. Branch: `feature/plugin-v2`.
