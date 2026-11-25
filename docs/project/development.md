<p align="right"><b>🇬🇧 English</b> · <a href="../nl/project/ontwikkelen.md">🇳🇱 Dutch</a></p>

# Developing DutchQuill

This repo is the Claude Code plugin `dutchquill` and at the same time its own marketplace (`marketplace.json` with
`source: "./"`). Everything in the repo therefore ships to every user; keep the repo clean and small.

## Layout

| Folder | Contents |
|---|---|
| `.claude-plugin/` | `plugin.json` (version, icon, network hosts) and `marketplace.json` |
| `skills/` | the six skills (`/dutchquill:<name>`): schrijven, herschrijven, reviewen, humaniseren, instellen, bijwerken |
| `agents/` | `tekst-analist`, `bronnen-lezer`, `stem-analist` |
| `hooks/` | SessionStart only: `sessie_start.py` (stdlib) for "not set up yet" and the monthly reminder |
| `scripts/dq` | wrapper: venv in `${CLAUDE_PLUGIN_DATA}` (uv or pip); light commands only need `requirements-basis.txt` |
| `scripts/dutchquill/` | the Python package; `cli.py` knows every command (`dq --help`) |
| `scripts/dutchquill/studio/` | DutchQuill Studio: a stdlib server and a static page (vanilla JS and CSS, local fonts) |
| `scripts/dev/` | maintenance: build templates, generate the configuration docs, release check |
| `config/` | `schema.json` (source of truth for config, Studio and skill), `profielen.yaml`, example config |
| `gidsen/` | guides per module, `data/tells_*.yaml`, `bronnen.yaml`, `stand.json`, `werkwijze/` |
| `templates/` | `docx/` (built by `scripts/dev/bouw_templates.py`), `genres/`, `student/` |
| `evals/` | cases for `claude plugin eval` |
| `tests/` | pytest |
| `docs/` | this documentation, in English, and in Dutch in `docs/nl/` |

## Conventions

- **Skills call scripts as** `CLAUDE_PLUGIN_DATA="${CLAUDE_PLUGIN_DATA}" "${CLAUDE_PLUGIN_ROOT}/scripts/dq" ...`.
  The variables are substituted in the skill text, but don't exist as environment variables in Bash. In hooks they do.
  A `` !`cmd` `` in a skill only works at the start of a line.
- **Never write in the plugin folder:** it is replaced on every update. User data lives in the workspace, plugin data in
  `${CLAUDE_PLUGIN_DATA}`.
- **A new setting** starts in `config/schema.json`, with `x-label` and `x-uitleg` in NL and EN. Then run
  `scripts/dev/configuratie_doc.py`; it updates the tables in the NL and EN docs.
- **A new AI pattern** goes in `gidsen/data/tells_*.yaml` and in the guide, with a source and a test in
  `tests/test_tells.py`. Single words that are common in ordinary Dutch become weak tells.
- **Guides** contain rules in our own words with a reference, no copied text.
- **Paths** that are stored or shown use `/` (`Path.as_posix()`), on Windows too.
- **Humanizing** is about better, personal writing. No invented metadata (editing time, revisions, backdated
  timestamps), no optimising for detector scores, no "undetectable" claims.
- **No client, employer or personal data** in the repository, not in examples or tests either.
- **Docs** exist in two languages. A change in `docs/` also belongs in `docs/nl/`.
- The code, the guides and the skills are in Dutch; identifiers stay Dutch too.

## Checks

```bash
uv run --no-project --python 3.12 --with-requirements requirements.txt --with pytest pytest -q
uvx ruff check scripts hooks tests
uv run --script scripts/dev/release_check.py
claude plugin validate .
claude plugin eval . --runs 1 --model sonnet --allow-tools Bash --scaffold --no-publish
```

CI runs the tests and ruff on Linux, macOS and Windows, plus gitleaks and a link check.

**Evals in which `dq` really runs** (`tells-draait`, `review-met-rubric`, `humaniseren-feiten`, tag `dq`). In the
sandbox of `claude plugin eval` the plugin's data folder isn't writable and nothing can be installed. Those cases
therefore have a `scaffold.sh` that builds the Python environment in the run's workspace beforehand, outside the
sandbox (shared part: `evals/scaffold-dq.sh`), and set `EVAL_DQ_DATA: .dq-data` so `scripts/dq` uses it. The
scaffold needs a system Python 3.10+ outside your home folder (Homebrew, `/usr/local` or `/usr`), because the
sandbox can't read your home folder. Run with `--scaffold --allow-tools Bash`; with `--ablation none` you skip the
no-plugin arm, which says nothing for these cases. Without `--scaffold` they fail.

## Trying it locally

- **Without the plugin:** `scripts/dq <command>` then uses `.dev-data/` in the repo (gitignored).
- **With the plugin, without installing:** `claude --plugin-dir .`. Data then goes to
  `~/.claude/plugins/data/dutchquill-inline`; clean it up afterwards.
- **The Studio:** `scripts/dq studio`. With `#s=<screen>` and `#l=en` in the link you open a specific screen or the
  English version.

## Rebuilding templates and documentation

```bash
uv run --no-project --with-requirements requirements.txt python scripts/dev/bouw_templates.py
uv run --no-project --with-requirements requirements.txt python scripts/dev/configuratie_doc.py
```

## Releasing

See [releasing.md](releasing.md): branches, the CHANGELOG layout and the steps up to the tag.
