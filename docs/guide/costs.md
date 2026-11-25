<p align="right"><b>🇬🇧 English</b> · <a href="../nl/handleiding/kosten.md">🇳🇱 Dutch</a></p>

# Costs and models

DutchQuill itself is free and costs nothing per use. What it does cost is what Claude reads and writes: tokens. On
a Pro or Max subscription those count towards your usage limits; with an API key you pay per token
([Anthropic's prices](https://www.anthropic.com/pricing)). This page explains where the tokens go and how to keep
them down.

## Where the tokens go

| Part | Tokens | Why |
|---|---|---|
| The guides | most | Every task reads the working method and the guides for the checks that are on. That is deliberate: Claude follows the current rules, not what it remembers. |
| Your material | depends | Notes, sources and earlier versions that Claude reads. A lot of material goes through the subagent `bronnen-lezer`, which hands back one summary. |
| The text itself | the smallest part | Writing a mail costs little; a report of 5,000 words more, and every repair round reads it again. |
| The scripts (`dq`) | almost nothing | `dq tells`, `dq feiten`, the export and the other scripts run on your computer. Claude only reads their short output. |

An estimate from the size of the guides (about four characters per token): a mail or LinkedIn post reads roughly
15,000 to 20,000 tokens of guides, a report with APA and academic style roughly 30,000 to 40,000. On top of that
comes your material, the text and the repair rounds (at most three).

## Which model

- **The skills** (`schrijven`, `herschrijven`, `reviewen`, `humaniseren`, `instellen`, `bijwerken`) have no fixed
  model: they run on the model you chose in Claude Code (`/model`). Writing and humanizing need a good feel for
  language, so DutchQuill doesn't pick a smaller model for you. In v1 humanizing ran on Haiku; v2 leaves that
  choice to you.
- **The subagents** do have a fixed model, because their job is fixed:

  | Subagent | Model | Job |
  |---|---|---|
  | `tekst-analist` | Haiku | Runs the scripts and summarises their output |
  | `bronnen-lezer` | Sonnet | Reads a lot of material and turns it into one overview |
  | `stem-analist` | Sonnet | Reads your own texts and describes your voice |

## Keeping it down

- **Sonnet is enough** for almost everything. Use Opus for a long report or a difficult rewrite, if you have it.
- **Switch off what you don't need.** A check that is off (APA, academic style, humanizing) means a guide that
  isn't read. A profile per kind of text helps: `social` for posts reads no APA.
- **Chat instead of a file** for short texts: no export and no version folder.
- **Let the subagent read** when you have more than a few files of material; your main conversation then stays small.
- **Start a new conversation** for a new text. A long conversation carries everything from before.
- With an API key, `/cost` in Claude Code shows what a session cost.
