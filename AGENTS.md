# DutchQuill AI: instructies voor AI-assistenten

Dit bestand is voor AI-assistenten (Claude Code, Codex, Cursor en andere) die aan deze repository werken. Gebruikers
van de plugin krijgen het niet: een plugin laadt geen CLAUDE.md of AGENTS.md. Wat de plugin bij gebruikers doet,
staat in `skills/`.

**Lees eerst [docs/project/ontwikkelen.md](docs/nl/project/ontwikkelen.md):** de opbouw, de afspraken en de checks.
Releases: [docs/project/releasen.md](docs/nl/project/releasen.md).

## De regels die je niet mag missen

- Schrijf nooit in de pluginmap; gebruikersdata staat in de werkmap, plugindata in `${CLAUDE_PLUGIN_DATA}`.
- Een nieuwe instelling begint in `config/schema.json`, met labels in NL en EN.
- Elke wijziging in `scripts/` krijgt een test; `pytest` en `ruff check scripts hooks tests` moeten groen zijn.
- Docs bestaan in twee talen: Engels in `docs/`, Nederlands in `docs/nl/`. Wat in de ene taal verandert, verandert
  ook in de andere.
- Een gebruikerszichtbare wijziging krijgt een regel onder `[Unreleased]` in `CHANGELOG.md`.
- Geen klant-, werkgevers- of persoonsgegevens, ook niet in voorbeelden of tests.
- Geen verzonnen documentmetadata en niets dat bedoeld is om detectie of controles te misleiden.
- Commits: `Add:`, `Fix:`, `Update:`, `Refactor:` of `Docs:` plus een zin in de gebiedende wijs. Pull requests gaan
  naar `develop`.
