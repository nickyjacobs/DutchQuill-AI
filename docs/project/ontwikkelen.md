# Ontwikkelen aan DutchQuill

Deze repo is de Claude Code-plugin `dutchquill` en tegelijk zijn eigen marketplace (`marketplace.json` met
`source: "./"`). Alles in de repo gaat dus mee naar elke gebruiker; houd de repo daarom schoon en klein.

## Opbouw

| Map | Inhoud |
|---|---|
| `.claude-plugin/` | `plugin.json` (versie, icoon, netwerkhosts) en `marketplace.json` |
| `skills/` | de zes skills (`/dutchquill:<naam>`): schrijven, herschrijven, reviewen, humaniseren, instellen, bijwerken |
| `agents/` | `tekst-analist`, `bronnen-lezer`, `stem-analist` |
| `hooks/` | alleen SessionStart: `sessie_start.py` (stdlib) voor "nog niet ingesteld" en de maandmelding |
| `scripts/dq` | wrapper: venv in `${CLAUDE_PLUGIN_DATA}` (uv of pip); lichte commando's alleen met `requirements-basis.txt` |
| `scripts/dutchquill/` | het Python-pakket; `cli.py` kent alle commando's (`dq --help`) |
| `scripts/dutchquill/studio/` | DutchQuill Studio: stdlib-server en een statische pagina (vanilla JS en CSS, lokale fonts) |
| `scripts/dev/` | onderhoud: templates bouwen, configuratiedocs genereren, release-check |
| `config/` | `schema.json` (bron van waarheid voor config, Studio en skill), `profielen.yaml`, voorbeeldconfig |
| `gidsen/` | gidsen per module, `data/tells_*.yaml`, `bronnen.yaml`, `stand.json`, `werkwijze/` |
| `templates/` | `docx/` (gebouwd door `scripts/dev/bouw_templates.py`), `genres/`, `student/` |
| `evals/` | cases voor `claude plugin eval` |
| `tests/` | pytest |
| `docs/` | deze documentatie, in het Nederlands en in `docs/en/` in het Engels |

## Afspraken

- **Skills roepen scripts aan als** `CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" ...`.
  De variabelen worden in de skilltekst vervangen, maar bestaan niet als omgevingsvariabele in Bash. In hooks wel.
  Een `` !`cmd` `` in een skill werkt alleen aan het begin van een regel.
- **Nooit schrijven in de pluginmap:** die wordt bij elke update vervangen. Gebruikersdata staat in de werkmap,
  plugindata in `${CLAUDE_PLUGIN_DATA}`.
- **Een nieuwe instelling** begint in `config/schema.json`, met `x-label` en `x-uitleg` in NL en EN. Draai daarna
  `scripts/dev/configuratie_doc.py`; dat werkt de tabellen in de NL- en EN-docs bij.
- **Een nieuw AI-patroon** gaat in `gidsen/data/tells_*.yaml` en in de gids, met een bron en een test in
  `tests/test_tells.py`. Losse woorden die in gewoon Nederlands veel voorkomen, worden zwak.
- **Gidsen** bevatten eigen geformuleerde regels met een bronverwijzing, geen gekopieerde tekst.
- **Paden** die opgeslagen of getoond worden, schrijf je met `/` (`Path.as_posix()`), ook op Windows.
- **Humaniseren** is gericht op beter en eigen schrijven. Geen verzonnen metadata (bewerkingstijd, revisies,
  teruggedateerde tijdstempels), geen optimalisatie op detectorscores, geen "onzichtbaar"-claims.
- **Geen klant-, werkgevers- of persoonsgegevens** in de repository, ook niet in voorbeelden of tests.
- **Docs** bestaan in twee talen. Een wijziging in `docs/` hoort ook in `docs/en/`.

## Checks

```bash
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
uvx ruff check scripts hooks tests
uv run --script scripts/dev/release_check.py
claude plugin validate .
claude plugin eval . --runs 1 --model sonnet --allow-tools Bash --no-publish
```

De CI draait de tests en ruff op Linux, macOS en Windows, plus gitleaks en een linkcheck.

## Lokaal proberen

- **Zonder plugin:** `scripts/dq <commando>` gebruikt dan `.dev-data/` in de repo (gitignored).
- **Met de plugin, zonder te installeren:** `claude --plugin-dir .`. De data komt dan in
  `~/.claude/plugins/data/dutchquill-inline`; ruim die daarna op.
- **De Studio:** `scripts/dq studio`. Met `#s=<scherm>` en `#l=en` in de link open je een bepaald scherm of de
  Engelse versie.

## Templates en documentatie opnieuw bouwen

```bash
uv run --no-project --with-requirements requirements.txt python scripts/dev/bouw_templates.py
uv run --no-project --with-requirements requirements.txt python scripts/dev/configuratie_doc.py
```

## Release

Zie [releasen.md](releasen.md): branches, de opbouw van de CHANGELOG en de stappen tot en met de tag.
