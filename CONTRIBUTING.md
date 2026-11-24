# Bijdragen aan DutchQuill AI

Bijdragen zijn welkom: een nieuw AI-patroon, een genre-sjabloon, een fix in de export, een vertaling.

## Opzetten

```bash
git clone https://github.com/nickyjacobs/DutchQuill-AI.git
cd DutchQuill-AI
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
```

Testen in Claude Code zonder te installeren: `claude --plugin-dir .`. Opbouw, afspraken en releasestappen staan
in [docs/project/ontwikkelen.md](docs/nl/project/ontwikkelen.md).

## Spelregels

- **Tests:** elke wijziging in `scripts/` krijgt een test. `pytest` en `ruff check scripts hooks tests` moeten
  groen zijn.
- **Instellingen** beginnen in `config/schema.json`, met labels en uitleg in NL en EN.
- **AI-patronen** gaan in `gidsen/data/tells_*.yaml` (sterk of zwak, met alternatieven) plus de gids, met een
  bron. Losse woorden die in gewoon Nederlands veel voorkomen, worden zwak.
- **Gidsen** bevatten eigen formuleringen met een bronverwijzing, geen gekopieerde tekst.
- **Geen** klant-, werkgevers- of persoonsgegevens, en niets dat bedoeld is om detectie of controles te
  misleiden (zoals verzonnen metadata).
- **Commits:** `Add:`, `Fix:`, `Update:`, `Refactor:` of `Docs:` gevolgd door een korte zin in de gebiedende wijs.

## Issues en pull requests

Open eerst een issue voor grotere wijzigingen. Een pull request gaat naar `develop`, met een regel onder
`[Unreleased]` in de CHANGELOG. Hoe een release gaat: [docs/project/releasen.md](docs/nl/project/releasen.md). Hoe we met elkaar
omgaan: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Werk je met een AI-assistent aan de repo, dan staan de regels voor die assistent in [AGENTS.md](AGENTS.md).

## In English

Contributions are welcome, in English or Dutch: a new AI pattern, a template per kind of text, an export fix, a
translation. Open an issue first for larger changes; pull requests go to `develop` and add a line under
`[Unreleased]` in the CHANGELOG. Setup, layout and checks: [docs/project/development.md](docs/project/development.md).
Releases: [docs/project/releasing.md](docs/project/releasing.md).

