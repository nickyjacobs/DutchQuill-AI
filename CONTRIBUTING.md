# Bijdragen aan DutchQuill AI

Bijdragen zijn welkom: een nieuw AI-patroon, een genre-sjabloon, een fix in de export, een vertaling.

## Opzetten

```bash
git clone https://github.com/nickyjacobs/DutchQuill-AI.git
cd DutchQuill-AI
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
```

Testen in Claude Code zonder te installeren: `claude --plugin-dir .`. Opbouw, afspraken en releasestappen staan
in [docs/ontwikkelen.md](docs/ontwikkelen.md).

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

Open eerst een issue voor grotere wijzigingen. Een pull request gaat naar `develop`.
