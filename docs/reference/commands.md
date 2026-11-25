<p align="right"><b>🇬🇧 English</b> · <a href="../nl/naslag/commandos.md">🇳🇱 Dutch</a></p>

# Commands

## In Claude Code

The commands have Dutch names. Plain English works too: "write an email to ..." or "does this sound like AI?".

| Command | What it does |
|---|---|
| `/dutchquill:schrijven` (write) | A new text, from your question or the material in your workspace. Documents get an outline first. |
| `/dutchquill:herschrijven` (rewrite) | Improve, shorten, more formal or lighter, translate NL↔EN. Facts stay the same. |
| `/dutchquill:reviewen` (review) | Check without changing anything: language, structure, tone, AI patterns, and (when switched on) APA and your course rubric. |
| `/dutchquill:humaniseren` (humanize) | Remove AI patterns, in your own voice; or just scan. |
| `/dutchquill:instellen` (set up) | Workspace, profiles, checks, tone, templates and privacy, visually (Studio) or in the chat. |
| `/dutchquill:bijwerken` (update) | Check the reference guides against their sources and propose an update per guide. |

## Subagents

| Subagent | What it does |
|---|---|
| `bronnen-lezer` | Reads a lot of material at once and turns it into one summary, with key points, quotes with page numbers and a suggested place for every image. |
| `stem-analist` | Turns your texts in `my-style/` into a voice profile. |
| `tekst-analist` | Runs the analyses on a text (AI patterns, readability, before and after) and only returns the numbers. |

## `dq`: the toolbox

The skills call `dq`; you can use it yourself too. `dq <command> --help` shows the options.

| Command | What it does |
|---|---|
| `dq doctor` | Check the environment: Python, packages, workspace, how PDFs are made |
| `dq config toon` / `zet` / `valideer` / `profielen` | Show the merged config, set one setting, check the file, list profiles |
| `dq werkmap init` / `pad` / `status` | Create a workspace, show its path, show its state |
| `dq studio` | Start DutchQuill Studio |
| `dq materiaal inventaris` / `verzamel` | What is in `1-input/`, and what is new |
| `dq extraheer` | .docx, .pdf, .pptx, .xlsx, .csv and .html to text |
| `dq beeld` | Prepare images (orientation, metadata removed, HEIC to PNG) |
| `dq tells` | Measure AI patterns (`--compare` for before and after, `--json` for everything) |
| `dq feiten` | Fact check between the original and the new version |
| `dq leesbaarheid` | Flesch-Douma readability and sentence length |
| `dq stem` | Measure a voice profile from `my-style/` |
| `dq export` | Markdown to docx, pdf, html, md and txt, with a template |
| `dq template lijst` / `check` / `aanpas` | List Word templates, check them, make an adjusted copy |
| `dq versie volgende` / `laatste` / `lijst` | Version folders in `2-output/` |
| `dq historie toon` / `log` | Show or add to the history of your tasks; `log --tekst` keeps a copy of the text |
| `dq gids voor` / `pad` / `diff` / `schrijf` | Which guides belong to a task; compare and write an updated guide |
| `dq bronnen check` / `markeer` | Check the sources of the guides |
| `dq vak toon` / `lijst` | The submission requirements and rubric of a course, only the `## Rapportage` section |
| `dq apa-check`, `dq apa-bron` | APA checks and citations |
| `dq taalcheck` | LanguageTool, only when the online language check is on |
| `dq reviewgrafiek` | The overview image at the top of a review: AI patterns, readability, word variety, language round and the heaviest patterns |
| `dq diff`, `dq docx-tekst`, `dq grafiek`, `dq diagram` | Word diff, .docx to Markdown, charts and diagrams as PNG |

Outside Claude Code, `dq` is in the plugin folder (`scripts/dq`). On first use it creates its own Python environment
in the plugin's data folder.
