<p align="right"><b>🇬🇧 English</b> · <a href="CONTRIBUTING.nl.md">🇳🇱 Dutch</a></p>

# Contributing to DutchQuill AI

Contributions are welcome, in English or Dutch: a new AI pattern, a genre template, an export fix, a translation.

## Setting up

```bash
git clone https://github.com/nickyjacobs/DutchQuill-AI.git
cd DutchQuill-AI
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
```

To test in Claude Code without installing: `claude --plugin-dir .`. Layout, conventions and release steps are in
[docs/project/development.md](docs/project/development.md).

## Ground rules

- **Tests:** every change in `scripts/` gets a test. `pytest` and `ruff check scripts hooks tests` must be green.
- **Settings** start in `config/schema.json`, with labels and explanations in Dutch and English.
- **AI patterns** go in `gidsen/data/tells_*.yaml` (strong or weak, with alternatives) plus the guide, with a
  source. Single words that are common in ordinary Dutch become weak.
- **Guides** contain their own wording with a source reference, not copied text.
- **No** customer, employer or personal data, and nothing meant to mislead detection or checks (such as fabricated
  metadata).
- **Commits:** `Add:`, `Fix:`, `Update:`, `Refactor:` or `Docs:` followed by a short sentence in the imperative.

## Issues and pull requests

Open an issue first for larger changes. A pull request goes to `develop`, with a line under `[Unreleased]` in the
CHANGELOG. How a release works: [docs/project/releasing.md](docs/project/releasing.md). How we treat each other:
[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

Working on the repo with an AI assistant? The rules for that assistant are in [AGENTS.md](AGENTS.md).
