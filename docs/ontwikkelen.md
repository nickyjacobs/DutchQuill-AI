# Ontwikkelen aan DutchQuill AI

## Opbouw

| Map | Inhoud |
|---|---|
| `.claude-plugin/` | `plugin.json` (versie, icoon, netwerkhosts) en `marketplace.json` |
| `skills/` | de zes skills (`/dutchquill:<naam>`) |
| `agents/` | `tekst-analist`, `bronnen-lezer`, `stem-analist` |
| `hooks/` | `sessie_start.py` (stdlib): eenmalig "nog niet ingesteld", en de maandmelding |
| `scripts/dq` | wrapper: venv in `${CLAUDE_PLUGIN_DATA}` (uv of pip), daarna `python -m dutchquill` |
| `scripts/dutchquill/` | het Python-pakket; `cli.py` kent alle commando's (`dq --help`) |
| `scripts/dutchquill/studio/` | DutchQuill Studio (server en statische pagina) |
| `config/` | `schema.json` (bron van waarheid), `profielen.yaml`, voorbeeldconfig |
| `gidsen/` | gidsen per module, `data/tells_*.yaml`, `bronnen.yaml`, `stand.json`, `werkwijze/` |
| `templates/` | `docx/` (gebouwd door `scripts/dev/bouw_templates.py`), `genres/`, `student/` |
| `evals/` | cases voor `claude plugin eval` |
| `tests/` | pytest |

## Afspraken

- Skills roepen scripts aan als `CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" ...`.
  De variabelen worden in de skilltekst vervangen, maar bestaan niet als omgevingsvariabele in Bash. In hooks wel.
- Nooit schrijven in de pluginmap: die wordt bij elke update vervangen.
- Een nieuwe instelling begint in `config/schema.json`, met `x-label` en `x-uitleg` in NL en EN. Draai daarna
  `scripts/dev/configuratie_doc.py`.
- Een nieuw AI-patroon gaat in `gidsen/data/tells_*.yaml` en in de gids, met een test in `tests/test_tells.py`.
- Geen klant-, werkgevers- of persoonsgegevens in de repository.

## Checks

```bash
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
uvx ruff check scripts hooks tests
claude plugin validate .
claude plugin eval . --runs 1 --model sonnet --allow-tools Bash --no-publish
```

Lokaal zonder plugin: `scripts/dq <commando>` gebruikt `.dev-data/` in de repo (gitignored). Een proefrun met de
plugin: `claude -p --plugin-dir . "/dutchquill:instellen ..."`. Die zet data in
`~/.claude/plugins/data/dutchquill-inline`; ruim die daarna op.

## Templates en documentatie opnieuw bouwen

```bash
uv run --no-project --with-requirements requirements.txt python scripts/dev/bouw_templates.py
uv run --no-project --with-requirements requirements.txt python scripts/dev/configuratie_doc.py
```

## Release

1. Versie ophogen in `.claude-plugin/plugin.json` en `scripts/dutchquill/__init__.py`; CHANGELOG bijwerken.
2. Checks en evals groen.
3. `develop` naar `main` via een pull request, daarna een tag `vX.Y.Z`.
